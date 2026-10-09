"""Pipeline do banco Horizon em PostgreSQL (ModeloLogicoHorizon.sql).

Substitui o ``full_ingestion_pipeline`` para o banco novo, que continua
existindo para o SQLite antigo. Cada execução recria o banco (recarga completa)
e grava o relatório em ``data/reports/carga_postgres*.json``.

Uso: ``python -m src.flows.pipelines.horizon_postgres [--campus Serra] [--sem-download]``
"""

import argparse
from typing import Optional

from dotenv import load_dotenv
from prefect import flow, get_run_logger

from src.adapters.sinks.postgres.conexao import abrir_conexao
from src.core.logic.carga.pipeline import ConfiguracaoCarga, executar_carga
from src.core.logic.carga.relatorio import PASTA_PADRAO, RelatorioCarga
from src.core.logic.prefect_runtime import configure_local_prefect_runtime
from src.flows.sigpesq.all import download_all_sigpesq_reports
from src.notifications.telegram import telegram_flow_state_handlers

load_dotenv()
configure_local_prefect_runtime()


@flow(name="Horizon Pipeline PostgreSQL", **telegram_flow_state_handlers())
def pipeline_horizon_postgres(
    campus_name: Optional[str] = None,
    baixar_sigpesq: bool = True,
    pasta_relatorio: str = PASTA_PADRAO,
) -> str:
    """Baixa o SigPesq (opcional), recria o banco Horizon e carrega todas as fontes.

    Devolve o caminho do relatório da carga.
    """
    logger = get_run_logger()
    if baixar_sigpesq:
        logger.info("Baixando os relatórios do SigPesq (um login só)...")
        download_all_sigpesq_reports()

    relatorio = RelatorioCarga()
    try:
        with abrir_conexao() as conexao:
            executar_carga(
                conexao,
                relatorio,
                ConfiguracaoCarga(campus=campus_name),
                registrar=logger.info,
            )
    finally:
        caminho = relatorio.salvar(pasta_relatorio)
        logger.info(
            f"Relatório da carga: {caminho} "
            f"({len(relatorio.pendencias)} pendência(s), "
            f"{len(relatorio.revisoes)} item(ns) para revisar)"
        )
    return caminho


def main() -> None:
    argumentos = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    argumentos.add_argument("--campus", default=None, help="filtro de campus do CNPq")
    argumentos.add_argument(
        "--sem-download",
        action="store_true",
        help="usa as planilhas do SigPesq que já estão em data/raw/sigpesq",
    )
    opcoes = argumentos.parse_args()
    pipeline_horizon_postgres(
        campus_name=opcoes.campus, baixar_sigpesq=not opcoes.sem_download
    )


if __name__ == "__main__":
    main()
