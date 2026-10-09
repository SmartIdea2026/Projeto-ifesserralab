import pytest

from src.adapters.sinks.postgres.repositorio_formacoes import (
    RepositorioFormacoesPostgres,
)
from src.adapters.sinks.postgres.repositorio_organizacoes import (
    RepositorioOrganizacoesPostgres,
)
from src.adapters.sinks.postgres.repositorio_pessoas import RepositorioPessoasPostgres


@pytest.fixture
def repositorio(conexao_horizon):
    return RepositorioFormacoesPostgres(conexao_horizon)


@pytest.fixture
def pessoa_e_instituicao(conexao_horizon):
    pessoa = RepositorioPessoasPostgres(conexao_horizon).criar("Helena")
    ufes = RepositorioOrganizacoesPostgres(conexao_horizon).garantir_organizacao(
        "Universidade Federal do Espírito Santo", "instituicao_ensino", "UFES"
    )
    return pessoa, ufes


def _contar(conexao, tabela):
    with conexao.cursor() as cursor:
        cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
        return cursor.fetchone()[0]


def test_tipo_de_formacao_e_casado_por_nome_normalizado(repositorio, conexao_horizon):
    doutorado = repositorio.garantir_tipo_formacao("Doutorado")

    assert repositorio.garantir_tipo_formacao("DOUTORADO") == doutorado
    assert repositorio.garantir_tipo_formacao("Mestrado") != doutorado
    assert _contar(conexao_horizon, "tipos_formacao") == 2


def test_formacao_igual_nao_e_gravada_de_novo(
    repositorio, pessoa_e_instituicao, conexao_horizon
):
    pessoa, ufes = pessoa_e_instituicao
    doutorado = repositorio.garantir_tipo_formacao("Doutorado")

    primeira, criada = repositorio.adicionar_formacao(
        pessoa, doutorado, ufes, "Informática", 2015, None, None
    )
    repetida, criada_de_novo = repositorio.adicionar_formacao(
        pessoa, doutorado, ufes, "Informática", 2015, None, None
    )
    concluida, criada_concluida = repositorio.adicionar_formacao(
        pessoa, doutorado, ufes, "Informática", 2015, 2019, "Tese X"
    )

    assert (criada, criada_de_novo, criada_concluida) == (True, False, True)
    assert repetida == primeira
    assert concluida != primeira
    assert _contar(conexao_horizon, "formacoes_academicas") == 2


def test_formacao_aceita_valores_genericos_do_etl(repositorio, pessoa_e_instituicao):
    pessoa, ufes = pessoa_e_instituicao
    desconhecido = repositorio.garantir_tipo_formacao("Unknown")

    _, criada = repositorio.adicionar_formacao(
        pessoa, desconhecido, ufes, "Untitled", 0, None, None
    )

    assert criada is True


def test_formacao_sem_curso_ou_ano_e_recusada(repositorio, pessoa_e_instituicao):
    pessoa, ufes = pessoa_e_instituicao
    tipo = repositorio.garantir_tipo_formacao("Mestrado")

    with pytest.raises(ValueError):
        repositorio.adicionar_formacao(pessoa, tipo, ufes, None, 2015, None, None)
    with pytest.raises(ValueError):
        repositorio.adicionar_formacao(pessoa, tipo, ufes, "Física", None, None, None)


def test_orientadores_da_formacao(repositorio, pessoa_e_instituicao, conexao_horizon):
    pessoa, ufes = pessoa_e_instituicao
    pessoas = RepositorioPessoasPostgres(conexao_horizon)
    orientador = pessoas.criar("Prof. Ivo")
    coorientador = pessoas.criar("Profa. Júlia")
    formacao, _ = repositorio.adicionar_formacao(
        pessoa,
        repositorio.garantir_tipo_formacao("Mestrado"),
        ufes,
        "Computação",
        2018,
        2020,
        "Dissertação Y",
    )

    assert repositorio.adicionar_orientador(formacao, orientador, "orientador")
    assert repositorio.adicionar_orientador(formacao, coorientador, "coorientador")
    assert not repositorio.adicionar_orientador(formacao, orientador, "coorientador")
    with pytest.raises(ValueError):
        repositorio.adicionar_orientador(formacao, pessoa, "banca")
    assert _contar(conexao_horizon, "orientadores_formacao") == 2
