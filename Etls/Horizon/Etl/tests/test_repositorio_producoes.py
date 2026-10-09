import pytest

from src.adapters.sinks.postgres.repositorio_pessoas import RepositorioPessoasPostgres
from src.adapters.sinks.postgres.repositorio_producoes import (
    RepositorioProducoesPostgres,
    link_do_doi,
)
from src.core.ports.repositorio_producoes import (
    ANO_NAO_INFORMADO,
    TIPO_TRABALHO_CONGRESSO,
    VEICULO_NAO_INFORMADO,
)


@pytest.fixture
def repositorio(conexao_horizon):
    return RepositorioProducoesPostgres(conexao_horizon)


def _consultar(conexao, consulta, parametros=()):
    with conexao.cursor() as cursor:
        cursor.execute(consulta, parametros)
        return cursor.fetchall()


@pytest.mark.parametrize(
    "doi, link",
    [
        ("10.1000/xyz123", "https://doi.org/10.1000/xyz123"),
        ("doi:10.1000/abc", "https://doi.org/10.1000/abc"),
        ("https://doi.org/10.1000/j", "https://doi.org/10.1000/j"),
        (None, None),
        ("", None),
    ],
)
def test_link_do_doi(doi, link):
    assert link_do_doi(doi) == link


def test_artigo_e_gravado_em_producoes_e_artigos(repositorio, conexao_horizon):
    artigo, criado = repositorio.garantir_artigo(
        "Aprendizado de máquina na educação",
        2023,
        "Revista Brasileira de Informática na Educação",
        volume="31",
        paginas="10-20",
        doi=" 10.5753/rbie.2023.1 ",
    )

    assert criado is True
    assert (
        _consultar(
            conexao_horizon,
            """
        SELECT t.nome, p.titulo, p.ano, p.link, a.veiculo, a.volume, a.paginas, a.doi
        FROM producoes p
        JOIN artigos a ON a.id = p.id
        JOIN tipos_producao t ON t.id = p.tipo_producao_id
        WHERE p.id = %s
        """,
            (artigo,),
        )
        == [
            (
                "artigo",
                "Aprendizado de máquina na educação",
                2023,
                "https://doi.org/10.5753/rbie.2023.1",
                "Revista Brasileira de Informática na Educação",
                "31",
                "10-20",
                "10.5753/rbie.2023.1",
            )
        ]
    )


def test_artigo_e_casado_por_doi_e_depois_por_titulo_e_ano(repositorio):
    com_doi, _ = repositorio.garantir_artigo(
        "Título A", 2022, "Revista X", doi="10.1/a"
    )
    sem_doi, _ = repositorio.garantir_artigo("Título B", 2022, "Revista Y")

    assert repositorio.garantir_artigo("Outro título", 2020, "Z", doi="10.1/a") == (
        com_doi,
        False,
    )
    assert repositorio.garantir_artigo("Título B", 2022, "Revista Y") == (
        sem_doi,
        False,
    )
    assert repositorio.garantir_artigo("Título B", 2023, "Revista Y")[1] is True


def test_trabalho_de_congresso_tem_tipo_proprio(repositorio, conexao_horizon):
    trabalho, _ = repositorio.garantir_artigo(
        "Trabalho no SBIE", 2021, "SBIE 2021", tipo=TIPO_TRABALHO_CONGRESSO
    )

    assert _consultar(
        conexao_horizon,
        "SELECT t.nome FROM producoes p JOIN tipos_producao t "
        "ON t.id = p.tipo_producao_id WHERE p.id = %s",
        (trabalho,),
    ) == [("trabalhos_completos_congressos",)]


def test_artigo_aceita_valores_genericos_e_recusa_vazios(repositorio):
    _, criado = repositorio.garantir_artigo(
        "Sem ano nem revista", ANO_NAO_INFORMADO, VEICULO_NAO_INFORMADO
    )

    assert criado is True
    with pytest.raises(ValueError):
        repositorio.garantir_artigo("Sem ano", None, "Revista")
    with pytest.raises(ValueError):
        repositorio.garantir_artigo("Sem revista", 2020, None)


def test_producao_tecnica_com_tipo_sob_demanda(repositorio, conexao_horizon):
    software, criado = repositorio.garantir_producao(
        "Sistema Horizon", 2024, "softwares_sem_patente"
    )

    assert criado is True
    assert repositorio.garantir_producao(
        "Sistema Horizon", 2024, "softwares_sem_patente"
    ) == (software, False)
    assert repositorio.garantir_producao("Sistema Horizon", 2024, "patentes")[1]
    assert _consultar(conexao_horizon, "SELECT COUNT(*) FROM tipos_producao") == [(3,)]


def test_producao_tecnica_nao_casa_com_artigo_de_mesmo_titulo(repositorio):
    artigo, _ = repositorio.garantir_artigo("Mesmo título", 2024, "Revista")

    producao, criada = repositorio.garantir_producao("Mesmo título", 2024, "artigo")

    assert criada is True
    assert producao != artigo


def test_autores_nao_repetem(repositorio, conexao_horizon):
    pessoas = RepositorioPessoasPostgres(conexao_horizon)
    dona = pessoas.criar("Quésia")
    coautor = pessoas.criar("Rafael")
    artigo, _ = repositorio.garantir_artigo("Artigo com coautor", 2024, "Revista")

    assert repositorio.adicionar_autor(artigo, dona)
    assert repositorio.adicionar_autor(artigo, coautor)
    assert not repositorio.adicionar_autor(artigo, dona)
    assert _consultar(conexao_horizon, "SELECT COUNT(*) FROM autores_producao") == [
        (2,)
    ]
