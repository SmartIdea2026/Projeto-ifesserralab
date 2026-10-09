from typing import Optional, Tuple

import psycopg

from src.core.logic.initiative_identity import normalize_text
from src.core.ports.repositorio_formacoes import (
    PAPEIS_ORIENTACAO_FORMACAO,
    RepositorioFormacoes,
)


class RepositorioFormacoesPostgres(RepositorioFormacoes):
    """Tipos de formação, formações e orientadores sobre ModeloLogicoHorizon.sql.

    Recebe uma conexão aberta e não faz commit. A formação não se repete quando
    todos os campos são iguais, como no ETL antigo.
    """

    def __init__(self, conexao: psycopg.Connection):
        self._conexao = conexao

    def garantir_tipo_formacao(self, nome: str) -> int:
        if not nome:
            raise ValueError("tipo de formação sem nome")

        alvo = normalize_text(nome)
        with self._conexao.cursor() as cursor:
            cursor.execute("SELECT id, nome FROM tipos_formacao ORDER BY id")
            for tipo_id, tipo_nome in cursor.fetchall():
                if normalize_text(tipo_nome) == alvo:
                    return tipo_id

            cursor.execute(
                "INSERT INTO tipos_formacao (nome) VALUES (%s) RETURNING id", (nome,)
            )
            return cursor.fetchone()[0]

    def adicionar_formacao(
        self,
        pessoa_id: int,
        tipo_formacao_id: int,
        organizacao_id: int,
        curso: str,
        ano_inicio: int,
        ano_fim: Optional[int],
        titulo_tese: Optional[str],
    ) -> Tuple[int, bool]:
        if curso is None or ano_inicio is None:
            raise ValueError("formação exige curso e ano de início")

        campos = (
            pessoa_id,
            tipo_formacao_id,
            organizacao_id,
            curso,
            ano_inicio,
            ano_fim,
            titulo_tese,
        )
        with self._conexao.cursor() as cursor:
            cursor.execute(
                """
                SELECT id FROM formacoes_academicas
                WHERE pessoa_id = %s AND tipo_formacao_id = %s
                  AND organizacao_id = %s AND curso = %s AND ano_inicio = %s
                  AND ano_fim IS NOT DISTINCT FROM %s::integer
                  AND titulo_tese IS NOT DISTINCT FROM %s::text
                ORDER BY id
                LIMIT 1
                """,
                campos,
            )
            linha = cursor.fetchone()
            if linha:
                return linha[0], False

            cursor.execute(
                """
                INSERT INTO formacoes_academicas (
                    pessoa_id, tipo_formacao_id, organizacao_id,
                    curso, ano_inicio, ano_fim, titulo_tese
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                campos,
            )
            return cursor.fetchone()[0], True

    def adicionar_orientador(
        self, formacao_id: int, pessoa_id: int, papel: str
    ) -> bool:
        if papel not in PAPEIS_ORIENTACAO_FORMACAO:
            raise ValueError(f"papel de orientação inválido: {papel!r}")

        with self._conexao.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO orientadores_formacao (formacao_id, pessoa_id, papel)
                VALUES (%s, %s, %s)
                ON CONFLICT (formacao_id, pessoa_id) DO NOTHING
                RETURNING formacao_id
                """,
                (formacao_id, pessoa_id, papel),
            )
            return cursor.fetchone() is not None
