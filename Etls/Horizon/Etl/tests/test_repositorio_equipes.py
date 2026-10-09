from datetime import date

import pytest

from src.adapters.sinks.postgres.repositorio_equipes import RepositorioEquipesPostgres
from src.adapters.sinks.postgres.repositorio_organizacoes import (
    RepositorioOrganizacoesPostgres,
)
from src.adapters.sinks.postgres.repositorio_pessoas import RepositorioPessoasPostgres


@pytest.fixture
def repositorio(conexao_horizon):
    return RepositorioEquipesPostgres(conexao_horizon)


@pytest.fixture
def organizacoes(conexao_horizon):
    return RepositorioOrganizacoesPostgres(conexao_horizon)


@pytest.fixture
def campus_serra(organizacoes):
    return organizacoes.garantir_unidade("Campus Serra", organizacoes.ifes_id())


def _contar(conexao, tabela):
    with conexao.cursor() as cursor:
        cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
        return cursor.fetchone()[0]


def test_grupo_e_criado_como_equipe_e_grupo_de_pesquisa(
    repositorio, campus_serra, conexao_horizon
):
    grupo, criado = repositorio.garantir_grupo(
        "Núcleo de Pesquisa em Computação", campus_serra, sigla="NPC"
    )

    assert criado is True
    assert _contar(conexao_horizon, "equipes") == 1
    assert _contar(conexao_horizon, "grupos_pesquisa") == 1
    [cadastrado] = repositorio.listar_grupos()
    assert cadastrado.id == grupo
    assert cadastrado.organizacao_id == campus_serra
    assert cadastrado.url_cnpq is None


def test_grupo_existente_e_devolvido_sem_mudanca(repositorio, campus_serra):
    grupo, _ = repositorio.garantir_grupo("Grupo de Robótica", campus_serra)

    mesmo, criado = repositorio.garantir_grupo(
        "GRUPO DE ROBOTICA", campus_serra, sigla="GR", descricao="outra"
    )

    assert (mesmo, criado) == (grupo, False)
    assert repositorio.buscar_grupo_por_nome("grupo de robótica") == grupo
    assert repositorio.buscar_grupo_por_nome("Outro grupo") is None


def test_url_cnpq_repetida_nao_e_gravada_em_outro_grupo(repositorio, campus_serra):
    url = "http://dgp.cnpq.br/dgp/espelhogrupo/123"
    primeiro, _ = repositorio.garantir_grupo("Grupo A", campus_serra)
    segundo, _ = repositorio.garantir_grupo("Grupo B", campus_serra)

    assert repositorio.definir_url_cnpq(primeiro, url) is True
    assert repositorio.definir_url_cnpq(primeiro, url) is True
    assert repositorio.definir_url_cnpq(segundo, url) is False
    assert repositorio.definir_url_cnpq(segundo, "") is False
    urls = {grupo.id: grupo.url_cnpq for grupo in repositorio.listar_grupos()}
    assert urls == {primeiro: url, segundo: None}


def test_atualizar_equipe_e_data_de_formacao(
    repositorio, campus_serra, conexao_horizon
):
    grupo, _ = repositorio.garantir_grupo("Grupo C", campus_serra, descricao="antiga")

    repositorio.atualizar_equipe(grupo, nome="Grupo C (CNPq)")
    repositorio.atualizar_equipe(grupo, descricao="Repercussões do grupo")
    repositorio.definir_data_inicio_grupo(grupo, date(2014, 4, 1))

    with conexao_horizon.cursor() as cursor:
        cursor.execute(
            "SELECT e.nome, e.descricao, g.data_inicio FROM equipes e "
            "JOIN grupos_pesquisa g ON g.id = e.id"
        )
        assert cursor.fetchone() == (
            "Grupo C (CNPq)",
            "Repercussões do grupo",
            date(2014, 4, 1),
        )


def test_membro_pode_ter_mais_de_um_papel_sem_repetir(
    repositorio, organizacoes, campus_serra, conexao_horizon
):
    grupo, _ = repositorio.garantir_grupo("Grupo D", campus_serra)
    pessoa = RepositorioPessoasPostgres(conexao_horizon).criar("Lia")
    lider = organizacoes.garantir_papel("lider", "equipe")
    pesquisador = organizacoes.garantir_papel("pesquisador", "equipe")

    assert repositorio.adicionar_membro(grupo, pessoa, lider, None, None)
    assert repositorio.adicionar_membro(
        grupo, pessoa, pesquisador, date(2015, 3, 1), None
    )
    assert not repositorio.adicionar_membro(
        grupo, pessoa, lider, date(2016, 1, 1), None
    )
    assert _contar(conexao_horizon, "membros_equipe") == 2


def test_fim_do_membro_egresso(
    repositorio, organizacoes, campus_serra, conexao_horizon
):
    grupo, _ = repositorio.garantir_grupo("Grupo E", campus_serra)
    pessoa = RepositorioPessoasPostgres(conexao_horizon).criar("Marcos")
    estudante = organizacoes.garantir_papel("estudante", "equipe")
    repositorio.adicionar_membro(grupo, pessoa, estudante, date(2019, 2, 1), None)

    assert repositorio.definir_fim_membro(grupo, pessoa, estudante, date(2021, 12, 1))
    assert not repositorio.definir_fim_membro(
        grupo, pessoa, estudante, date(2021, 12, 1)
    )
    with conexao_horizon.cursor() as cursor:
        cursor.execute("SELECT data_inicio, data_fim FROM membros_equipe")
        assert cursor.fetchone() == (date(2019, 2, 1), date(2021, 12, 1))
