"""Enriquecimento dos projetos pelos documentos PJ do SigPesq (``PJ_*.json``).

Reaproveita o casamento do ProjectEnrichmentLoader antigo (funções puras de
``project_enrichment``): código SigPesq > título exato > título aproximado
(>= 90), cada projeto disputado por um documento só.

Decisões da migração aplicadas aqui:

* preenche ``descricao`` vazia e cria projeto novo para documento rico sem par;
* o conteúdo extra do documento (objetivos, cronograma, linha de pesquisa...)
  não tem coluna no banco novo: é descartado e contado no relatório;
* o índice código → projeto vem dos projetos carregados nesta execução (antes
  vinha das tabelas de rastreamento);
* o que antes ficava marcado ``needs_review`` vai para a lista de revisão.
"""

import glob
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from src.core.logic.carga.contexto import ContextoCarga
from src.core.logic.carga.regras import situacao_iniciativa
from src.core.logic.initiative_identity import normalize_text
from src.core.logic.project_enrichment import (
    Candidate,
    compose_description,
    derive_status,
    is_ingestable,
    match_pj,
    parse_datetime,
    resolve_claims,
)

PASSO = "enriquecimento_pj"
PASTA_PADRAO = "data/exports/project_sigpesq_files_json"
TIPO_PROJETO_NOVO = "projeto_pesquisa"
TIPOS_PROJETO = ("projeto_pesquisa", "projeto_extensao", "projeto_desenvolvimento")

Documento = Tuple[str, dict]


def ler_documentos(pasta: str) -> List[Documento]:
    """Documentos ``PJ_*.json`` da pasta, em ordem de nome; ilegíveis são ignorados."""
    documentos: List[Documento] = []
    for caminho in sorted(glob.glob(os.path.join(pasta, "PJ_*.json"))):
        try:
            with open(caminho, encoding="utf-8") as arquivo:
                documentos.append((caminho, json.load(arquivo)))
        except (OSError, json.JSONDecodeError):
            continue
    return documentos


class CarregadorEnriquecimentoPJ:
    def __init__(
        self,
        contexto: ContextoCarga,
        projetos_por_codigo: Optional[Dict[str, int]] = None,
        criar_novos: bool = True,
    ):
        self._ctx = contexto
        self._projetos_por_codigo = projetos_por_codigo or {}
        self._criar_novos = criar_novos

    def carregar_pasta(self, pasta: str = PASTA_PADRAO) -> None:
        self.carregar(ler_documentos(pasta))

    def carregar(self, documentos: List[Documento]) -> None:
        with self._ctx.passo(PASSO):
            projetos = [
                projeto
                for tipo in TIPOS_PROJETO
                for projeto in self._ctx.iniciativas.listar(tipo)
            ]
            por_nome: Dict[str, List[int]] = {}
            aproximados: Dict[int, str] = {}
            for projeto in projetos:
                nome = normalize_text(projeto.nome)
                if nome:
                    por_nome.setdefault(nome, []).append(projeto.id)
                    aproximados[projeto.id] = nome
            descricoes = {p.id: (p.descricao or "").strip() for p in projetos}

            candidatos = [
                Candidate(
                    caminho,
                    pj,
                    match_pj(pj, self._projetos_por_codigo, por_nome, aproximados),
                )
                for caminho, pj in documentos
            ]
            vencedores, disputas = resolve_claims(candidatos)
            self._ctx.relatorio.contar(PASSO, "documentos", len(candidatos))
            self._ctx.relatorio.contar(PASSO, "disputas_descartadas", disputas)

            for candidato in vencedores:
                self._enriquecer(candidato, descricoes)

            sem_par = [c for c in candidatos if c.match is None]
            self._ctx.relatorio.contar(PASSO, "sem_par", len(sem_par))
            if self._criar_novos:
                self._criar_projetos(sem_par, set(por_nome))

    def _enriquecer(self, candidato: Candidate, descricoes: Dict[int, str]) -> None:
        projeto_id = candidato.match.initiative_id
        titulo = candidato.pj.get("titulo") or os.path.basename(candidato.path)
        with self._ctx.registro(PASSO, f"documento {os.path.basename(candidato.path)}"):
            nova = compose_description(candidato.pj)
            if nova and not descricoes.get(projeto_id):
                self._ctx.iniciativas.atualizar(projeto_id, {"descricao": nova})
                descricoes[projeto_id] = nova
                self._ctx.relatorio.contar(PASSO, "descricoes_preenchidas")
            self._ctx.relatorio.contar(PASSO, f"casados_{candidato.match.strategy}")
            self._ctx.relatorio.descartar(PASSO, "conteudo_pj")
            if candidato.match.needs_review:
                self._ctx.relatorio.revisar(
                    PASSO,
                    f"documento casado por {candidato.match.strategy}",
                    titulo,
                )

    def _criar_projetos(self, sem_par: List[Candidate], nomes: set) -> None:
        ifes_id = self._ctx.organizacoes.ifes_id()
        vistos: set = set()
        for candidato in sem_par:
            pj = candidato.pj
            if not is_ingestable(pj):
                self._ctx.relatorio.contar(PASSO, "sem_par_pobres")
                continue
            nome = (pj.get("titulo") or "").strip()
            normalizado = normalize_text(nome)
            if normalizado in nomes or normalizado in vistos:
                self._ctx.relatorio.contar(PASSO, "sem_par_repetidos")
                continue
            vistos.add(normalizado)

            datas = pj.get("datas") or {}
            with self._ctx.registro(
                PASSO, f"documento {os.path.basename(candidato.path)}"
            ):
                self._ctx.iniciativas.criar(
                    nome,
                    TIPO_PROJETO_NOVO,
                    ifes_id,
                    situacao_iniciativa(
                        derive_status(
                            datas.get("inicio"), datas.get("fim"), now=datetime.now()
                        )
                    ),
                    compose_description(pj),
                    parse_datetime(datas.get("inicio")),
                    parse_datetime(datas.get("fim")),
                )
                self._ctx.relatorio.contar(PASSO, "projetos_criados")
                self._ctx.relatorio.descartar(PASSO, "conteudo_pj")
                self._ctx.relatorio.revisar(
                    PASSO, "projeto criado a partir de documento PJ sem par", nome
                )
