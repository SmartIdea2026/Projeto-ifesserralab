from datetime import date, datetime
from decimal import Decimal

import pytest

from src.adapters.sinks.postgres.repositorio_areas_conhecimento import (
    RepositorioAreasConhecimentoPostgres,
)
from src.adapters.sinks.postgres.repositorio_equipes import RepositorioEquipesPostgres
from src.adapters.sinks.postgres.repositorio_iniciativas import (
    RepositorioIniciativasPostgres,
)
from src.adapters.sinks.postgres.repositorio_organizacoes import (
    RepositorioOrganizacoesPostgres,
)
from src.adapters.sinks.postgres.repositorio_pessoas import RepositorioPessoasPostgres


@pytest.fixture
def repositorio(conexao_horizon):
    return RepositorioIniciativasPostgres(conexao_horizon)


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


def test_criar_e_buscar_iniciativa(repositorio, campus_serra):
    projeto = repositorio.criar(
        "Projeto Alfa",
        "projeto_pesquisa",
        campus_serra,
        "em_andamento",
        descricao="Resumo",
        data_inicio=datetime(2024, 3, 1, 10, 30),
        data_fim=date(2025, 2, 28),
    )

    encontrada = repositorio.buscar(projeto)
    assert encontrada.nome == "Projeto Alfa"
    assert encontrada.tipo == "projeto_pesquisa"
    assert encontrada.organizacao_id == campus_serra
    assert (encontrada.data_inicio, encontrada.data_fim) == (
        date(2024, 3, 1),
        date(2025, 2, 28),
    )
    assert repositorio.buscar(projeto + 999) is None


def test_tipo_e_situacao_invalidos_sao_recusados(repositorio, campus_serra):
    with pytest.raises(ValueError):
        repositorio.criar("X", "Research Project", campus_serra, "em_andamento")
    with pytest.raises(ValueError):
        repositorio.criar("X", "projeto_pesquisa", campus_serra, "Active")


def test_buscar_por_nome_e_listar_por_tipo(repositorio, campus_serra):
    projeto = repositorio.criar(
        "Mesmo título", "projeto_pesquisa", campus_serra, "concluida"
    )
    orientacao = repositorio.criar(
        "Mesmo título", "orientacao", campus_serra, "em_andamento"
    )

    assert [i.id for i in repositorio.buscar_por_nome("Mesmo título")] == [
        projeto,
        orientacao,
    ]
    assert [
        i.id for i in repositorio.buscar_por_nome("Mesmo título", "orientacao")
    ] == [orientacao]
    assert [i.id for i in repositorio.listar("projeto_pesquisa")] == [projeto]
    assert len(repositorio.listar()) == 2


def test_atualizar_so_os_campos_informados(repositorio, campus_serra, organizacoes):
    projeto = repositorio.criar(
        "Projeto Beta", "projeto_pesquisa", campus_serra, "desconhecida", descricao="a"
    )

    repositorio.atualizar(
        projeto,
        {
            "situacao": "concluida",
            "data_fim": datetime(2023, 12, 31),
            "organizacao_id": organizacoes.ifes_id(),
        },
    )

    atual = repositorio.buscar(projeto)
    assert (atual.situacao, atual.data_fim, atual.descricao) == (
        "concluida",
        date(2023, 12, 31),
        "a",
    )
    assert atual.organizacao_id == organizacoes.ifes_id()
    with pytest.raises(ValueError):
        repositorio.atualizar(projeto, {"situacao": "Concluded"})
    with pytest.raises(ValueError):
        repositorio.atualizar(projeto, {"tipo_iniciativa_id": 1})


def test_hierarquia_e_periodo_dos_filhos(repositorio, campus_serra):
    pai = repositorio.criar(
        "Projeto Pai", "projeto_pesquisa", campus_serra, "desconhecida"
    )
    filho_a = repositorio.criar(
        "Plano A",
        "orientacao",
        campus_serra,
        "concluida",
        data_inicio=date(2021, 3, 1),
        data_fim=date(2022, 2, 28),
    )
    filho_b = repositorio.criar(
        "Plano B",
        "orientacao",
        campus_serra,
        "em_andamento",
        data_inicio=date(2022, 3, 1),
        data_fim=date(2026, 2, 28),
    )

    repositorio.definir_pai(filho_a, pai)
    repositorio.definir_pai(filho_b, pai)
    repositorio.definir_pai(filho_b, pai)

    assert repositorio.periodos_dos_filhos() == {
        pai: (date(2021, 3, 1), date(2026, 2, 28))
    }
    with pytest.raises(ValueError):
        repositorio.definir_pai(pai, pai)


