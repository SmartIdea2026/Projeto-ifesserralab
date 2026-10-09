import json
from datetime import date

import pytest

from src.core.logic.carga.contexto import ContextoCarga
from src.core.logic.carga.enriquecimento_pj import CarregadorEnriquecimentoPJ
from src.core.logic.carga.iniciativas_sigpesq import CarregadorIniciativasSigpesq


@pytest.fixture
def contexto(conexao_horizon):
    return ContextoCarga.criar(conexao_horizon)


def _projeto(contexto, nome, tipo="projeto_pesquisa", descricao=None):
    return contexto.iniciativas.criar(
        nome, tipo, contexto.organizacoes.ifes_id(), "em_andamento", descricao
    )


def _doc(nome_arquivo, **pj):
    return (f"/pj/{nome_arquivo}", pj)


def _rico(titulo, **extra):
    pj = {
        "titulo": titulo,
        "descricao": f"Descrição de {titulo}",
        "objetivos": {"geral": "Objetivo geral"},
    }
    pj.update(extra)
    return pj


def _descricao(conexao, iniciativa_id):
    with conexao.cursor() as cursor:
        cursor.execute(
            "SELECT descricao FROM iniciativas WHERE id = %s", (iniciativa_id,)
        )
        return cursor.fetchone()[0]


def test_preenche_descricao_vazia_pelo_codigo(contexto, conexao_horizon):
    projeto = _projeto(contexto, "Nome diferente do documento")

    CarregadorEnriquecimentoPJ(contexto, {"6020": projeto}).carregar(
        [
            _doc(
                "PJ_6020.json",
                codigo="PJ 6020",
                titulo="Outro título",
                descricao="Do PJ",
            )
        ]
    )

    assert _descricao(conexao_horizon, projeto) == "Do PJ"
    contagens = contexto.relatorio.contagens()["enriquecimento_pj"]
    assert contagens["casados_sigpesq_project_code"] == 1
    assert contagens["descartado:conteudo_pj"] == 1
    assert contexto.relatorio.revisoes == []


def test_nao_sobrescreve_descricao_existente(contexto, conexao_horizon):
    projeto = _projeto(contexto, "Projeto Com Resumo", descricao="Resumo do SigPesq")

    CarregadorEnriquecimentoPJ(contexto).carregar(
        [_doc("PJ_1.json", titulo="projeto com resumo", descricao="Do PJ")]
    )

    assert _descricao(conexao_horizon, projeto) == "Resumo do SigPesq"
    assert (
        contexto.relatorio.contagens()["enriquecimento_pj"]["casados_title_exact"] == 1
    )


def test_usa_objetivo_geral_quando_nao_ha_descricao(contexto, conexao_horizon):
    projeto = _projeto(contexto, "Projeto Só Objetivo")

    CarregadorEnriquecimentoPJ(contexto).carregar(
        [
            _doc(
                "PJ_2.json",
                titulo="Projeto Só Objetivo",
                objetivos={"geral": "Objetivo do projeto"},
            )
        ]
    )

    assert _descricao(conexao_horizon, projeto) == "Objetivo do projeto"


def test_titulo_aproximado_vai_para_revisao(contexto, conexao_horizon):
    projeto = _projeto(contexto, "Monitoramento da qualidade do ar na Serra")

    CarregadorEnriquecimentoPJ(contexto).carregar(
        [
            _doc(
                "PJ_3.json",
                titulo="Monitoramento da qualidade do ar da Serra",
                descricao="Aproximado",
            )
        ]
    )

    assert _descricao(conexao_horizon, projeto) == "Aproximado"
    assert [(r.motivo, r.registro) for r in contexto.relatorio.revisoes] == [
        (
            "documento casado por title_fuzzy",
            "Monitoramento da qualidade do ar da Serra",
        )
    ]


