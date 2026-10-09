from datetime import date
from typing import Optional

import psycopg

from src.core.logic.initiative_identity import normalize_text
from src.core.ports.repositorio_organizacoes import (
    ESCOPOS_PAPEL,
    PAPEIS_FIXOS,
    TIPOS_ORGANIZACAO,
    RepositorioOrganizacoes,
)


class RepositorioOrganizacoesPostgres(RepositorioOrganizacoes):
    """Organizações, unidades, papéis e vínculos sobre ModeloLogicoHorizon.sql.

    Recebe uma conexão aberta e não faz commit. Nomes são comparados com
    ``normalize_text`` (sem acento, caixa ou pontuação), como no ETL antigo.
    Não há cache: as tabelas são pequenas e um cache ficaria inválido após um
    rollback de quem chama.
    """

    def __init__(self, conexao: psycopg.Connection):
        self._conexao = conexao

    def ifes_id(self) -> int:
        with self._conexao.cursor() as cursor:
            cursor.execute(
                """
                SELECT id FROM organizacoes
                WHERE sigla = 'IFES' AND tipo = 'instituicao_ensino'
                ORDER BY id
                LIMIT 1
                """
            )
            linha = cursor.fetchone()
        if not linha:
            raise RuntimeError(
                "IFES não encontrado; recrie o schema com make horizon-db-schema."
            )
        return linha[0]

    def garantir_organizacao(
        self, nome: str, tipo: str, sigla: Optional[str] = None
    ) -> int:
        if tipo not in TIPOS_ORGANIZACAO or tipo == "unidade":
            raise ValueError(f"tipo de organização inválido: {tipo!r}")
        if not nome:
            raise ValueError("organização sem nome")

        alvo_nome = normalize_text(nome)
        alvo_sigla = normalize_text(sigla)
        with self._conexao.cursor() as cursor:
            cursor.execute(
                "SELECT id, nome, sigla FROM organizacoes "
                "WHERE tipo <> 'unidade' ORDER BY id"
            )
            for org_id, org_nome, org_sigla in cursor.fetchall():
                if normalize_text(org_nome) == alvo_nome or (
                    alvo_sigla and normalize_text(org_sigla) == alvo_sigla
                ):
                    return org_id

            cursor.execute(
                "INSERT INTO organizacoes (nome, sigla, tipo) "
                "VALUES (%s, %s, %s) RETURNING id",
                (nome, sigla, tipo),
            )
            return cursor.fetchone()[0]

    def garantir_unidade(self, nome: str, organizacao_pai_id: int) -> int:
        if not nome:
            raise ValueError("unidade sem nome")

        alvo = normalize_text(nome)
        with self._conexao.cursor() as cursor:
            cursor.execute(
                """
                SELECT o.id, o.nome
                FROM organizacoes o
                JOIN unidades_organizacionais u ON u.id = o.id
                WHERE u.organizacao_pai_id = %s
                ORDER BY o.id
                """,
                (organizacao_pai_id,),
            )
            for unidade_id, unidade_nome in cursor.fetchall():
                if normalize_text(unidade_nome) == alvo:
                    return unidade_id

            cursor.execute(
                "INSERT INTO organizacoes (nome, tipo) "
                "VALUES (%s, 'unidade') RETURNING id",
                (nome,),
            )
            unidade_id = cursor.fetchone()[0]
            cursor.execute(
                "INSERT INTO unidades_organizacionais (id, organizacao_pai_id) "
                "VALUES (%s, %s)",
                (unidade_id, organizacao_pai_id),
            )
        return unidade_id

    def garantir_papel(self, nome: str, escopo: str) -> int:
        if escopo not in ESCOPOS_PAPEL:
            raise ValueError(f"escopo de papel inválido: {escopo!r}")
        if not nome:
            raise ValueError("papel sem nome")
        if escopo in PAPEIS_FIXOS and nome not in PAPEIS_FIXOS[escopo]:
            raise ValueError(f"papel {nome!r} não é um papel fixo de {escopo}")

        alvo = normalize_text(nome)
        with self._conexao.cursor() as cursor:
            cursor.execute(
                "SELECT id, nome FROM papeis WHERE escopo = %s ORDER BY id", (escopo,)
            )
            for papel_id, papel_nome in cursor.fetchall():
                if normalize_text(papel_nome) == alvo:
                    return papel_id

            cursor.execute(
                "INSERT INTO papeis (nome, escopo) VALUES (%s, %s) RETURNING id",
                (nome, escopo),
            )
            return cursor.fetchone()[0]

    def adicionar_vinculo(
        self,
        pessoa_id: int,
        organizacao_id: int,
        papel_id: int,
        data_inicio: Optional[date],
        data_fim: Optional[date],
    ) -> bool:
        with self._conexao.cursor() as cursor:
            cursor.execute(
                """
                SELECT 1 FROM vinculos
                WHERE pessoa_id = %s AND organizacao_id = %s AND papel_id = %s
                  AND data_inicio IS NOT DISTINCT FROM %s::date
                """,
                (pessoa_id, organizacao_id, papel_id, data_inicio),
            )
            if cursor.fetchone():
                return False

            cursor.execute(
                """
                INSERT INTO vinculos
                    (pessoa_id, organizacao_id, papel_id, data_inicio, data_fim)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (pessoa_id, organizacao_id, papel_id, data_inicio, data_fim),
            )
        return True
