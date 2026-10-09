"""Orquestração ETL: campus(es) -> ações -> detalhe -> JSON por ação.

`campus` aceita:
    - None            -> todos os campi (lidos do dropdown)
    - "Serra"         -> um campus
    - ["Serra", "..."]-> um conjunto de campi
"""

from __future__ import annotations

import asyncio
import json
import re
from pathlib import Path
from typing import Iterable

import httpx

from .detail import USER_AGENT, fetch_detalhe
from .gerenciar import coletar_participacoes
from .models import Acao, AcaoParticipacoes
from .scraper import coletar_campus, listar_campi
from . import database, crud

CampusArg = str | Iterable[str] | None


def _slug(nome: str) -> str:
    """Nome de campus -> nome de pasta seguro."""
    s = re.sub(r"[^\w]+", "-", nome.strip().lower(), flags=re.UNICODE)
    return s.strip("-") or "campus"


async def _resolver_campi(campus: CampusArg, *, headless: bool) -> list[str]:
    if campus is None:
        return await listar_campi(headless=headless)
    if isinstance(campus, str):
        return [campus]
    return list(campus)


async def extrair_campus(
    campus: str,
    *,
    headless: bool = True,
    max_acoes: int | None = None,
    on_progress=None,
    workers: int = 1,
) -> list[Acao]:
    """Extrai as ações de UM campus e devolve modelos `Acao` validados."""
    log = on_progress or (lambda _m: None)
    linhas = await coletar_campus(
        campus, headless=headless, max_acoes=max_acoes, on_progress=log, workers=workers
    )
    log(f"[{campus}] coletadas {len(linhas)} ações; baixando detalhes")

    acoes: list[Acao] = []
    with httpx.Client(follow_redirects=True, headers={"User-Agent": USER_AGENT}, timeout=30) as cli:
        for k, ref in enumerate(linhas, 1):
            if not ref.acao_id:
                log(f"  ! sem acao_id, pulando linha {ref.linha}")
                continue
            try:
                campos = fetch_detalhe(ref.acao_id, client=cli)
            except Exception as e:  # segue em caso de falha pontual
                log(f"  ! erro detalhe acao={ref.acao_id}: {e}")
                continue
            acoes.append(
                Acao.from_labels(ref.acao_id, campos, url_detalhe=ref.url_detalhe, campus=campus)
            )
            log(f"  [{campus} {k}/{len(linhas)}] {ref.acao_id} — {(acoes[-1].titulo or '')[:60]}")
    return acoes


async def extrair_campi(
    campus: CampusArg = None,
    *,
    headless: bool = True,
    max_acoes: int | None = None,
    on_progress=None,
    workers: int = 1,
) -> dict[str, list[Acao]]:
    """Extrai um, vários ou todos os campi. Devolve {campus: [Acao, ...]}."""
    log = on_progress or (lambda _m: None)
    campi = await _resolver_campi(campus, headless=headless)
    log(f"campi alvo ({len(campi)}): {', '.join(campi)}")

    resultado: dict[str, list[Acao]] = {}
    for c in campi:
        resultado[c] = await extrair_campus(
            c, headless=headless, max_acoes=max_acoes, on_progress=log, workers=workers
        )
    return resultado


