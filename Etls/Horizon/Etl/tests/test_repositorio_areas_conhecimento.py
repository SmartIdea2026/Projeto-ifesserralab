import pytest

from src.adapters.sinks.postgres.repositorio_areas_conhecimento import (
    RepositorioAreasConhecimentoPostgres,
)
from src.adapters.sinks.postgres.repositorio_equipes import RepositorioEquipesPostgres
from src.adapters.sinks.postgres.repositorio_organizacoes import (
    RepositorioOrganizacoesPostgres,
)
from src.adapters.sinks.postgres.repositorio_pessoas import RepositorioPessoasPostgres


@pytest.fixture
def repositorio(conexao_horizon):
    return RepositorioAreasConhecimentoPostgres(conexao_horizon)


def _contar(conexao, tabela):
    with conexao.cursor() as cursor:
        cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
        return cursor.fetchone()[0]


def test_area_e_casada_por_nome_normalizado(repositorio, conexao_horizon):
    educacao = repositorio.garantir_area("Educação")

    assert repositorio.garantir_area("EDUCACAO") == educacao
    assert repositorio.garantir_area("  educação ") == educacao
    assert repositorio.garantir_area("Computação") != educacao
    assert _contar(conexao_horizon, "areas_conhecimento") == 2


def test_area_sem_nome_e_recusada(repositorio):
    with pytest.raises(ValueError):
        repositorio.garantir_area("  ")


def test_ligacoes_com_equipe_e_pessoa_nao_repetem(repositorio, conexao_horizon):
    organizacoes = RepositorioOrganizacoesPostgres(conexao_horizon)
    campus = organizacoes.garantir_unidade("Campus Serra", organizacoes.ifes_id())
    grupo, _ = RepositorioEquipesPostgres(conexao_horizon).garantir_grupo(
        "Grupo F", campus
    )
    pessoa = RepositorioPessoasPostgres(conexao_horizon).criar("Nina")
    area = repositorio.garantir_area("Engenharia de Software")

    assert repositorio.ligar_area_equipe(grupo, area)
    assert not repositorio.ligar_area_equipe(grupo, area)
    assert repositorio.ligar_area_pessoa(pessoa, area)
    assert not repositorio.ligar_area_pessoa(pessoa, area)
    assert _contar(conexao_horizon, "areas_conhecimento_equipe") == 1
    assert _contar(conexao_horizon, "areas_conhecimento_pessoa") == 1
