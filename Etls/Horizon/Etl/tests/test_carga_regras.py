from datetime import date, datetime

import pytest

from src.core.logic.carga.regras import (
    data_atualizacao_lattes,
    fim_do_ano,
    inicio_do_ano,
    nivel_proficiencia,
    situacao_iniciativa,
    situacao_pela_data,
)

HOJE = date(2026, 6, 1)


@pytest.mark.parametrize(
    "status, situacao",
    [
        ("Active", "em_andamento"),
        ("In Progress", "em_andamento"),
        ("Concluded", "concluida"),
        ("Cancelled", "cancelada"),
        ("Unknown", "desconhecida"),
        ("", "desconhecida"),
        (None, "desconhecida"),
        ("Em análise", "desconhecida"),
    ],
)
def test_situacao_iniciativa_a_partir_do_status(status, situacao):
    assert situacao_iniciativa(status, hoje=HOJE) == situacao


def test_variacao_de_aprovado_segue_a_regra_da_data():
    assert (
        situacao_iniciativa("Aprovado com ressalvas", datetime(2025, 1, 31), HOJE)
        == "concluida"
    )
    assert (
        situacao_iniciativa("APROVADO c/ ajustes", date(2027, 1, 31), HOJE)
        == "em_andamento"
    )
    assert situacao_iniciativa("Aprovado com ressalvas", None, HOJE) == "em_andamento"


def test_situacao_pela_data():
    assert situacao_pela_data(date(2026, 5, 31), HOJE) == "concluida"
    assert situacao_pela_data(date(2026, 6, 1), HOJE) == "em_andamento"
    assert situacao_pela_data(None, HOJE) == "em_andamento"


@pytest.mark.parametrize(
    "termo, nivel",
    [
        ("Bem", "alto"),
        ("razoavelmente", "medio"),
        (" Pouco ", "basico"),
        ("Nenhum", "nao_se_aplica"),
        ("", "nao_se_aplica"),
        (None, "nao_se_aplica"),
    ],
)
def test_nivel_proficiencia(termo, nivel):
    assert nivel_proficiencia(termo) == nivel


def test_ano_vira_data():
    assert inicio_do_ano(2020) == date(2020, 1, 1)
    assert fim_do_ano(2020) == date(2020, 12, 31)
    assert inicio_do_ano(None) is None
    assert fim_do_ano(0) is None


@pytest.mark.parametrize(
    "valor, esperado",
    [
        ("15/03/2025", datetime(2025, 3, 15)),
        ("15/03/2025 10:20:30", datetime(2025, 3, 15, 10, 20, 30)),
        ("2025-03-15", datetime(2025, 3, 15)),
        ("", None),
        (None, None),
        ("março de 2025", None),
    ],
)
def test_data_atualizacao_lattes(valor, esperado):
    assert data_atualizacao_lattes(valor) == esperado
