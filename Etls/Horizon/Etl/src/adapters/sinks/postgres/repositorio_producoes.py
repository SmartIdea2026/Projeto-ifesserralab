from typing import Optional, Tuple

import psycopg

from src.core.logic.initiative_identity import normalize_text
from src.core.ports.repositorio_producoes import TIPO_ARTIGO, RepositorioProducoes


def link_do_doi(doi: Optional[str]) -> Optional[str]:
    """``https://doi.org/<doi>``; um DOI que já é URL é mantido como está."""
    if not doi:
        return None
    if doi.lower().startswith(("http://", "https://")):
        return doi
    if doi.lower().startswith("doi:"):
        doi = doi[4:].strip()
    return f"https://doi.org/{doi}"


def _limpar(valor: Optional[str]) -> Optional[str]:
    if valor is None:
        return None
    valor = str(valor).strip()
    return valor or None


class RepositorioProducoesPostgres(RepositorioProducoes):
    """Produções, artigos, tipos e autores sobre ModeloLogicoHorizon.sql.

    Recebe uma conexão aberta e não faz commit. Artigos e produções valem entre
    currículos: o mesmo artigo de dois coautores é gravado uma vez.
    """

    def __init__(self, conexao: psycopg.Connection):
        self._conexao = conexao

    def garantir_tipo_producao(self, nome: str) -> int:
        alvo = normalize_text(nome)
        if not alvo:
            raise ValueError("tipo de produção sem nome")

        with self._conexao.cursor() as cursor:
            cursor.execute("SELECT id, nome FROM tipos_producao ORDER BY id")
            for tipo_id, tipo_nome in cursor.fetchall():
                if normalize_text(tipo_nome) == alvo:
                    return tipo_id

            cursor.execute(
                "INSERT INTO tipos_producao (nome) VALUES (%s) RETURNING id",
                (nome.strip(),),
            )
            return cursor.fetchone()[0]

    def garantir_artigo(
        self,
        titulo: str,
        ano: int,
        veiculo: str,
        tipo: str = TIPO_ARTIGO,
        volume: Optional[str] = None,
        paginas: Optional[str] = None,
        doi: Optional[str] = None,
    ) -> Tuple[int, bool]:
        if not titulo or ano is None or not veiculo:
            raise ValueError("artigo exige título, ano e veículo")
        doi = _limpar(doi)

        existente = self._buscar_artigo(titulo, ano, doi)
        if existente is not None:
            return existente, False

        producao_id = self._criar_producao(titulo, ano, tipo, link_do_doi(doi))
        with self._conexao.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO artigos (id, veiculo, volume, paginas, doi)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (producao_id, veiculo, _limpar(volume), _limpar(paginas), doi),
            )
        return producao_id, True

    def garantir_producao(self, titulo: str, ano: int, tipo: str) -> Tuple[int, bool]:
        if not titulo or ano is None:
            raise ValueError("produção exige título e ano")
        tipo_id = self.garantir_tipo_producao(tipo)

        with self._conexao.cursor() as cursor:
            cursor.execute(
                """
                SELECT p.id FROM producoes p
                LEFT JOIN artigos a ON a.id = p.id
                WHERE a.id IS NULL
                  AND p.titulo = %s AND p.ano = %s AND p.tipo_producao_id = %s
                ORDER BY p.id
                LIMIT 1
                """,
                (titulo, ano, tipo_id),
            )
            linha = cursor.fetchone()
        if linha:
            return linha[0], False
        return self._criar_producao(titulo, ano, tipo, None), True

    def adicionar_autor(self, producao_id: int, pessoa_id: int) -> bool:
        with self._conexao.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO autores_producao (producao_id, pessoa_id)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING
                RETURNING producao_id
                """,
                (producao_id, pessoa_id),
            )
            return cursor.fetchone() is not None

    def _buscar_artigo(
        self, titulo: str, ano: int, doi: Optional[str]
    ) -> Optional[int]:
        with self._conexao.cursor() as cursor:
            if doi:
                cursor.execute("SELECT id FROM artigos WHERE doi = %s", (doi,))
                linha = cursor.fetchone()
                if linha:
                    return linha[0]

            cursor.execute(
                """
                SELECT p.id FROM producoes p
                JOIN artigos a ON a.id = p.id
                WHERE p.titulo = %s AND p.ano = %s
                ORDER BY p.id
                LIMIT 1
                """,
                (titulo, ano),
            )
            linha = cursor.fetchone()
        return linha[0] if linha else None

    def _criar_producao(
        self, titulo: str, ano: int, tipo: str, link: Optional[str]
    ) -> int:
        tipo_id = self.garantir_tipo_producao(tipo)
        with self._conexao.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO producoes (tipo_producao_id, titulo, ano, link)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """,
                (tipo_id, titulo, ano, link),
            )
            return cursor.fetchone()[0]
