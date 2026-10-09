import os
import uuid

import pytest


@pytest.fixture
def conexao_horizon():
    """Conexão com o banco Horizon apontada para um schema temporário já criado.

    O schema (``teste_repo_*``) recebe ModeloLogicoHorizon.sql com os ajustes e é
    apagado no fim. Pulado quando ``HORIZON_DATABASE_URL`` não está definida ou o
    servidor não responde (suba com ``make horizon-db-up``).
    """
    psycopg = pytest.importorskip("psycopg")
    from psycopg import sql

    from src.db.esquema_horizon import aplicar_schema

    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass

    url = os.getenv("HORIZON_DATABASE_URL")
    if not url:
        pytest.skip("HORIZON_DATABASE_URL não definida")
    try:
        conexao = psycopg.connect(url, connect_timeout=3)
    except psycopg.OperationalError as exc:
        pytest.skip(f"banco do Horizon indisponível: {exc}")

    schema = f"teste_repo_{uuid.uuid4().hex[:8]}"
    aplicar_schema(conexao, schema=schema)
    with conexao.cursor() as cursor:
        cursor.execute(sql.SQL("SET search_path TO {}").format(sql.Identifier(schema)))
    conexao.commit()

    try:
        yield conexao
    finally:
        conexao.rollback()
        with conexao.cursor() as cursor:
            cursor.execute(
                sql.SQL("DROP SCHEMA IF EXISTS {} CASCADE").format(
                    sql.Identifier(schema)
                )
            )
        conexao.commit()
        conexao.close()
