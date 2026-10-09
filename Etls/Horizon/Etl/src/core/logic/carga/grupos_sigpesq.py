"""Carga dos grupos de pesquisa do SigPesq no banco Horizon.

Mesmas regras do ResearchGroupLoader antigo:

* o grupo é casado pelo nome normalizado; se já existe, só a URL do CNPq é
  atualizada e os líderes não são mexidos;
* grupo sem unidade vai para o "Campus Desconhecido" (unidade do IFES);
* os líderes ("Nome (email)") entram como membros com papel ``lider``.

Diferenças decididas na migração: o líder fica sem data de início (antes era a
data da carga) e a pessoa é resolvida pelo PersonMatcher, o mesmo das outras fontes.
"""

from typing import Iterable, Optional

import pandas as pd

from src.core.logic.carga.contexto import ContextoCarga
from src.core.logic.carga.regras import texto
from src.core.logic.strategies.sigpesq_excel import SigPesqExcelMappingStrategy

PASSO = "grupos_sigpesq"
CAMPUS_DESCONHECIDO = "Campus Desconhecido"


class CarregadorGruposSigpesq:
    def __init__(
        self,
        contexto: ContextoCarga,
        estrategia: Optional[SigPesqExcelMappingStrategy] = None,
    ):
        self._ctx = contexto
        self._estrategia = estrategia or SigPesqExcelMappingStrategy()

    def carregar_arquivo(self, caminho: str) -> None:
        """Lê a planilha de grupos do SigPesq e carrega as linhas."""
        self.carregar_linhas(pd.read_excel(caminho).to_dict("records"))

    def carregar_linhas(self, linhas: Iterable[dict]) -> None:
        with self._ctx.passo(PASSO):
            ifes_id = self._ctx.organizacoes.ifes_id()
            papel_lider = self._ctx.organizacoes.garantir_papel("lider", "equipe")

            for numero, linha in enumerate(linhas, start=1):
                dados = self._estrategia.map_row(linha)
                nome = texto(dados.get("name"))
                if not nome:
                    self._ctx.relatorio.pular(
                        PASSO, "grupo sem nome", f"linha {numero}"
                    )
                    continue
                with self._ctx.registro(PASSO, f"grupo {nome}"):
                    self._carregar_grupo(dados, nome, ifes_id, papel_lider)

    def _carregar_grupo(
        self, dados: dict, nome: str, ifes_id: int, papel_lider: int
    ) -> None:
        url_cnpq = texto(dados.get("site_url"))

        existente = self._ctx.equipes.buscar_grupo_por_nome(nome)
        if existente is not None:
            self._definir_url_cnpq(existente, url_cnpq, nome)
            self._ctx.relatorio.contar(PASSO, "grupos_repetidos")
            return

        campus = texto(dados.get("campus_name")) or CAMPUS_DESCONHECIDO
        campus_id = self._ctx.organizacoes.garantir_unidade(campus, ifes_id)
        grupo_id, _ = self._ctx.equipes.garantir_grupo(
            nome, campus_id, sigla=texto(dados.get("short_name"))
        )
        self._definir_url_cnpq(grupo_id, url_cnpq, nome)

        area = texto(dados.get("area_name"))
        if area:
            area_id = self._ctx.areas.garantir_area(area)
            self._ctx.areas.ligar_area_equipe(grupo_id, area_id)

        for nome_lider, email in self._estrategia.parse_leaders(
            dados.get("leaders_raw")
        ):
            pessoa = self._ctx.casamento_pessoas.match_or_create(
                nome_lider, email=email, strict_match=True
            )
            if pessoa is None:
                self._ctx.relatorio.pular(PASSO, "líder sem nome nem e-mail", nome)
                continue
            if self._ctx.equipes.adicionar_membro(
                grupo_id, pessoa.id, papel_lider, None, None
            ):
                self._ctx.relatorio.contar(PASSO, "lideres")

        self._ctx.relatorio.contar(PASSO, "grupos_criados")

    def _definir_url_cnpq(
        self, grupo_id: int, url_cnpq: Optional[str], nome: str
    ) -> None:
        if url_cnpq and not self._ctx.equipes.definir_url_cnpq(grupo_id, url_cnpq):
            self._ctx.relatorio.pular(
                PASSO, "URL CNPq não gravada: já é de outro grupo", nome
            )
