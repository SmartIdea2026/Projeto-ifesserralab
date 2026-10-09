from datetime import date

import pytest

from src.core.logic.carga.contexto import ContextoCarga
from src.core.logic.carga.grupos_cnpq import CarregadorCnpq
from src.core.logic.carga.regras import (
    data_cnpq,
    data_formacao_cnpq,
    papel_equipe_cnpq,
    texto_cnpq,
)

URL_A = "http://dgp.cnpq.br/dgp/espelhogrupo/A"
URL_B = "http://dgp.cnpq.br/dgp/espelhogrupo/B"


class AdaptadorFalso:
    """Substitui o CnpqCrawlerAdapter: devolve dados prontos por URL."""

    def __init__(self, por_url):
        self._por_url = por_url

    def get_group_data(self, url):
        return self._por_url.get(url)

    def extract_members(self, dados):
        return dados.get("_membros", [])

    def extract_leaders(self, dados):
        return dados.get("_lideres", [])

    def extract_research_lines(self, dados):
        return dados.get("_linhas", [])


@pytest.fixture
def contexto(conexao_horizon):
    return ContextoCarga.criar(conexao_horizon)


@pytest.fixture
def grupos(contexto):
    ifes = contexto.organizacoes.ifes_id()
    serra = contexto.organizacoes.garantir_unidade("Campus Serra", ifes)
    vitoria = contexto.organizacoes.garantir_unidade("Campus Vitória", ifes)
    grupo_a, _ = contexto.equipes.garantir_grupo("Grupo A", serra)
    grupo_b, _ = contexto.equipes.garantir_grupo("Grupo B", vitoria)
    contexto.equipes.garantir_grupo("Grupo Sem URL", serra)
    contexto.equipes.definir_url_cnpq(grupo_a, URL_A)
    contexto.equipes.definir_url_cnpq(grupo_b, URL_B)
    return {"A": grupo_a, "B": grupo_b}


def _consultar(conexao, consulta, parametros=()):
    with conexao.cursor() as cursor:
        cursor.execute(consulta, parametros)
        return cursor.fetchall()


def _membros(conexao, grupo_id):
    return _consultar(
        conexao,
        """
        SELECT p.nome, pa.nome, m.data_inicio, m.data_fim
        FROM membros_equipe m
        JOIN pessoas p ON p.id = m.pessoa_id
        JOIN papeis pa ON pa.id = m.papel_id
        WHERE m.equipe_id = %s
        ORDER BY p.nome, pa.nome
        """,
        (grupo_id,),
    )


@pytest.mark.parametrize(
    "valor, esperado",
    [
        ("15/03/2014", date(2014, 3, 15)),
        ("Anterior a abril de 2014", date(2014, 4, 1)),
        ("Anterior a março de 2010", date(2010, 3, 1)),
        ("Não informada", None),
        ("", None),
        (None, None),
        ("março", None),
    ],
)
def test_data_cnpq(valor, esperado):
    assert data_cnpq(valor) == esperado


def test_data_formacao_cnpq():
    assert data_formacao_cnpq("2012") == date(2012, 1, 1)
    assert data_formacao_cnpq("10/05/2012") == date(2012, 5, 10)
    assert data_formacao_cnpq(None) is None


@pytest.mark.parametrize(
    "papel, esperado",
    [
        ("Pesquisador", ("pesquisador", False)),
        ("Estudante", ("estudante", False)),
        ("Técnico", ("tecnico", False)),
        ("Líder", ("lider", False)),
        ("Pesquisador (Egresso)", ("pesquisador", True)),
        ("Estudante (Egresso)", ("estudante", True)),
        (None, ("pesquisador", False)),
        ("Colaborador estrangeiro", (None, False)),
    ],
)
def test_papel_equipe_cnpq(papel, esperado):
    assert papel_equipe_cnpq(papel) == esperado


def test_texto_cnpq():
    assert texto_cnpq({"descricao": " Repercussões "}) == "Repercussões"
    assert texto_cnpq(["Linha 1", "", {"texto": "Linha 2"}]) == "Linha 1\nLinha 2"
    assert texto_cnpq("  ") is None


def test_grupos_para_sincronizar_com_e_sem_campus(contexto, grupos):
    carregador = CarregadorCnpq(contexto, AdaptadorFalso({}))

    assert [g.id for g in carregador.grupos_para_sincronizar()] == [
        grupos["A"],
        grupos["B"],
    ]
    assert [g.id for g in carregador.grupos_para_sincronizar("serra")] == [grupos["A"]]
    assert carregador.grupos_para_sincronizar("Cachoeiro") == []


