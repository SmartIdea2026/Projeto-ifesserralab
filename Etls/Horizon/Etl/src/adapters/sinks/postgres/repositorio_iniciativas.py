from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple, Union

import psycopg
from psycopg import sql

from src.core.ports.repositorio_iniciativas import (
    CAMPOS_ATUALIZAVEIS,
    PAPEIS_EQUIPE_INICIATIVA,
    PAPEIS_ORGANIZACAO_INICIATIVA,
    SITUACOES_INICIATIVA,
    IniciativaCadastrada,
    RepositorioIniciativas,
)

_SELECT_INICIATIVA = """
    SELECT i.id, i.nome, t.nome, i.situacao, i.organizacao_id,
           i.descricao, i.data_inicio, i.data_fim
    FROM iniciativas i
    JOIN tipos_iniciativa t ON t.id = i.tipo_iniciativa_id
"""


def _como_data(valor: Optional[Any]) -> Optional[date]:
    """As estratégias de mapeamento entregam datetime; as colunas são DATE."""
    if isinstance(valor, datetime):
        return valor.date()
    return valor


def _validar_situacao(situacao: str) -> None:
    if situacao not in SITUACOES_INICIATIVA:
        raise ValueError(f"situação de iniciativa inválida: {situacao!r}")


class RepositorioIniciativasPostgres(RepositorioIniciativas):
    """Iniciativas e ligações sobre ModeloLogicoHorizon.sql.

    Recebe uma conexão aberta e não faz commit. Casos esperados (participante,
    bolsa ou ligação repetidos) são tratados sem erro de banco.
    """

    def __init__(self, conexao: psycopg.Connection):
        self._conexao = conexao

    def tipo_iniciativa_id(self, nome: str) -> int:
        with self._conexao.cursor() as cursor:
            cursor.execute("SELECT id FROM tipos_iniciativa WHERE nome = %s", (nome,))
            linha = cursor.fetchone()
        if not linha:
            raise ValueError(f"tipo de iniciativa desconhecido: {nome!r}")
        return linha[0]

    def criar(
        self,
        nome: str,
        tipo: str,
        organizacao_id: int,
        situacao: str,
        descricao: Optional[str] = None,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
    ) -> int:
        if not nome:
            raise ValueError("iniciativa sem nome")
        _validar_situacao(situacao)
        tipo_id = self.tipo_iniciativa_id(tipo)

        with self._conexao.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO iniciativas (
                    nome, tipo_iniciativa_id, organizacao_id, situacao,
                    descricao, data_inicio, data_fim
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    nome,
                    tipo_id,
                    organizacao_id,
                    situacao,
                    descricao,
                    _como_data(data_inicio),
                    _como_data(data_fim),
                ),
            )
            return cursor.fetchone()[0]

    def atualizar(self, iniciativa_id: int, campos: Dict[str, Any]) -> None:
        if not campos:
            return
        invalidos = set(campos) - set(CAMPOS_ATUALIZAVEIS)
        if invalidos:
            raise ValueError(f"campos que não podem ser atualizados: {invalidos}")
        if "situacao" in campos:
            _validar_situacao(campos["situacao"])
        if "nome" in campos and not campos["nome"]:
            raise ValueError("iniciativa sem nome")

        valores = {
            campo: (
                _como_data(valor) if campo in ("data_inicio", "data_fim") else valor
            )
            for campo, valor in campos.items()
        }
        atribuicoes = sql.SQL(", ").join(
            sql.SQL("{} = {}").format(sql.Identifier(campo), sql.Placeholder(campo))
            for campo in valores
        )
        with self._conexao.cursor() as cursor:
            cursor.execute(
                sql.SQL("UPDATE iniciativas SET {} WHERE id = {}").format(
                    atribuicoes, sql.Placeholder("_id")
                ),
                {**valores, "_id": iniciativa_id},
            )

    def buscar(self, iniciativa_id: int) -> Optional[IniciativaCadastrada]:
        encontradas = self._consultar(" WHERE i.id = %s", (iniciativa_id,))
        return encontradas[0] if encontradas else None

    def buscar_por_nome(
        self, nome: str, tipo: Optional[str] = None
    ) -> List[IniciativaCadastrada]:
        if tipo is None:
            return self._consultar(" WHERE i.nome = %s ORDER BY i.id", (nome,))
        return self._consultar(
            " WHERE i.nome = %s AND t.nome = %s ORDER BY i.id", (nome, tipo)
        )

    def listar(self, tipo: Optional[str] = None) -> List[IniciativaCadastrada]:
        if tipo is None:
            return self._consultar(" ORDER BY i.id", ())
        return self._consultar(" WHERE t.nome = %s ORDER BY i.id", (tipo,))

    def definir_pai(self, iniciativa_id: int, pai_id: int) -> None:
        if iniciativa_id == pai_id:
            raise ValueError("iniciativa não pode ser mãe de si mesma")
        with self._conexao.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO hierarquia_iniciativas (iniciativa_id, iniciativa_pai_id)
                VALUES (%s, %s)
                ON CONFLICT (iniciativa_id)
                DO UPDATE SET iniciativa_pai_id = EXCLUDED.iniciativa_pai_id
                """,
                (iniciativa_id, pai_id),
            )

    def periodos_dos_filhos(
        self,
    ) -> Dict[int, Tuple[Optional[date], Optional[date]]]:
        with self._conexao.cursor() as cursor:
            cursor.execute(
                """
                SELECT h.iniciativa_pai_id, MIN(i.data_inicio), MAX(i.data_fim)
                FROM hierarquia_iniciativas h
                JOIN iniciativas i ON i.id = h.iniciativa_id
                GROUP BY h.iniciativa_pai_id
                """
            )
            return {pai: (inicio, fim) for pai, inicio, fim in cursor.fetchall()}

    def adicionar_participante(
        self,
        iniciativa_id: int,
        pessoa_id: int,
        papel_id: int,
        data_inicio: Optional[date],
        data_fim: Optional[date],
    ) -> Tuple[int, bool]:
        with self._conexao.cursor() as cursor:
            cursor.execute(
                """
                SELECT id FROM participantes_iniciativa
                WHERE iniciativa_id = %s AND pessoa_id = %s AND papel_id = %s
                ORDER BY id
                LIMIT 1
                """,
                (iniciativa_id, pessoa_id, papel_id),
            )
            linha = cursor.fetchone()
            if linha:
                return linha[0], False

            cursor.execute(
                """
                INSERT INTO participantes_iniciativa
                    (iniciativa_id, pessoa_id, papel_id, data_inicio, data_fim)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    iniciativa_id,
                    pessoa_id,
                    papel_id,
                    _como_data(data_inicio),
                    _como_data(data_fim),
                ),
            )
            return cursor.fetchone()[0], True

    def garantir_bolsa(
        self, nome: str, financiador_id: int, valor: Union[Decimal, float]
    ) -> int:
        if not nome or not nome.strip():
            raise ValueError("bolsa sem nome")
        if valor is None:
            raise ValueError("bolsa sem valor")

        with self._conexao.cursor() as cursor:
            # Mesma comparação do ETL antigo: nome sem espaços nas pontas e sem caixa.
            cursor.execute(
                """
                SELECT id FROM bolsas
                WHERE lower(trim(nome)) = lower(trim(%s)) AND financiador_id = %s
                ORDER BY id
                LIMIT 1
                """,
                (nome, financiador_id),
            )
            linha = cursor.fetchone()
            if linha:
                return linha[0]

            cursor.execute(
                """
                INSERT INTO bolsas (nome, valor, financiador_id)
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (nome.strip(), valor, financiador_id),
            )
            return cursor.fetchone()[0]

    def definir_bolsa_participante(self, participante_id: int, bolsa_id: int) -> None:
        with self._conexao.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO bolsas_participante (participante_id, bolsa_id)
                VALUES (%s, %s)
                ON CONFLICT (participante_id) DO UPDATE SET bolsa_id = EXCLUDED.bolsa_id
                """,
                (participante_id, bolsa_id),
            )

    def ligar_equipe(self, iniciativa_id: int, equipe_id: int, papel: str) -> bool:
        if papel not in PAPEIS_EQUIPE_INICIATIVA:
            raise ValueError(f"papel de equipe na iniciativa inválido: {papel!r}")
        return self._ligar(
            """
            INSERT INTO equipes_iniciativa (iniciativa_id, equipe_id, papel)
            VALUES (%s, %s, %s)
            ON CONFLICT DO NOTHING
            RETURNING equipe_id
            """,
            (iniciativa_id, equipe_id, papel),
        )

    def ligar_organizacao(
        self, iniciativa_id: int, organizacao_id: int, papel: str
    ) -> bool:
        if papel not in PAPEIS_ORGANIZACAO_INICIATIVA:
            raise ValueError(f"papel de organização na iniciativa inválido: {papel!r}")
        return self._ligar(
            """
            INSERT INTO organizacoes_iniciativa (iniciativa_id, organizacao_id, papel)
            VALUES (%s, %s, %s)
            ON CONFLICT DO NOTHING
            RETURNING organizacao_id
            """,
            (iniciativa_id, organizacao_id, papel),
        )

    def _ligar(self, consulta: str, parametros: tuple) -> bool:
        with self._conexao.cursor() as cursor:
            cursor.execute(consulta, parametros)
            return cursor.fetchone() is not None

    def _consultar(
        self, complemento: str, parametros: tuple
    ) -> List[IniciativaCadastrada]:
        with self._conexao.cursor() as cursor:
            cursor.execute(_SELECT_INICIATIVA + complemento, parametros)
            return [IniciativaCadastrada(*linha) for linha in cursor.fetchall()]