def salvar_json_por_acao(acoes: list[Acao], out_dir: str | Path) -> Path:
    """Salva 1 JSON por ação em out_dir + _index.json. Retorna out_dir."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    index = []
    for a in acoes:
        arquivo = out / f"acao_{a.acao_id}.json"
        arquivo.write_text(a.model_dump_json(by_alias=True, indent=2), encoding="utf-8")
        index.append({"acao_id": a.acao_id, "processo": a.processo,
                      "titulo": a.titulo, "arquivo": arquivo.name})
    (out / "_index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return out


def salvar_por_campus(dados: dict[str, list[Acao]], out_dir: str | Path) -> Path:
    """Salva cada campus em out_dir/<campus>/ com 1 JSON por ação."""
    base = Path(out_dir)
    for campus, acoes in dados.items():
        salvar_json_por_acao(acoes, base / _slug(campus))
    return base


def processos_de_index(index_path: str | Path) -> list[str]:
    """Extrai os números de processo de um _index.json gerado pela etapa pública."""
    dados = json.loads(Path(index_path).read_text(encoding="utf-8"))
    vistos, out = set(), []
    for item in dados:
        proc = item.get("processo")
        if proc and proc not in vistos:
            vistos.add(proc)
            out.append(proc)
    return out


def run_participacoes(
    processos: list[str],
    out_dir: str | Path = "data",
    *,
    user: str | None = None,
    senha: str | None = None,
    headless: bool = True,
    on_progress=None,
    workers: int = 1,
    save_json: bool = False
) -> dict[str, AcaoParticipacoes]:
    """Coleta participações (público-alvo + equipe) e salva no banco de dados.

    save_json=True preserva o comportamento legado de salvar 1 JSON por processo.
    workers>1: N abas numa única sessão (um login) processam processos em paralelo.
    """
    import asyncio

    out = Path(out_dir)
    if save_json:
        out.mkdir(parents=True, exist_ok=True)

    def _arquivo(proc: str) -> Path:
        return out / ("participacoes_" + proc.replace("/", "-") + ".json")

    # resume: pula processos já salvos se save_json for true, 
    # senão confia no upsert do banco e processa a lista
    pendentes = processos
    if save_json:
        pendentes = [p for p in processos if not _arquivo(p).exists()]
        if len(pendentes) < len(processos) and on_progress:
            on_progress(f"resume: {len(processos)-len(pendentes)} já salvos, "
                        f"{len(pendentes)} pendentes")

    def salvar(ap: AcaoParticipacoes) -> None:  # save incremental
        db = database.SessionLocal()
        try:
            crud.upsert_participacoes(db, ap)
        finally:
            db.close()
            
        if save_json:
            _arquivo(ap.processo).write_text(ap.model_dump_json(indent=2), encoding="utf-8")

    dados = asyncio.run(
        coletar_participacoes(pendentes, user=user, senha=senha, headless=headless,
                              on_progress=on_progress, on_processo=salvar, workers=workers)
    )
    return dados


def run(
    campus: CampusArg = None,
    out_dir: str | Path = "data",
    *,
    headless: bool = True,
    max_acoes: int | None = None,
    on_progress=None,
    workers: int = 1,
    save_json: bool = False
) -> dict[str, list[Acao]]:
    """Ponto de entrada síncrono: extrai o(s) campus(es) e salva no banco de dados.

    Args:
        campus: None (todos) | "Serra" (um) | ["Serra", "Vitória"] (conjunto).
        out_dir: diretório-base de saída (um subdiretório por campus), se save_json=True.
        workers: abas paralelas no crawl público (agiliza; ignora max_acoes).
        save_json: se True, salva JSON por ação além da gravação no banco.
    """
    dados = asyncio.run(
        extrair_campi(campus, headless=headless, max_acoes=max_acoes,
                      on_progress=on_progress, workers=workers)
    )
    
    db = database.SessionLocal()
    try:
        for c, acoes in dados.items():
            for acao in acoes:
                crud.upsert_acao(db, acao)
    finally:
        db.close()

    if save_json:
        salvar_por_campus(dados, out_dir)
        
    return dados

def run_vinculadas(on_progress=None) -> None:
    """Extrai vínculos (Ações Vinculadas) e grava no banco de dados."""
    from .vinculadas import fetch_vinculadas
    log = on_progress or (lambda _m: None)
    
    db = database.SessionLocal()
    try:
        acoes = db.query(database.Acao.id, database.Acao.acao_original_id, database.Acao.processo).all()
        log(f"Iniciando busca de ações vinculadas (avaliando {len(acoes)} ações-mãe cadastradas)...")
        
        with httpx.Client(follow_redirects=True, headers={"User-Agent": USER_AGENT}, timeout=30) as cli:
            for acao_db_id, acao_original_id, processo in acoes:
                try:
                    filhas = fetch_vinculadas(acao_original_id, cli)
                    if filhas:
                        crud.upsert_vinculadas(db, acao_db_id, filhas)
                        log(f"  {processo}: {len(filhas)} vinculadas encontradas e salvas.")
                except Exception as e:
                    log(f"  ! erro ao buscar vinculadas para {processo}: {e}")
    finally:
        db.close()
