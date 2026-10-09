import psycopg

from src.core.logic.initiative_identity import normalize_text
from src.core.ports.repositorio_areas_conhecimento import RepositorioAreasConhecimento


class RepositorioAreasConhecimentoPostgres(RepositorioAreasConhecimento):
    """Áreas de conhecimento e ligações com equipes, pessoas e iniciativas.

    Recebe uma conexão aberta e não faz commit. Uma só normalização de nome
    (``normalize_text``) para todas as fontes; o nome gravado é o da primeira
    vez em que a área aparece.
    """

    def __init__(self, conexao: psycopg.Connection):
        self._conexao = conexao

    def garantir_area(self, nome: str) -> int:
        alvo = normalize_text(nome)
        if not alvo:
            raise ValueError("área de conhecimento sem nome")

        with self._conexao.cursor() as cursor:
            cursor.execute("SELECT id, nome FROM areas_conhecimento ORDER BY id")
            for area_id, area_nome in cursor.fetchall():
                if normalize_text(area_nome) == alvo:
                    return area_id

            cursor.execute(
                "INSERT INTO areas_conhecimento (nome) VALUES (%s) RETURNING id",
                (nome.strip(),),
            )
            return cursor.fetchone()[0]

    def ligar_area_equipe(self, equipe_id: int, area_id: int) -> bool:
        return self._ligar(
            """
            INSERT INTO areas_conhecimento_equipe (equipe_id, area_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
            RETURNING area_id
            """,
            (equipe_id, area_id),
        )

    def ligar_area_pessoa(self, pessoa_id: int, area_id: int) -> bool:
        return self._ligar(
            """
            INSERT INTO areas_conhecimento_pessoa (pessoa_id, area_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
            RETURNING area_id
            """,
            (pessoa_id, area_id),
        )

    def ligar_area_iniciativa(self, iniciativa_id: int, area_id: int) -> bool:
        return self._ligar(
            """
            INSERT INTO areas_conhecimento_iniciativa (iniciativa_id, area_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
            RETURNING area_id
            """,
            (iniciativa_id, area_id),
        )

    def _ligar(self, consulta: str, parametros: tuple) -> bool:
        with self._conexao.cursor() as cursor:
            cursor.execute(consulta, parametros)
            return cursor.fetchone() is not None