def test_documentos_disputando_o_mesmo_projeto(contexto, conexao_horizon):
    projeto = _projeto(contexto, "Projeto Disputado")

    CarregadorEnriquecimentoPJ(contexto, {"77": projeto}).carregar(
        [
            _doc("PJ_a.json", titulo="Projeto Disputado", descricao="Pelo título"),
            _doc("PJ_b.json", codigo="77", titulo="X", descricao="Pelo código"),
        ]
    )

    assert _descricao(conexao_horizon, projeto) == "Pelo código"
    assert (
        contexto.relatorio.contagens()["enriquecimento_pj"]["disputas_descartadas"] == 1
    )


def test_orientacao_nao_e_enriquecida(contexto, conexao_horizon):
    orientacao = _projeto(contexto, "Plano de Trabalho", tipo="orientacao")

    CarregadorEnriquecimentoPJ(contexto, criar_novos=False).carregar(
        [_doc("PJ_4.json", titulo="Plano de Trabalho", descricao="Não deve entrar")]
    )

    assert _descricao(conexao_horizon, orientacao) is None
    assert contexto.relatorio.contagens()["enriquecimento_pj"]["sem_par"] == 1


def test_documento_rico_sem_par_vira_projeto_para_revisar(contexto, conexao_horizon):
    _projeto(contexto, "Projeto Já Existente")

    CarregadorEnriquecimentoPJ(contexto).carregar(
        [
            _doc(
                "PJ_5.json",
                **_rico(
                    "Projeto Novo do Documento",
                    datas={"inicio": "2020-03-01", "fim": "2021-02-28"},
                ),
            ),
            _doc("PJ_6.json", titulo="Documento Pobre", descricao="Sem objetivos"),
            _doc("PJ_7.json", **_rico("Projeto Novo do Documento")),
        ]
    )

    with conexao_horizon.cursor() as cursor:
        cursor.execute(
            """
            SELECT i.nome, i.situacao, i.data_inicio, i.data_fim, o.sigla
            FROM iniciativas i JOIN organizacoes o ON o.id = i.organizacao_id
            WHERE i.nome = 'Projeto Novo do Documento'
            """
        )
        assert cursor.fetchall() == [
            (
                "Projeto Novo do Documento",
                "concluida",
                date(2020, 3, 1),
                date(2021, 2, 28),
                "IFES",
            )
        ]
    contagens = contexto.relatorio.contagens()["enriquecimento_pj"]
    assert contagens["projetos_criados"] == 1
    assert contagens["sem_par_pobres"] == 1
    assert contagens["sem_par_repetidos"] == 1
    assert [r.registro for r in contexto.relatorio.revisoes] == [
        "Projeto Novo do Documento"
    ]


def test_indice_de_codigos_vem_dos_projetos_do_sigpesq(contexto, conexao_horizon):
    carregador = CarregadorIniciativasSigpesq(contexto)
    carregador.carregar_projetos(
        [
            {
                "Id": "PJ 6020",
                "Titulo": "Projeto Com Código",
                "ParecerDiretoria": "Aprovado",
            },
            {"Id": "", "Titulo": "Projeto Sem Código", "ParecerDiretoria": "Aprovado"},
        ]
    )

    indice = carregador.projetos_por_codigo()

    assert list(indice) == ["6020"]
    CarregadorEnriquecimentoPJ(contexto, indice).carregar(
        [_doc("PJ_6020.json", codigo="6020", titulo="?", descricao="Via índice")]
    )
    assert _descricao(conexao_horizon, indice["6020"]) == "Via índice"


def test_carregar_pasta(contexto, conexao_horizon, tmp_path):
    projeto = _projeto(contexto, "Projeto da Pasta")
    (tmp_path / "PJ_10.json").write_text(
        json.dumps({"titulo": "Projeto da Pasta", "descricao": "Lido do arquivo"}),
        encoding="utf-8",
    )
    (tmp_path / "PJ_11.json").write_text("{quebrado", encoding="utf-8")
    (tmp_path / "outro.json").write_text("{}", encoding="utf-8")

    CarregadorEnriquecimentoPJ(contexto).carregar_pasta(str(tmp_path))

    assert _descricao(conexao_horizon, projeto) == "Lido do arquivo"
    assert contexto.relatorio.contagens()["enriquecimento_pj"]["documentos"] == 1
