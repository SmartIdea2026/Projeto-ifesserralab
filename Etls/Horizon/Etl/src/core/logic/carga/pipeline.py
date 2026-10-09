"""Ordem da carga no banco Horizon, na mesma sequência do pipeline unificado antigo.

1. recarga completa: o schema é recriado a partir de ModeloLogicoHorizon.sql;
2. SigPesq: grupos, projetos e bolsistas (planilhas mais recentes em disco);
3. CNPq: grupos com URL do espelho, com filtro opcional de campus;
4. Lattes: pessoas, currículos e orientações (JSON do scriptLattes);
5. enriquecimento dos projetos pelos documentos PJ.

Sem exports, marts, rastreamento nem relatório via sqlite3 (decisões 5 e 11).
O download do SigPesq fica no flow, que chama esta função depois.
"""

import glob
import os
from dataclasses import dataclass
from typing import Any, Callable, List, Optional

import psycopg
from psycopg import sql

from src.core.logic.carga.contexto import ContextoCarga
from src.core.logic.carga.enriquecimento_pj import PASTA_PADRAO as PASTA_PJ_PADRAO
from src.core.logic.carga.enriquecimento_pj import CarregadorEnriquecimentoPJ
from src.core.logic.carga.grupos_cnpq import CarregadorCnpq
from src.core.logic.carga.grupos_sigpesq import CarregadorGruposSigpesq
from src.core.logic.carga.iniciativas_sigpesq import CarregadorIniciativasSigpesq
from src.core.logic.carga.lattes import CarregadorLattes, ler_curriculos
from src.core.logic.carga.relatorio import RelatorioCarga
from src.db.esquema_horizon import aplicar_schema

PASSO_ARQUIVOS = "arquivos"


@dataclass
class ConfiguracaoCarga:
    pasta_sigpesq: str = "data/raw/sigpesq"
    pasta_lattes: str = "data/lattes_json"
    pasta_pj: str = PASTA_PJ_PADRAO
    campus: Optional[str] = None
    schema: str = "public"


def planilha_mais_recente(padrao: str) -> Optional[str]:
    arquivos = glob.glob(padrao)
    return max(arquivos, key=os.path.getmtime) if arquivos else None


def planilhas_de_bolsistas(pasta_sigpesq: str) -> List[str]:
    """Como o fluxo antigo: subpasta advisorships (recursiva) ou a raiz do SigPesq."""
    arquivos = glob.glob(
        os.path.join(pasta_sigpesq, "advisorships", "**", "*.xlsx"), recursive=True
    )
    if not arquivos:
        arquivos = glob.glob(os.path.join(pasta_sigpesq, "*.xlsx"))
    return sorted(arquivos, key=os.path.getmtime)


def executar_carga(
    conexao: psycopg.Connection,
    relatorio: RelatorioCarga,
    configuracao: Optional[ConfiguracaoCarga] = None,
    adaptador_cnpq: Optional[Any] = None,
    registrar: Callable[[str], None] = print,
) -> None:
    config = configuracao or ConfiguracaoCarga()

    registrar(f"Recriando o schema '{config.schema}' (recarga completa)...")
    aplicar_schema(conexao, schema=config.schema)
    with conexao.cursor() as cursor:
        cursor.execute(
            sql.SQL("SET search_path TO {}").format(sql.Identifier(config.schema))
        )
    contexto = ContextoCarga.criar(conexao, relatorio)

    grupos = planilha_mais_recente(
        os.path.join(config.pasta_sigpesq, "research_group", "*.xlsx")
    )
    if grupos:
        registrar(f"SigPesq grupos: {grupos}")
        CarregadorGruposSigpesq(contexto).carregar_arquivo(grupos)
    else:
        relatorio.pular(PASSO_ARQUIVOS, "planilha de grupos não encontrada", "SigPesq")

    iniciativas = CarregadorIniciativasSigpesq(contexto)
    projetos = planilha_mais_recente(
        os.path.join(config.pasta_sigpesq, "research_projects", "*.xlsx")
    )
    if projetos:
        registrar(f"SigPesq projetos: {projetos}")
        iniciativas.carregar_projetos_arquivo(projetos)
    else:
        relatorio.pular(
            PASSO_ARQUIVOS, "planilha de projetos não encontrada", "SigPesq"
        )

    bolsistas = planilhas_de_bolsistas(config.pasta_sigpesq)
    if bolsistas:
        registrar(f"SigPesq bolsistas: {len(bolsistas)} planilha(s)")
        iniciativas.carregar_bolsistas_arquivos(bolsistas)
    else:
        relatorio.pular(
            PASSO_ARQUIVOS, "planilha de bolsistas não encontrada", "SigPesq"
        )

    registrar(f"CNPq (campus: {config.campus or 'todos'})...")
    CarregadorCnpq(contexto, adaptador_cnpq).carregar(config.campus)

    curriculos = ler_curriculos(config.pasta_lattes)
    registrar(f"Lattes: {len(curriculos)} currículo(s)")
    if curriculos:
        CarregadorLattes(contexto).carregar(curriculos)
    else:
        relatorio.pular(PASSO_ARQUIVOS, "nenhum currículo encontrado", "Lattes")

    registrar("Enriquecimento pelos documentos PJ...")
    CarregadorEnriquecimentoPJ(
        contexto, iniciativas.projetos_por_codigo()
    ).carregar_pasta(config.pasta_pj)
