from datetime import date
from typing import List, Optional, Tuple

import psycopg

from src.core.logic.initiative_identity import normalize_text
from src.core.ports.repositorio_equipes import GrupoCadastrado, RepositorioEquipes


class RepositorioEquipesPostgres(RepositorioEquipes):
    """Equipes, grupos de pesquisa e membros sobre ModeloLogicoHorizon.sql.

    Recebe uma conexão aberta e não faz commit. Grupos são comparados pelo nome
    com ``normalize_text``, como no ETL antigo. A mesma pessoa pode ter mais de
    um papel na equipe; repete-se só equipe + pessoa + papel.
    """

    def __init__(self, conexao: psycopg.Connection):
        self._conexao = conexao

    def listar_grupos(self) -> List[GrupoCadastrado]:
        with self._conexao.cursor() as cursor:
            cursor.execute(
                """
                SELECT e.id, e.nome, e.organizacao_id, g.url_cnpq
                FROM equipes e
                JOIN grupos_pesquisa g ON g.id = e.id
                ORDER BY e.id
                """
            )
            return [GrupoCadastrado(*linha) for linha in cursor.fetchall()]

    def buscar_grupo_por_nome(self, nome: str) -> Optional[int]:
        alvo = normalize_text(nome)
        if not alvo:
            return None
        for grupo in self.listar_grupos():
            if normalize_text(grupo.nome) == alvo:
                return grupo.id
        return None

    def garantir_grupo(
        self,
        nome: str,
        organizacao_id: int,
        sigla: Optional[str] = None,
        descricao: Optional[str] = None,
    ) -> Tuple[int, bool]:
        if not nome:
            raise ValueError("grupo sem nome")

        existente = self.buscar_grupo_por_nome(nome)
        if existente is not None:
            return existente, False

        with self._conexao.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO equipes (nome, sigla, descricao, organizacao_id)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """,
                (nome, sigla, descricao, organizacao_id),
            )
            grupo_id = cursor.fetchone()[0]
            cursor.execute("INSERT INTO grupos_pesquisa (id) VALUES (%s)", (grupo_id,))
        return grupo_id, True

    def definir_url_cnpq(self, grupo_id: int, url: str) -> bool:
        if not url:
            return False

        with self._conexao.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM grupos_pesquisa WHERE url_cnpq = %s AND id <> %s",
                (url, grupo_id),
            )
            if cursor.fetchone():
                return False
            cursor.execute(
                "UPDATE grupos_pesquisa SET url_cnpq = %s WHERE id = %s",
                (url, grupo_id),
            )
        return True

    def atualizar_equipe(
        self,
        equipe_id: int,
        nome: Optional[str] = None,
        descricao: Optional[str] = None,
    ) -> None:
        with self._conexao.cursor() as cursor:
            cursor.execute(
                """
                UPDATE equipes
                SET nome = COALESCE(%s, nome), descricao = COALESCE(%s, descricao)
                WHERE id = %s
                """,
                (nome or None, descricao or None, equipe_id),
            )

    def definir_data_inicio_grupo(self, grupo_id: int, data_inicio: date) -> None:
        with self._conexao.cursor() as cursor:
            cursor.execute(
                "UPDATE grupos_pesquisa SET data_inicio = %s WHERE id = %s",
                (data_inicio, grupo_id),
            )

    def adicionar_membro(
        self,
        equipe_id: int,
        pessoa_id: int,
        papel_id: int,
        data_inicio: Optional[date],
        data_fim: Optional[date],
    ) -> bool:
        with self._conexao.cursor() as cursor:
            cursor.execute(
                """
                SELECT 1 FROM membros_equipe
                WHERE equipe_id = %s AND pessoa_id = %s AND papel_id = %s
                """,
                (equipe_id, pessoa_id, papel_id),
            )
            if cursor.fetchone():
                return False

            cursor.execute(
                """
                INSERT INTO membros_equipe
                    (equipe_id, pessoa_id, papel_id, data_inicio, data_fim)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (equipe_id, pessoa_id, papel_id, data_inicio, data_fim),
            )
        return True

    def definir_fim_membro(
        self, equipe_id: int, pessoa_id: int, papel_id: int, data_fim: date
    ) -> bool:
        with self._conexao.cursor() as cursor:
            cursor.execute(
                """
                UPDATE membros_equipe SET data_fim = %s
                WHERE equipe_id = %s AND pessoa_id = %s AND papel_id = %s
                  AND data_fim IS DISTINCT FROM %s::date
                """,
                (data_fim, equipe_id, pessoa_id, papel_id, data_fim),
            )
            return cursor.rowcount > 0
