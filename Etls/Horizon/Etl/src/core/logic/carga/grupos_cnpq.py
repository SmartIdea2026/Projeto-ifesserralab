"""Sincronização dos grupos de pesquisa com o espelho do CNPq (DGP).

Mesmas regras do CnpqSyncLogic e do fluxo ``sync_cnpq_groups_flow`` antigos:

* só grupos com URL do CNPq, com filtro opcional pelo nome do campus;
* o nome do grupo (exceto o cabeçalho "CNPq") e as repercussões (descrição)
  vêm do espelho; o ano de formação vira a data de início do grupo;
* membros e líderes entram com papel e datas; o membro que já existe recebe a
  data de fim quando o CNPq trouxer uma diferente;
* linhas de pesquisa viram áreas de conhecimento do grupo.

Decisões da migração aplicadas aqui: papel fixo de equipe (pesquisador,
estudante, tecnico, lider); egresso é o papel base com data de fim; a pessoa
pode ter mais de um papel no grupo; pessoas resolvidas pelo PersonMatcher.
"""

from typing import Any, Dict, List, Optional

from src.core.logic.carga.contexto import ContextoCarga
from src.core.logic.carga.regras import (
    data_cnpq,
    data_formacao_cnpq,
    papel_equipe_cnpq,
    texto,
    texto_cnpq,
)
from src.core.ports.repositorio_equipes import GrupoCadastrado
from src.core.ports.repositorio_organizacoes import PAPEIS_FIXOS

PASSO = "cnpq"


class CarregadorCnpq:
    def __init__(self, contexto: ContextoCarga, adaptador: Optional[Any] = None):
        self._ctx = contexto
        if adaptador is None:
            from src.adapters.sources.cnpq_crawler import CnpqCrawlerAdapter

            adaptador = CnpqCrawlerAdapter()
        self._adaptador = adaptador

    def grupos_para_sincronizar(
        self, campus: Optional[str] = None
    ) -> List[GrupoCadastrado]:
        """Grupos com URL do CNPq; com ``campus``, só os do primeiro campus cujo
        nome contém o texto, como no fluxo antigo."""
        grupos = [g for g in self._ctx.equipes.listar_grupos() if g.url_cnpq]
        if not campus:
            return grupos

        unidades = [
            unidade_id
            for unidade_id, nome in self._ctx.organizacoes.listar_unidades(
                self._ctx.organizacoes.ifes_id()
            )
            if campus.lower() in nome.lower()
        ]
        if not unidades:
            self._ctx.relatorio.pular(PASSO, "nenhum campus com esse nome", campus)
            return []
        if len(unidades) > 1:
            self._ctx.relatorio.revisar(
                PASSO, "mais de um campus casa com o filtro; usado o primeiro", campus
            )
        return [g for g in grupos if g.organizacao_id == unidades[0]]

    def carregar(self, campus: Optional[str] = None) -> None:
        with self._ctx.passo(PASSO):
            papeis = {
                nome: self._ctx.organizacoes.garantir_papel(nome, "equipe")
                for nome in PAPEIS_FIXOS["equipe"]
            }
            for grupo in self.grupos_para_sincronizar(campus):
                dados = self._adaptador.get_group_data(grupo.url_cnpq)
                if not dados:
                    self._ctx.relatorio.pular(
                        PASSO, "falha ao ler o espelho do CNPq", grupo.nome
                    )
                    continue
                with self._ctx.registro(PASSO, f"grupo {grupo.nome}"):
                    self._sincronizar_grupo(grupo, dados, papeis)

    def _sincronizar_grupo(
        self, grupo: GrupoCadastrado, dados: dict, papeis: Dict[str, int]
    ) -> None:
        nome = texto_cnpq(dados.get("nome_grupo"))
        if nome and nome.upper() == "CNPQ":
            nome = None
        repercussoes = texto_cnpq(dados.get("repercussoes"))
        if nome or repercussoes:
            self._ctx.equipes.atualizar_equipe(
                grupo.id, nome=nome, descricao=repercussoes
            )

        identificacao = dados.get("identificacao") or {}
        formacao = data_formacao_cnpq(
            identificacao.get("ano_de_formacao")
            or identificacao.get("data_de_formacao")
        )
        if formacao:
            self._ctx.equipes.definir_data_inicio_grupo(grupo.id, formacao)

        membros = list(self._adaptador.extract_members(dados))
        membros += [
            {"name": lider, "role": "Líder", "data_inicio": None, "data_fim": None}
            for lider in self._adaptador.extract_leaders(dados)
        ]
        for membro in membros:
            nome_membro = texto(membro.get("name"))
            if not nome_membro:
                self._ctx.relatorio.contar(PASSO, "membros_sem_nome")
                continue
            with self._ctx.registro(PASSO, f"membro {nome_membro} em {grupo.nome}"):
                self._membro(grupo, nome_membro, membro, papeis)

        for linha in self._adaptador.extract_research_lines(dados):
            nome_linha = texto(linha.get("nome_da_linha_de_pesquisa"))
            if nome_linha:
                area_id = self._ctx.areas.garantir_area(nome_linha)
                if self._ctx.areas.ligar_area_equipe(grupo.id, area_id):
                    self._ctx.relatorio.contar(PASSO, "linhas_de_pesquisa")

        self._ctx.relatorio.contar(PASSO, "grupos_sincronizados")

    def _membro(
        self,
        grupo: GrupoCadastrado,
        nome: str,
        membro: dict,
        papeis: Dict[str, int],
    ) -> None:
        papel, egresso = papel_equipe_cnpq(membro.get("role"))
        if papel is None:
            self._ctx.relatorio.pular(
                PASSO, f"papel do CNPq desconhecido: {membro.get('role')}", nome
            )
            return

        pessoa = self._ctx.casamento_pessoas.match_or_create(nome, strict_match=True)
        if pessoa is None:
            raise ValueError("não foi possível criar a pessoa")

        inicio = data_cnpq(membro.get("data_inicio"))
        fim = data_cnpq(membro.get("data_fim")) if membro.get("data_fim") else None
        papel_id = papeis[papel]
        if self._ctx.equipes.adicionar_membro(
            grupo.id, pessoa.id, papel_id, inicio, fim
        ):
            self._ctx.relatorio.contar(PASSO, "membros")
        elif fim and self._ctx.equipes.definir_fim_membro(
            grupo.id, pessoa.id, papel_id, fim
        ):
            self._ctx.relatorio.contar(PASSO, "membros_com_fim_atualizado")

        if egresso and fim is None:
            self._ctx.relatorio.revisar(
                PASSO, "egresso sem data de fim no CNPq", f"{nome} em {grupo.nome}"
            )
