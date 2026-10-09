import pytest

from src.core.logic.carga.contexto import ContextoCarga
from src.core.logic.pii_anonymizer import anonymize_email


@pytest.fixture
def contexto(conexao_horizon):
    return ContextoCarga.criar(conexao_horizon)


def _contar_pessoas(conexao):
    with conexao.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM pessoas")
        return cursor.fetchone()[0]


def test_casamento_de_pessoas_grava_no_banco_novo(contexto):
    criada = contexto.casamento_pessoas.match_or_create(
        "Sara Lima", email="sara@ifes.edu.br", strict_match=True
    )

    por_email = contexto.casamento_pessoas.match_or_create(
        "S. Lima", email="sara@ifes.edu.br", strict_match=True
    )
    por_nome = contexto.casamento_pessoas.match_or_create(
        "SARA LIMA", strict_match=True
    )

    assert por_email.id == criada.id
    assert por_nome.id == criada.id
    [pessoa] = contexto.pessoas.listar()
    assert pessoa.emails == [anonymize_email("sara@ifes.edu.br")]


def test_casamento_le_pessoas_ja_gravadas(conexao_horizon):
    primeiro = ContextoCarga.criar(conexao_horizon)
    pessoa = primeiro.casamento_pessoas.match_or_create("Tiago Rocha")

    segundo = ContextoCarga.criar(conexao_horizon)

    assert segundo.casamento_pessoas.match_or_create("Tiago Rocha").id == pessoa.id


def test_erro_no_registro_desfaz_so_ele_e_vira_pendencia(contexto, conexao_horizon):
    with contexto.registro("teste", "registro bom"):
        contexto.casamento_pessoas.match_or_create("Úrsula")

    with contexto.registro("teste", "registro com erro"):
        contexto.casamento_pessoas.match_or_create("Valter")
        raise ValueError("dado obrigatório ausente")

    assert _contar_pessoas(conexao_horizon) == 1
    assert [(p.registro, p.motivo) for p in contexto.relatorio.pendencias] == [
        ("registro com erro", "ValueError: dado obrigatório ausente")
    ]
    # O cache foi recarregado: "Valter" não existe mais e é criado de novo.
    novo = contexto.casamento_pessoas.match_or_create("Valter")
    assert novo is not None
    assert _contar_pessoas(conexao_horizon) == 2


def test_erro_de_banco_no_registro_nao_derruba_a_transacao(contexto, conexao_horizon):
    with contexto.registro("teste", "pessoa sem nome"):
        with conexao_horizon.cursor() as cursor:
            cursor.execute("INSERT INTO pessoas (nome) VALUES (NULL)")

    with contexto.registro("teste", "pessoa depois do erro"):
        contexto.pessoas.criar("Wagner")

    assert _contar_pessoas(conexao_horizon) == 1
    assert contexto.relatorio.contagens()["teste"] == {"pulados": 1}
