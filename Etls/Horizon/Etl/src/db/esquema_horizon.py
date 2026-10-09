"""Cria o schema do banco Horizon no PostgreSQL a partir de ModeloLogicoHorizon.sql.

O modelo é a fonte da verdade e não é editado. O que o PostgreSQL não aceita, ou
o que a Etapa 1 decidiu ajustar, é tratado aqui ao aplicar:

* ``DATETIME`` vira ``TIMESTAMP`` em memória, antes do ``CREATE TABLE``;
* ``sql/ajustes_postgres.sql`` dá ids gerados pelo banco, amplia títulos e nomes
  para ``TEXT`` e troca a unicidade de ``bolsas`` para nome + financiador;
* ``sql/dados_iniciais.sql`` grava os tipos iniciais.

A aplicação é repetível: o schema de destino é apagado e recriado numa única
transação (a carga do Horizon é uma recarga completa a cada execução).

Uso: ``python -m src.db.esquema_horizon`` com ``HORIZON_DATABASE_URL`` definida.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Optional

import psycopg
from loguru import logger
from psycopg import sql

RAIZ_ETL = Path(__file__).resolve().parents[2]
MODELO_SQL_PADRAO = RAIZ_ETL.parent / "ModeloLogicoHorizon.sql"
PASTA_SQL = Path(__file__).resolve().parent / "sql"
AJUSTES_SQL = PASTA_SQL / "ajustes_postgres.sql"
DADOS_INICIAIS_SQL = PASTA_SQL / "dados_iniciais.sql"
TOTAL_TABELAS_MODELO = 33


def traduzir_modelo(ddl: str) -> str:
    """Troca tipos do modelo que o PostgreSQL não conhece (``DATETIME``)."""
    return re.sub(r"\bDATETIME\b", "TIMESTAMP", ddl, flags=re.IGNORECASE)


def caminho_modelo() -> Path:
    """Caminho do ModeloLogicoHorizon.sql (``HORIZON_MODELO_SQL`` sobrepõe o padrão)."""
    return Path(os.getenv("HORIZON_MODELO_SQL") or MODELO_SQL_PADRAO)


def aplicar_schema(
    conexao: psycopg.Connection,
    schema: str = "public",
    modelo_sql: Optional[Path] = None,
) -> None:
    """Apaga e recria ``schema`` com o modelo, os ajustes e os dados iniciais."""
    ddl = traduzir_modelo(Path(modelo_sql or caminho_modelo()).read_text("utf-8"))
    nome_schema = sql.Identifier(schema)

    with conexao.transaction():
        with conexao.cursor() as cursor:
            cursor.execute(
                sql.SQL("DROP SCHEMA IF EXISTS {} CASCADE").format(nome_schema)
            )
            cursor.execute(sql.SQL("CREATE SCHEMA {}").format(nome_schema))
            cursor.execute(sql.SQL("SET LOCAL search_path TO {}").format(nome_schema))
            cursor.execute(ddl)
            cursor.execute(AJUSTES_SQL.read_text("utf-8"))
            cursor.execute(DADOS_INICIAIS_SQL.read_text("utf-8"))


def listar_tabelas(conexao: psycopg.Connection, schema: str = "public") -> List[str]:
    """Tabelas existentes em ``schema``, em ordem alfabética."""
    with conexao.cursor() as cursor:
        cursor.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = %s AND table_type = 'BASE TABLE'
            ORDER BY table_name
            """,
            (schema,),
        )
        return [linha[0] for linha in cursor.fetchall()]


def url_banco() -> str:
    """URL do banco Horizon, lida de ``HORIZON_DATABASE_URL``."""
    url = os.getenv("HORIZON_DATABASE_URL")
    if not url:
        raise RuntimeError(
            "HORIZON_DATABASE_URL não definida. Copie o bloco do banco do Horizon "
            "de .env.example para .env."
        )
    return url


def main() -> int:
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass

    with psycopg.connect(url_banco()) as conexao:
        aplicar_schema(conexao)
        tabelas = listar_tabelas(conexao)

    logger.info(
        "Schema do Horizon aplicado: {} tabelas em public (modelo: {}).",
        len(tabelas),
        caminho_modelo(),
    )
    if len(tabelas) != TOTAL_TABELAS_MODELO:
        logger.error(
            "Esperadas {} tabelas, encontradas {}.",
            TOTAL_TABELAS_MODELO,
            len(tabelas),
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