def test_participantes_e_bolsa_do_orientando(
    repositorio, organizacoes, campus_serra, conexao_horizon
):
    pessoas = RepositorioPessoasPostgres(conexao_horizon)
    aluno = pessoas.criar("Olívia")
    orientador = pessoas.criar("Prof. Paulo")
    orientacao = repositorio.criar(
        "Plano C", "orientacao", campus_serra, "em_andamento"
    )
    fapes = organizacoes.garantir_organizacao("FAPES", "fomento")

    participante, criado = repositorio.adicionar_participante(
        orientacao,
        aluno,
        organizacoes.garantir_papel("orientando", "participacao"),
        date(2024, 3, 1),
        None,
    )
    repetido, criado_de_novo = repositorio.adicionar_participante(
        orientacao,
        aluno,
        organizacoes.garantir_papel("orientando", "participacao"),
        date(2024, 3, 1),
        None,
    )
    repositorio.adicionar_participante(
        orientacao,
        orientador,
        organizacoes.garantir_papel("orientador", "participacao"),
        None,
        None,
    )
    pibic = repositorio.garantir_bolsa("PIBIC", fapes, Decimal("700.00"))
    repositorio.definir_bolsa_participante(participante, pibic)
    repositorio.definir_bolsa_participante(participante, pibic)

    assert (criado, criado_de_novo, repetido) == (True, False, participante)
    assert _contar(conexao_horizon, "participantes_iniciativa") == 2
    assert _contar(conexao_horizon, "bolsas_participante") == 1


def test_bolsa_unica_por_nome_e_financiador(repositorio, organizacoes, conexao_horizon):
    fapes = organizacoes.garantir_organizacao("FAPES", "fomento")
    cnpq = organizacoes.garantir_organizacao("CNPq", "fomento")

    pibic_fapes = repositorio.garantir_bolsa("PIBIC", fapes, 700)

    assert repositorio.garantir_bolsa(" pibic ", fapes, 999) == pibic_fapes
    assert repositorio.garantir_bolsa("PIBIC", cnpq, 0.0) != pibic_fapes
    with conexao_horizon.cursor() as cursor:
        cursor.execute("SELECT valor FROM bolsas WHERE id = %s", (pibic_fapes,))
        assert cursor.fetchone()[0] == Decimal("700.00")
    with pytest.raises(ValueError):
        repositorio.garantir_bolsa("PIBIC", fapes, None)


def test_ligacoes_com_equipe_organizacao_e_area(
    repositorio, organizacoes, campus_serra, conexao_horizon
):
    projeto = repositorio.criar(
        "Projeto Gama", "projeto_pesquisa", campus_serra, "em_andamento"
    )
    grupo, _ = RepositorioEquipesPostgres(conexao_horizon).garantir_grupo(
        "Grupo G", campus_serra
    )
    prefeitura = organizacoes.garantir_organizacao(
        "Prefeitura Municipal da Serra", "orgao_publico"
    )
    areas = RepositorioAreasConhecimentoPostgres(conexao_horizon)
    area = areas.garantir_area("Cidades Inteligentes")

    assert repositorio.ligar_equipe(projeto, grupo, "executor")
    assert not repositorio.ligar_equipe(projeto, grupo, "parceiro")
    assert repositorio.ligar_organizacao(projeto, prefeitura, "demandante")
    assert repositorio.ligar_organizacao(projeto, prefeitura, "parceira")
    assert not repositorio.ligar_organizacao(projeto, prefeitura, "demandante")
    assert areas.ligar_area_iniciativa(projeto, area)
    assert not areas.ligar_area_iniciativa(projeto, area)
    with pytest.raises(ValueError):
        repositorio.ligar_equipe(projeto, grupo, "lider")
    with pytest.raises(ValueError):
        repositorio.ligar_organizacao(projeto, prefeitura, "patrocinadora")
    assert _contar(conexao_horizon, "equipes_iniciativa") == 1
    assert _contar(conexao_horizon, "organizacoes_iniciativa") == 2
    assert _contar(conexao_horizon, "areas_conhecimento_iniciativa") == 1
