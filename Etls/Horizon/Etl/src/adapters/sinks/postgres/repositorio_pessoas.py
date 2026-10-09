from datetime import datetime
from typing import Dict, Iterable, List, Optional

import psycopg

from src.core.logic.pii_anonymizer import anonymize_email
from src.core.ports.repositorio_pessoas import (
    FONTES_IDENTIFICADOR,
    NIVEIS_PROFICIENCIA,
    PessoaCadastrada,
    RepositorioPessoas,
)


class RepositorioPessoasPostgres(RepositorioPessoas):
    """Família pessoas sobre as tabelas de ModeloLogicoHorizon.sql.

    Recebe uma conexão aberta e não faz commit. Casos esperados (e-mail repetido,
    prêmio já gravado) são tratados sem erro de banco, porque no PostgreSQL um
    erro aborta a transação inteira de quem chama.

    Todo e-mail é gravado em hash (LGPD), como fazia o hook do ORM antigo.
    """

    def __init__(self, conexao: psycopg.Connection):
        self._conexao = conexao

    def listar(self) -> List[PessoaCadastrada]:
        with self._conexao.cursor() as cursor:
            cursor.execute("SELECT id, nome FROM pessoas ORDER BY id")
            pessoas: Dict[int, PessoaCadastrada] = {
                pessoa_id: PessoaCadastrada(id=pessoa_id, nome=nome)
                for pessoa_id, nome in cursor.fetchall()
            }

            cursor.execute("SELECT pessoa_id, email FROM emails_pessoa ORDER BY id")
            for pessoa_id, email in cursor.fetchall():
                pessoas[pessoa_id].emails.append(email)

            cursor.execute(
                "SELECT pessoa_id, fonte, codigo FROM identificadores_pessoa"
            )
            for pessoa_id, fonte, codigo in cursor.fetchall():
                pessoas[pessoa_id].identificadores[fonte] = codigo

        return list(pessoas.values())

    def criar(self, nome: str, emails: Iterable[str] = ()) -> int:
        if nome is None:
            raise ValueError("pessoa sem nome")

        with self._conexao.cursor() as cursor:
            cursor.execute(
                "INSERT INTO pessoas (nome) VALUES (%s) RETURNING id", (nome,)
            )
            pessoa_id = cursor.fetchone()[0]

        for email in emails:
            self.adicionar_email(pessoa_id, email)
        return pessoa_id

    def adicionar_email(self, pessoa_id: int, email: str) -> bool:
        email_hash = anonymize_email(email)
        if not email_hash:
            return False

        with self._conexao.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO emails_pessoa (pessoa_id, email) VALUES (%s, %s)
                ON CONFLICT (email) DO NOTHING
                RETURNING id
                """,
                (pessoa_id, email_hash),
            )
            return cursor.fetchone() is not None

    def definir_identificador(self, pessoa_id: int, fonte: str, codigo: str) -> None:
        if fonte not in FONTES_IDENTIFICADOR:
            raise ValueError(f"fonte de identificador inválida: {fonte!r}")
        if not codigo:
            raise ValueError("identificador sem código")

        with self._conexao.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO identificadores_pessoa (pessoa_id, fonte, codigo)
                VALUES (%s, %s, %s)
                ON CONFLICT (pessoa_id, fonte) DO UPDATE SET codigo = EXCLUDED.codigo
                """,
                (pessoa_id, fonte, codigo),
            )

    def buscar_por_identificador(self, fonte: str, codigo: str) -> Optional[int]:
        with self._conexao.cursor() as cursor:
            cursor.execute(
                """
                SELECT pessoa_id FROM identificadores_pessoa
                WHERE fonte = %s AND codigo = %s
                ORDER BY pessoa_id
                LIMIT 1
                """,
                (fonte, codigo),
            )
            linha = cursor.fetchone()
        return linha[0] if linha else None

    def salvar_perfil_lattes(
        self,
        pessoa_id: int,
        resumo: str,
        nomes_citacao: str,
        atualizado_em: datetime,
    ) -> None:
        if resumo is None or nomes_citacao is None or atualizado_em is None:
            raise ValueError("perfil Lattes exige resumo, nomes de citação e data")

        with self._conexao.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO perfis_lattes (pessoa_id, resumo, nomes_citacao, atualizado_em)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (pessoa_id) DO UPDATE SET
                    resumo = EXCLUDED.resumo,
                    nomes_citacao = EXCLUDED.nomes_citacao,
                    atualizado_em = EXCLUDED.atualizado_em
                """,
                (pessoa_id, resumo, nomes_citacao, atualizado_em),
            )

    def adicionar_premio(self, pessoa_id: int, titulo: str, ano: Optional[int]) -> bool:
        if not titulo:
            raise ValueError("prêmio sem título")

        with self._conexao.cursor() as cursor:
            cursor.execute(
                """
                SELECT 1 FROM premios
                WHERE pessoa_id = %s AND titulo = %s
                  AND ano IS NOT DISTINCT FROM %s::integer
                """,
                (pessoa_id, titulo, ano),
            )
            if cursor.fetchone():
                return False

            cursor.execute(
                "INSERT INTO premios (pessoa_id, titulo, ano) VALUES (%s, %s, %s)",
                (pessoa_id, titulo, ano),
            )
        return True

    def garantir_idioma(self, nome: str) -> int:
        if not nome:
            raise ValueError("idioma sem nome")

        with self._conexao.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO idiomas (nome) VALUES (%s)
                ON CONFLICT (nome) DO NOTHING
                RETURNING id
                """,
                (nome,),
            )
            linha = cursor.fetchone()
            if linha:
                return linha[0]

            cursor.execute("SELECT id FROM idiomas WHERE nome = %s", (nome,))
            return cursor.fetchone()[0]

    def definir_proficiencia(
        self,
        pessoa_id: int,
        idioma: str,
        leitura: str,
        escrita: str,
        fala: str,
        compreensao: str,
    ) -> bool:
        for nivel in (leitura, escrita, fala, compreensao):
            if nivel not in NIVEIS_PROFICIENCIA:
                raise ValueError(f"nível de proficiência inválido: {nivel!r}")

        idioma_id = self.garantir_idioma(idioma)
        with self._conexao.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO proficiencias
                    (pessoa_id, idioma_id, leitura, escrita, fala, compreensao)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (pessoa_id, idioma_id) DO NOTHING
                RETURNING pessoa_id
                """,
                (pessoa_id, idioma_id, leitura, escrita, fala, compreensao),
            )
            return cursor.fetchone() is not None
