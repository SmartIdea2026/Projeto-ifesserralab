"""Testes do schema do banco Horizon no PostgreSQL.

Os testes de banco aplicam o schema num schema temporário (``teste_esquema_*``),
apagado no fim, e são pulados quando ``HORIZON_DATABASE_URL`` não está definida
ou o servidor não responde (suba com ``make horizon-db-up``).
"""

import os
import re
import uuid

import pytest

from src.db.esquema_horizon import (
    AJUSTES_SQL,
    TOTAL_TABELAS_MODELO,
    aplicar_schema,
    caminho_modelo,
    listar_tabelas,
    traduzir_modelo,
)


def _modelo() -> str:
    return caminho_modelo().read_text("utf-8")


def _tabelas_do_modelo() -> set[str]:
    return set(re.findall(r"CREATE TABLE (\w+) \(", _modelo()))


def _tabelas_com_id_proprio() -> set[str]:
    """Tabelas com ``id`` próprio; as que herdam o id da tabela-mãe ficam de fora."""
    modelo = _modelo()
    com_id = set(re.findall(r"CREATE TABLE (\w+) \(\s*id INTEGER PRIMARY KEY", modelo))
    herdam_id = set(
        re.findall(r"ALTER TABLE (\w+) ADD CONSTRAINT \w+\s+FOREIGN KEY \(id\)", modelo)
    )
    return com_id - herdam_id


def test_traduzir_modelo_troca_datetime_por_timestamp():
    ddl = "atualizado_em DATETIME NOT NULL,\n    criado_em datetime"

    assert traduzir_modelo(ddl) == (
        "atualizado_em TIMESTAMP NOT NULL,\n    criado_em TIMESTAMP"
    )


def test_traduzir_modelo_preserva_identificadores_que_contem_datetime():
    assert traduzir_modelo("coluna_datetime INTEGER") == "coluna_datetime INTEGER"


def test_modelo_tem_33_tabelas():
    assert len(_tabelas_do_modelo()) == TOTAL_TABELAS_MODELO


def test_ajustes_geram_id_em_toda_tabela_com_id_proprio():
    com_identity = set(
        re.findall(
            r"ALTER TABLE (\w+) ALTER COLUMN id ADD GENERATED",
            AJUSTES_SQL.read_text("utf-8"),
        )
    )

    assert com_identity == _tabelas_com_id_proprio()
    assert not com_identity & {"unidades_organizacionais", "grupos_pesquisa", "artigos"}


@pytest.fixture
def banco():
    """Conexão com o banco Horizon e um nome de schema temporário."""
    psycopg = pytest.importorskip("psycopg")
    from psycopg import sql

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

    schema = f"teste_esquema_{uuid.uuid4().hex[:8]}"
    try:
        yield conexao, schema
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


def _consultar(conexao, consulta, parametros=()):
    with conexao.cursor() as cursor:
        cursor.execute(consulta, parametros)
        return cursor.fetchall()


def test_aplicar_schema_cria_as_33_tabelas_do_modelo(banco):
    conexao, schema = banco

    aplicar_schema(conexao, schema=schema)

    assert set(listar_tabelas(conexao, schema)) == _tabelas_do_modelo()


def test_aplicar_schema_e_repetivel(banco):
    conexao, schema = banco

    aplicar_schema(conexao, schema=schema)
    aplicar_schema(conexao, schema=schema)

    assert len(listar_tabelas(conexao, schema)) == TOTAL_TABELAS_MODELO
    tipos = _consultar(conexao, f'SELECT COUNT(*) FROM "{schema}".tipos_iniciativa')
    assert tipos == [(4,)]


def test_atualizado_em_vira_timestamp(banco):
    conexao, schema = banco

    aplicar_schema(conexao, schema=schema)

    tipo = _consultar(
        conexao,
        """
        SELECT data_type FROM information_schema.columns
        WHERE table_schema = %s AND table_name = 'perfis_lattes'
          AND column_name = 'atualizado_em'
        """,
        (schema,),
    )
    assert tipo == [("timestamp without time zone",)]


def test_ids_proprios_sao_gerados_pelo_banco(banco):
    conexao, schema = banco

    aplicar_schema(conexao, schema=schema)

    com_identity = _consultar(
        conexao,
        """
        SELECT table_name FROM information_schema.columns
        WHERE table_schema = %s AND column_name = 'id' AND is_identity = 'YES'
        """,
        (schema,),
    )
    assert {linha[0] for linha in com_identity} == _tabelas_com_id_proprio()

    novo_id = _consultar(
        conexao,
        f"INSERT INTO \"{schema}\".pessoas (nome) VALUES ('Pessoa Teste') RETURNING id",
    )
    assert novo_id[0][0] is not None


def test_titulos_e_nomes_aceitam_mais_de_255_caracteres(banco):
    conexao, schema = banco

    aplicar_schema(conexao, schema=schema)

    titulo_longo = "T" * 400
    linha = _consultar(
        conexao,
        f"""
        INSERT INTO "{schema}".producoes (tipo_producao_id, titulo, ano)
        SELECT id, %s, 2024 FROM "{schema}".tipos_producao WHERE nome = 'artigo'
        RETURNING length(titulo)
        """,
        (titulo_longo,),
    )
    assert linha == [(400,)]


def test_bolsa_e_unica_por_nome_e_financiador(banco):
    errors = pytest.importorskip("psycopg.errors")
    conexao, schema = banco

    aplicar_schema(conexao, schema=schema)

    organizacoes = _consultar(
        conexao,
        f"""
        INSERT INTO "{schema}".organizacoes (nome, tipo)
        VALUES ('Fapes', 'fomento'), ('CNPq', 'fomento')
        RETURNING id
        """,
    )
    fapes, cnpq = (linha[0] for linha in organizacoes)
    inserir_bolsa = (
        f'INSERT INTO "{schema}".bolsas (nome, valor, financiador_id) '
        "VALUES ('PIBIC', 700, %s)"
    )

    with conexao.cursor() as cursor:
        cursor.execute(inserir_bolsa, (fapes,))
        cursor.execute(inserir_bolsa, (cnpq,))
        with pytest.raises(errors.UniqueViolation):
            cursor.execute(inserir_bolsa, (fapes,))


def test_dados_iniciais_dos_tipos(banco):
    conexao, schema = banco

    aplicar_schema(conexao, schema=schema)

    tipos_iniciativa = _consultar(
        conexao, f'SELECT nome FROM "{schema}".tipos_iniciativa ORDER BY nome'
    )
    tipos_producao = _consultar(
        conexao, f'SELECT nome FROM "{schema}".tipos_producao ORDER BY nome'
    )
    assert [linha[0] for linha in tipos_iniciativa] == [
        "orientacao",
        "projeto_desenvolvimento",
        "projeto_extensao",
        "projeto_pesquisa",
    ]
    assert [linha[0] for linha in tipos_producao] == ["artigo"]


def test_dados_iniciais_do_ifes_e_dos_papeis_fixos(banco):
    from src.core.ports.repositorio_organizacoes import PAPEIS_FIXOS

    conexao, schema = banco

    aplicar_schema(conexao, schema=schema)

    organizacoes = _consultar(
        conexao, f'SELECT nome, sigla, tipo FROM "{schema}".organizacoes'
    )
    papeis = _consultar(conexao, f'SELECT escopo, nome FROM "{schema}".papeis')
    assert organizacoes == [
        ("Instituto Federal do Espírito Santo", "IFES", "instituicao_ensino")
    ]
    assert sorted(papeis) == sorted(
        (escopo, nome) for escopo, nomes in PAPEIS_FIXOS.items() for nome in nomes
    )
