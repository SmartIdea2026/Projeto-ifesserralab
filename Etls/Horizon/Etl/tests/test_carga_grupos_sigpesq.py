import pandas as pd
import pytest

from src.core.logic.carga.contexto import ContextoCarga
from src.core.logic.carga.grupos_sigpesq import CarregadorGruposSigpesq
from src.core.logic.carga.regras import texto
from src.core.logic.pii_anonymizer import anonymize_email

NAN = float("nan")


def _linha(nome, sigla=NAN, unidade=NAN, area=NAN, site=NAN, lideres=NAN):
    return {
        "Nome": nome,
        "Sigla": sigla,
        "Unidade": unidade,
        "AreaConhecimento": area,
        "Column1": site,
        "Lideres": lideres,
    }


@pytest.fixture
def contexto(conexao_horizon):
    return ContextoCarga.criar(conexao_horizon)


def _consultar(conexao, consulta):
    with conexao.cursor() as cursor:
        cursor.execute(consulta)
        return cursor.fetchall()


@pytest.mark.parametrize(
    "valor, esperado",
    [(" Serra ", "Serra"), ("", None), (None, None), (NAN, None), (3, "3")],
)
def test_texto_da_planilha(valor, esperado):
    assert texto(valor) == esperado


def test_grupo_novo_com_campus_area_url_e_lideres(contexto, conexao_horizon):
    CarregadorGruposSigpesq(contexto).carregar_linhas(
        [
            _linha(
                "Núcleo de Robótica",
                sigla="NR",
                unidade="Serra",
                area="Engenharias",
                site="http://dgp.cnpq.br/dgp/espelhogrupo/1",
                lideres="Ana Souza (ana@ifes.edu.br); Bruno Lima",
            )
        ]
    )

    assert (
        _consultar(
            conexao_horizon,
            """
        SELECT e.nome, e.sigla, o.nome, g.url_cnpq
        FROM equipes e
        JOIN grupos_pesquisa g ON g.id = e.id
        JOIN organizacoes o ON o.id = e.organizacao_id
        """,
        )
        == [
            (
                "Núcleo de Robótica",
                "NR",
                "Serra",
                "http://dgp.cnpq.br/dgp/espelhogrupo/1",
            )
        ]
    )
    assert (
        _consultar(
            conexao_horizon,
            """
        SELECT p.nome, pa.nome, m.data_inicio
        FROM membros_equipe m
        JOIN pessoas p ON p.id = m.pessoa_id
        JOIN papeis pa ON pa.id = m.papel_id
        ORDER BY p.nome
        """,
        )
        == [("Ana Souza", "lider", None), ("Bruno Lima", "lider", None)]
    )
    assert _consultar(
        conexao_horizon,
        "SELECT a.nome FROM areas_conhecimento_equipe ae "
        "JOIN areas_conhecimento a ON a.id = ae.area_id",
    ) == [("Engenharias",)]
    assert _consultar(conexao_horizon, "SELECT email FROM emails_pessoa") == [
        (anonymize_email("ana@ifes.edu.br"),)
    ]
    assert contexto.relatorio.contagens()["grupos_sigpesq"] == {
        "lideres": 2,
        "grupos_criados": 1,
        "concluido": 1,
    }


def test_grupo_sem_unidade_vai_para_campus_desconhecido(contexto, conexao_horizon):
    CarregadorGruposSigpesq(contexto).carregar_linhas([_linha("Grupo Sem Campus")])

    assert (
        _consultar(
            conexao_horizon,
            """
        SELECT o.nome, o.tipo, pai.sigla
        FROM equipes e
        JOIN organizacoes o ON o.id = e.organizacao_id
        JOIN unidades_organizacionais u ON u.id = o.id
        JOIN organizacoes pai ON pai.id = u.organizacao_pai_id
        """,
        )
        == [("Campus Desconhecido", "unidade", "IFES")]
    )


def test_grupo_repetido_so_atualiza_url_e_nao_mexe_nos_lideres(
    contexto, conexao_horizon
):
    CarregadorGruposSigpesq(contexto).carregar_linhas(
        [
            _linha("Grupo Alfa", unidade="Serra", lideres="Carla Dias"),
            _linha(
                "GRUPO ALFA",
                unidade="Vitória",
                site="http://dgp.cnpq.br/dgp/espelhogrupo/2",
                lideres="Davi Melo",
            ),
        ]
    )

    assert _consultar(conexao_horizon, "SELECT COUNT(*) FROM equipes") == [(1,)]
    assert _consultar(conexao_horizon, "SELECT url_cnpq FROM grupos_pesquisa") == [
        ("http://dgp.cnpq.br/dgp/espelhogrupo/2",)
    ]
    assert _consultar(
        conexao_horizon,
        "SELECT p.nome FROM membros_equipe m JOIN pessoas p ON p.id = m.pessoa_id",
    ) == [("Carla Dias",)]


def test_url_ja_usada_e_grupo_sem_nome_viram_pendencia(contexto, conexao_horizon):
    url = "http://dgp.cnpq.br/dgp/espelhogrupo/3"

    CarregadorGruposSigpesq(contexto).carregar_linhas(
        [
            _linha("Grupo Beta", site=url),
            _linha(NAN),
            _linha("Grupo Gama", site=url),
        ]
    )

    assert _consultar(conexao_horizon, "SELECT COUNT(*) FROM equipes") == [(2,)]
    assert [(p.motivo, p.registro) for p in contexto.relatorio.pendencias] == [
        ("grupo sem nome", "linha 2"),
        ("URL CNPq não gravada: já é de outro grupo", "Grupo Gama"),
    ]


def test_lider_ja_existente_e_reaproveitado_pelo_email(contexto, conexao_horizon):
    CarregadorGruposSigpesq(contexto).carregar_linhas(
        [
            _linha("Grupo Delta", lideres="Elisa Prado (elisa@ifes.edu.br)"),
            _linha("Grupo Épsilon", lideres="E. Prado (elisa@ifes.edu.br)"),
        ]
    )

    assert _consultar(conexao_horizon, "SELECT COUNT(*) FROM pessoas") == [(1,)]
    assert _consultar(conexao_horizon, "SELECT COUNT(*) FROM membros_equipe") == [(2,)]


def test_carregar_arquivo_excel(contexto, conexao_horizon, tmp_path):
    caminho = tmp_path / "grupos.xlsx"
    pd.DataFrame([_linha("Grupo do Excel", unidade="Serra")]).to_excel(
        caminho, index=False
    )

    CarregadorGruposSigpesq(contexto).carregar_arquivo(str(caminho))

    assert _consultar(conexao_horizon, "SELECT nome FROM equipes") == [
        ("Grupo do Excel",)
    ]
