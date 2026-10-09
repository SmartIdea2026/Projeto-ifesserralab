import psycopg

from src.db.esquema_horizon import url_banco


def abrir_conexao() -> psycopg.Connection:
    """Conexão com o banco Horizon (``HORIZON_DATABASE_URL``).

    Em autocommit: as transações são abertas explicitamente, por passo e por
    registro, pelo contexto de carga.
    """
    return psycopg.connect(url_banco(), autocommit=True)