def test_sincroniza_grupo_membros_lideres_e_linhas(contexto, grupos, conexao_horizon):
    dados = {
        "nome_grupo": "Grupo A (nome do CNPq)",
        "repercussoes": {"descricao": "Repercussões do grupo"},
        "identificacao": {"ano_de_formacao": "2014"},
        "_membros": [
            {"name": "Ana Souza", "role": "Pesquisador", "data_inicio": "01/03/2015"},
            {
                "name": "Bruno Lima",
                "role": "Estudante (Egresso)",
                "data_inicio": "01/03/2016",
                "data_fim": "28/02/2018",
            },
            {
                "name": "Carla Dias",
                "role": "Técnico",
                "data_inicio": "Anterior a abril de 2014",
            },
            {"name": "", "role": "Pesquisador"},
        ],
        "_lideres": ["Ana Souza"],
        "_linhas": [
            {"nome_da_linha_de_pesquisa": "Robótica Educacional"},
            {"nome_da_linha_de_pesquisa": "robotica educacional"},
        ],
    }

    CarregadorCnpq(contexto, AdaptadorFalso({URL_A: dados})).carregar("Serra")

    assert _consultar(
        conexao_horizon,
        "SELECT e.nome, e.descricao, g.data_inicio FROM equipes e "
        "JOIN grupos_pesquisa g ON g.id = e.id WHERE e.id = %s",
        (grupos["A"],),
    ) == [("Grupo A (nome do CNPq)", "Repercussões do grupo", date(2014, 1, 1))]
    assert _membros(conexao_horizon, grupos["A"]) == [
        ("Ana Souza", "lider", None, None),
        ("Ana Souza", "pesquisador", date(2015, 3, 1), None),
        ("Bruno Lima", "estudante", date(2016, 3, 1), date(2018, 2, 28)),
        ("Carla Dias", "tecnico", date(2014, 4, 1), None),
    ]
    assert _consultar(
        conexao_horizon, "SELECT COUNT(*) FROM areas_conhecimento_equipe"
    ) == [(1,)]
    contagens = contexto.relatorio.contagens()["cnpq"]
    assert contagens["membros"] == 4
    assert contagens["membros_sem_nome"] == 1
    assert contagens["grupos_sincronizados"] == 1


def test_cabecalho_cnpq_nao_vira_nome_do_grupo(contexto, grupos, conexao_horizon):
    CarregadorCnpq(contexto, AdaptadorFalso({URL_B: {"nome_grupo": "CNPq"}})).carregar(
        "Vitória"
    )

    assert _consultar(
        conexao_horizon, "SELECT nome FROM equipes WHERE id = %s", (grupos["B"],)
    ) == [("Grupo B",)]


def test_membro_existente_recebe_data_de_fim(contexto, grupos, conexao_horizon):
    pessoa = contexto.casamento_pessoas.match_or_create("Davi Melo")
    papel = contexto.organizacoes.garantir_papel("estudante", "equipe")
    contexto.equipes.adicionar_membro(
        grupos["A"], pessoa.id, papel, date(2019, 3, 1), None
    )

    CarregadorCnpq(
        contexto,
        AdaptadorFalso(
            {
                URL_A: {
                    "_membros": [
                        {
                            "name": "Davi Melo",
                            "role": "Estudante (Egresso)",
                            "data_inicio": "01/03/2019",
                            "data_fim": "15/12/2021",
                        }
                    ]
                }
            }
        ),
    ).carregar("Serra")

    assert _membros(conexao_horizon, grupos["A"]) == [
        ("Davi Melo", "estudante", date(2019, 3, 1), date(2021, 12, 15))
    ]
    assert contexto.relatorio.contagens()["cnpq"]["membros_com_fim_atualizado"] == 1


def test_falhas_viram_pendencias_e_revisoes(contexto, grupos):
    dados_a = {
        "_membros": [
            {"name": "Elisa Prado", "role": "Colaborador estrangeiro"},
            {"name": "Fábio Reis", "role": "Pesquisador (Egresso)"},
        ]
    }

    CarregadorCnpq(contexto, AdaptadorFalso({URL_A: dados_a})).carregar()

    assert [(p.motivo, p.registro) for p in contexto.relatorio.pendencias] == [
        ("papel do CNPq desconhecido: Colaborador estrangeiro", "Elisa Prado"),
        ("falha ao ler o espelho do CNPq", "Grupo B"),
    ]
    assert [(r.motivo, r.registro) for r in contexto.relatorio.revisoes] == [
        ("egresso sem data de fim no CNPq", "Fábio Reis em Grupo A")
    ]
