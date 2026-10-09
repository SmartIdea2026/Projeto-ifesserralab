import pytest

from src.core.logic.tipo_organizacao import tipo_organizacao_por_nome


@pytest.mark.parametrize(
    "nome, tipo",
    [
        ("Universidade Federal do Espírito Santo", "instituicao_ensino"),
        ("Instituto Federal do Espírito Santo", "instituicao_ensino"),
        ("Faculdade de Tecnologia", "instituicao_ensino"),
        ("Escola Estadual Maria Ortiz", "instituicao_ensino"),
        ("Centro Federal de Educação Tecnológica", "instituicao_ensino"),
        ("Escola de Governo do Espírito Santo", "instituicao_ensino"),
        ("Prefeitura Municipal da Serra", "orgao_publico"),
        ("Secretaria de Estado da Educação", "orgao_publico"),
        ("Ministério da Educação", "orgao_publico"),
        ("Governo do Estado do Espírito Santo", "orgao_publico"),
        ("Petrobras", "empresa"),
        ("Vale S.A.", "empresa"),
    ],
)
def test_tipo_organizacao_por_nome(nome, tipo):
    assert tipo_organizacao_por_nome(nome) == tipo


def test_termo_so_conta_como_palavra_inteira():
    assert tipo_organizacao_por_nome("Escolástica Consultoria") == "empresa"
