from datetime import datetime

import pytest

from src.adapters.sinks.postgres.repositorio_pessoas import RepositorioPessoasPostgres
from src.core.logic.pii_anonymizer import anonymize_email


@pytest.fixture
def repositorio(conexao_horizon):
    return RepositorioPessoasPostgres(conexao_horizon)


def _contar(conexao, tabela):
    with conexao.cursor() as cursor:
        cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
        return cursor.fetchone()[0]


def test_criar_grava_pessoa_com_emails_em_hash(repositorio, conexao_horizon):
    pessoa_id = repositorio.criar(
        "Maria da Silva", emails=["maria@ifes.edu.br", "maria@gmail.com"]
    )

    [pessoa] = repositorio.listar()
    assert pessoa.id == pessoa_id
    assert pessoa.nome == "Maria da Silva"
    assert pessoa.emails == [
        anonymize_email("maria@ifes.edu.br"),
        anonymize_email("maria@gmail.com"),
    ]
    with conexao_horizon.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM emails_pessoa WHERE email LIKE '%@ifes%'")
        assert cursor.fetchone()[0] == 0


def test_email_ja_em_hash_nao_e_hasheado_de_novo(repositorio):
    email_hash = anonymize_email("joao@ifes.edu.br")
    pessoa_id = repositorio.criar("João")

    assert repositorio.adicionar_email(pessoa_id, email_hash) is True
    assert repositorio.listar()[0].emails == [email_hash]


def test_email_repetido_nao_e_gravado_de_novo(repositorio, conexao_horizon):
    primeira = repositorio.criar("Ana", emails=["ana@ifes.edu.br"])
    segunda = repositorio.criar("Ana Souza")

    assert repositorio.adicionar_email(primeira, "ana@ifes.edu.br") is False
    assert repositorio.adicionar_email(segunda, "ana@ifes.edu.br") is False
    assert repositorio.adicionar_email(segunda, "") is False
    assert _contar(conexao_horizon, "emails_pessoa") == 1


def test_identificador_e_substituido_e_encontrado(repositorio):
    pessoa_id = repositorio.criar("Carlos")

    repositorio.definir_identificador(pessoa_id, "lattes", "1111111111111111")
    repositorio.definir_identificador(pessoa_id, "lattes", "2222222222222222")

    assert (
        repositorio.buscar_por_identificador("lattes", "2222222222222222") == pessoa_id
    )
    assert repositorio.buscar_por_identificador("lattes", "1111111111111111") is None
    assert repositorio.listar()[0].identificadores == {"lattes": "2222222222222222"}


def test_identificador_com_fonte_invalida_e_recusado(repositorio):
    pessoa_id = repositorio.criar("Carlos")

    with pytest.raises(ValueError):
        repositorio.definir_identificador(pessoa_id, "cnpq", "123")


def test_perfil_lattes_e_substituido(repositorio, conexao_horizon):
    pessoa_id = repositorio.criar("Beatriz")

    repositorio.salvar_perfil_lattes(
        pessoa_id, "Resumo antigo", "SILVA, B.", datetime(2024, 1, 10)
    )
    repositorio.salvar_perfil_lattes(
        pessoa_id, "Resumo novo", "SILVA, B.;SILVA, BEATRIZ", datetime(2025, 3, 5)
    )

    with conexao_horizon.cursor() as cursor:
        cursor.execute("SELECT resumo, nomes_citacao, atualizado_em FROM perfis_lattes")
        assert cursor.fetchall() == [
            ("Resumo novo", "SILVA, B.;SILVA, BEATRIZ", datetime(2025, 3, 5))
        ]


def test_perfil_lattes_sem_data_e_recusado(repositorio, conexao_horizon):
    pessoa_id = repositorio.criar("Beatriz")

    with pytest.raises(ValueError):
        repositorio.salvar_perfil_lattes(pessoa_id, "Resumo", "SILVA, B.", None)
    assert _contar(conexao_horizon, "perfis_lattes") == 0


def test_premio_nao_duplica_por_titulo_e_ano(repositorio, conexao_horizon):
    pessoa_id = repositorio.criar("Daniel")

    assert repositorio.adicionar_premio(pessoa_id, "Menção honrosa", 2023) is True
    assert repositorio.adicionar_premio(pessoa_id, "Menção honrosa", 2023) is False
    assert repositorio.adicionar_premio(pessoa_id, "Menção honrosa", 2024) is True
    assert repositorio.adicionar_premio(pessoa_id, "Prêmio sem ano", None) is True
    assert repositorio.adicionar_premio(pessoa_id, "Prêmio sem ano", None) is False
    assert _contar(conexao_horizon, "premios") == 3


def test_proficiencia_cria_idioma_uma_vez_e_nao_duplica(repositorio, conexao_horizon):
    pessoa_id = repositorio.criar("Elisa")
    outra_id = repositorio.criar("Fábio")

    assert (
        repositorio.definir_proficiencia(
            pessoa_id, "Inglês", "alto", "medio", "medio", "alto"
        )
        is True
    )
    assert (
        repositorio.definir_proficiencia(
            pessoa_id, "Inglês", "basico", "basico", "basico", "basico"
        )
        is False
    )
    assert (
        repositorio.definir_proficiencia(
            outra_id, "Inglês", "nao_se_aplica", "basico", "basico", "basico"
        )
        is True
    )
    assert _contar(conexao_horizon, "idiomas") == 1
    assert _contar(conexao_horizon, "proficiencias") == 2


def test_proficiencia_com_nivel_invalido_e_recusada(repositorio):
    pessoa_id = repositorio.criar("Elisa")

    with pytest.raises(ValueError):
        repositorio.definir_proficiencia(
            pessoa_id, "Inglês", "ALTO", "medio", "medio", "alto"
        )


def test_listar_nomes_citacao(repositorio):
    com_perfil = repositorio.criar("Beatriz Silva")
    repositorio.criar("Sem Perfil")
    repositorio.salvar_perfil_lattes(
        com_perfil, "Resumo", "SILVA, B.;SILVA, BEATRIZ", datetime(2025, 1, 1)
    )

    assert repositorio.listar_nomes_citacao() == [
        (com_perfil, "SILVA, B.;SILVA, BEATRIZ")
    ]
