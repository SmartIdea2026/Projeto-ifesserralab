from datetime import date

import pytest

from src.adapters.sinks.postgres.repositorio_organizacoes import (
    RepositorioOrganizacoesPostgres,
)
from src.adapters.sinks.postgres.repositorio_pessoas import RepositorioPessoasPostgres
from src.core.ports.repositorio_organizacoes import PAPEIS_FIXOS


@pytest.fixture
def repositorio(conexao_horizon):
    return RepositorioOrganizacoesPostgres(conexao_horizon)


def _contar(conexao, consulta):
    with conexao.cursor() as cursor:
        cursor.execute(consulta)
        return cursor.fetchone()[0]


def test_ifes_vem_dos_dados_iniciais(repositorio):
    ifes = repositorio.ifes_id()

    assert (
        repositorio.garantir_organizacao("IFES", "instituicao_ensino", "IFES") == ifes
    )
    assert (
        repositorio.garantir_organizacao(
            "Instituto Federal do Espirito Santo", "instituicao_ensino"
        )
        == ifes
    )


def test_organizacao_e_casada_por_nome_normalizado(repositorio, conexao_horizon):
    fapes = repositorio.garantir_organizacao("FAPES", "fomento")

    assert repositorio.garantir_organizacao("fapes", "fomento") == fapes
    assert repositorio.garantir_organizacao("Fapes.", "empresa") == fapes
    assert _contar(conexao_horizon, "SELECT COUNT(*) FROM organizacoes") == 2


def test_organizacao_com_tipo_unidade_ou_invalido_e_recusada(repositorio):
    with pytest.raises(ValueError):
        repositorio.garantir_organizacao("Campus Serra", "unidade")
    with pytest.raises(ValueError):
        repositorio.garantir_organizacao("Petrobras", "privada")


def test_unidade_fica_sob_o_ifes_e_nao_duplica(repositorio, conexao_horizon):
    ifes = repositorio.ifes_id()

    serra = repositorio.garantir_unidade("Campus Serra", ifes)

    assert repositorio.garantir_unidade("CAMPUS SERRA", ifes) == serra
    assert repositorio.garantir_unidade("Campus Vitória", ifes) != serra
    with conexao_horizon.cursor() as cursor:
        cursor.execute(
            "SELECT o.tipo, u.organizacao_pai_id FROM organizacoes o "
            "JOIN unidades_organizacionais u ON u.id = o.id WHERE o.id = %s",
            (serra,),
        )
        assert cursor.fetchone() == ("unidade", ifes)


def test_unidade_nao_e_confundida_com_organizacao(repositorio):
    ifes = repositorio.ifes_id()
    serra = repositorio.garantir_unidade("Serra", ifes)

    assert repositorio.garantir_organizacao("Serra", "empresa") != serra


def test_papeis_fixos_existem_e_nao_aceitam_outros(repositorio, conexao_horizon):
    for escopo, nomes in PAPEIS_FIXOS.items():
        for nome in nomes:
            repositorio.garantir_papel(nome, escopo)
    total_fixos = sum(len(nomes) for nomes in PAPEIS_FIXOS.values())

    assert _contar(conexao_horizon, "SELECT COUNT(*) FROM papeis") == total_fixos
    with pytest.raises(ValueError):
        repositorio.garantir_papel("Coordinator", "participacao")
    with pytest.raises(ValueError):
        repositorio.garantir_papel("lider", "outro")


def test_papel_de_vinculo_e_criado_sob_demanda(repositorio):
    servidor = repositorio.garantir_papel("Servidor Público", "vinculo")

    assert repositorio.garantir_papel("servidor publico", "vinculo") == servidor
    assert repositorio.garantir_papel("Celetista", "vinculo") != servidor


def test_vinculo_nao_duplica_por_organizacao_papel_e_inicio(
    repositorio, conexao_horizon
):
    pessoa = RepositorioPessoasPostgres(conexao_horizon).criar("Gabriela")
    ifes = repositorio.ifes_id()
    servidor = repositorio.garantir_papel("Servidor Público", "vinculo")

    assert repositorio.adicionar_vinculo(pessoa, ifes, servidor, date(2010, 1, 1), None)
    assert not repositorio.adicionar_vinculo(
        pessoa, ifes, servidor, date(2010, 1, 1), date(2020, 12, 31)
    )
    assert repositorio.adicionar_vinculo(pessoa, ifes, servidor, None, None)
    assert not repositorio.adicionar_vinculo(pessoa, ifes, servidor, None, None)
    assert _contar(conexao_horizon, "SELECT COUNT(*) FROM vinculos") == 2


def test_listar_unidades_do_ifes(repositorio):
    ifes = repositorio.ifes_id()
    serra = repositorio.garantir_unidade("Campus Serra", ifes)
    vitoria = repositorio.garantir_unidade("Campus Vitória", ifes)
    repositorio.garantir_organizacao("Campus Serra Empresa", "empresa")

    assert repositorio.listar_unidades(ifes) == [
        (serra, "Campus Serra"),
        (vitoria, "Campus Vitória"),
    ]
