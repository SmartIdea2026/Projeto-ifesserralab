from datetime import date

import pandas as pd
import pytest

from src.core.logic.carga.contexto import ContextoCarga
from src.core.logic.carga.iniciativas_sigpesq import (
    CarregadorIniciativasSigpesq,
    aprovado,
    nome_campus,
)


def _projeto(**campos):
    linha = {
        "Id": "",
        "Titulo": "",
        "ParecerDiretoria": "Aprovado",
        "Inicio": "",
        "Fim": "",
        "Resumo": "",
        "Valor Aprovado": "",
        "Coordenador": "",
        "Pesquisadores": "",
        "Estudantes": "",
        "GrupoPesquisa": "",
        "ParceiroDemandante": "",
        "GrupoPesquisaExterno": "",
        "AreaConhecimento": "",
        "PalavraChave": "",
        "CampusExecucao": "",
    }
    linha.update(campos)
    return linha


def _bolsista(**campos):
    linha = {
        "Id": "",
        "Orientado": "",
        "OrientadoEmail": "",
        "Orientador": "",
        "OrientadorEmail": "",
        "TituloPT": "",
        "CodPT": "",
        "CodPJ": "",
        "TituloPJ": "",
        "Inicio": "",
        "Fim": "",
        "Cancelado": "",
        "Programa": "",
        "Valor": "",
        "AgFinanciadora": "",
        "CampusExecucao": "",
    }
    linha.update(campos)
    return linha


@pytest.fixture
def contexto(conexao_horizon):
    return ContextoCarga.criar(conexao_horizon)


@pytest.fixture
def carregador(contexto):
    return CarregadorIniciativasSigpesq(contexto)


def _consultar(conexao, consulta, parametros=()):
    with conexao.cursor() as cursor:
        cursor.execute(consulta, parametros)
        return cursor.fetchall()


def _participantes(conexao, nome_iniciativa):
    return _consultar(
        conexao,
        """
        SELECT pe.nome, pa.nome
        FROM participantes_iniciativa pi
        JOIN iniciativas i ON i.id = pi.iniciativa_id
        JOIN pessoas pe ON pe.id = pi.pessoa_id
        JOIN papeis pa ON pa.id = pi.papel_id
        WHERE i.nome = %s
        ORDER BY pa.nome, pe.nome
        """,
        (nome_iniciativa,),
    )


@pytest.mark.parametrize(
    "parecer, esperado",
    [
        ("Aprovado", True),
        ("Aprovado com ressalvas", True),
        ("", True),
        ("Reprovado", False),
        ("Em análise", False),
    ],
)
def test_filtro_de_aprovacao(parecer, esperado):
    assert aprovado({"ParecerDiretoria": parecer}) is esperado


def test_nome_campus_ignora_valores_curtos():
    assert nome_campus("Serra") == "Serra"
    assert nome_campus("N/A") is None
    assert nome_campus("") is None


def test_projeto_completo(carregador, contexto, conexao_horizon):
    carregador.carregar_projetos(
        [
            _projeto(
                Id="PJ-101",
                Titulo="Cidades Inteligentes na Serra",
                Inicio="01/03/2020",
                Fim="28/02/2021",
                Resumo="Resumo do projeto",
                **{"Valor Aprovado": "5000,00"},
                Coordenador="Ana Souza",
                Pesquisadores="Bruno Lima; Carla Dias",
                Estudantes="Davi Melo",
                ParceiroDemandante="Prefeitura Municipal da Serra",
                GrupoPesquisaExterno="Grupo X da UFES",
                AreaConhecimento="Ciência da Computação",
                PalavraChave="IoT; Mobilidade",
                CampusExecucao="Serra",
            )
        ]
    )

    assert (
        _consultar(
            conexao_horizon,
            """
        SELECT i.nome, t.nome, o.nome, i.situacao, i.descricao, i.data_inicio, i.data_fim
        FROM iniciativas i
        JOIN tipos_iniciativa t ON t.id = i.tipo_iniciativa_id
        JOIN organizacoes o ON o.id = i.organizacao_id
        """,
        )
        == [
            (
                "Cidades Inteligentes na Serra",
                "projeto_pesquisa",
                "Serra",
                "concluida",
                "Resumo do projeto",
                date(2020, 3, 1),
                date(2021, 2, 28),
            )
        ]
    )
    assert _participantes(conexao_horizon, "Cidades Inteligentes na Serra") == [
        ("Ana Souza", "coordenador"),
        ("Davi Melo", "estudante"),
        ("Bruno Lima", "pesquisador"),
        ("Carla Dias", "pesquisador"),
    ]
    assert _consultar(
        conexao_horizon,
        "SELECT o.nome, o.tipo, oi.papel FROM organizacoes_iniciativa oi "
        "JOIN organizacoes o ON o.id = oi.organizacao_id",
    ) == [("Prefeitura Municipal da Serra", "orgao_publico", "demandante")]
    assert _consultar(
        conexao_horizon,
        "SELECT a.nome FROM areas_conhecimento_iniciativa ai "
        "JOIN areas_conhecimento a ON a.id = ai.area_id ORDER BY a.nome",
    ) == [("Ciência da Computação",), ("IoT",), ("Mobilidade",)]
    assert _consultar(
        conexao_horizon, "SELECT COUNT(*) FROM areas_conhecimento_pessoa"
    ) == [(6,)]
    contagens = contexto.relatorio.contagens()["projetos_sigpesq"]
    assert contagens["descartado:valor_aprovado"] == 1
    assert contagens["descartado:grupo_pesquisa_externo"] == 1


def test_projeto_nao_aprovado_e_sem_titulo(carregador, contexto, conexao_horizon):
    carregador.carregar_projetos(
        [
            _projeto(Titulo="Reprovado", ParecerDiretoria="Reprovado"),
            _projeto(Titulo=""),
            _projeto(Titulo="Sem parecer", ParecerDiretoria=""),
        ]
    )

    assert _consultar(conexao_horizon, "SELECT nome, situacao FROM iniciativas") == [
        ("Sem parecer", "desconhecida")
    ]
    contagens = contexto.relatorio.contagens()["projetos_sigpesq"]
    assert contagens["nao_aprovados"] == 1
    assert [p.motivo for p in contexto.relatorio.pendencias] == ["projeto sem título"]


def test_projeto_sem_campus_fica_no_ifes(carregador, conexao_horizon):
    carregador.carregar_projetos([_projeto(Titulo="Projeto Geral", Fim="01/01/2099")])

    assert _consultar(
        conexao_horizon,
        "SELECT o.sigla, i.situacao FROM iniciativas i "
        "JOIN organizacoes o ON o.id = i.organizacao_id",
    ) == [("IFES", "em_andamento")]


def test_projeto_liga_grupo_existente_e_cria_o_que_falta(
    carregador, contexto, conexao_horizon
):
    serra = contexto.organizacoes.garantir_unidade(
        "Serra", contexto.organizacoes.ifes_id()
    )
    contexto.equipes.garantir_grupo("Grupo Existente", serra)

    carregador.carregar_projetos(
        [
            _projeto(
                Titulo="Projeto A",
                Coordenador="Elisa Prado",
                GrupoPesquisa="GRUPO EXISTENTE",
                CampusExecucao="Serra",
            ),
            _projeto(
                Titulo="Projeto B",
                Coordenador="Fábio Reis",
                Estudantes="Gabi Nunes",
                GrupoPesquisa="Grupo Novo",
            ),
        ]
    )

    assert (
        _consultar(
            conexao_horizon,
            """
        SELECT i.nome, e.nome, ei.papel
        FROM equipes_iniciativa ei
        JOIN iniciativas i ON i.id = ei.iniciativa_id
        JOIN equipes e ON e.id = ei.equipe_id
        ORDER BY i.nome
        """,
        )
        == [
            ("Projeto A", "Grupo Existente", "executor"),
            ("Projeto B", "Grupo Novo", "executor"),
        ]
    )
    assert (
        _consultar(
            conexao_horizon,
            """
        SELECT o.nome, e.descricao FROM equipes e
        JOIN organizacoes o ON o.id = e.organizacao_id WHERE e.nome = 'Grupo Novo'
        """,
        )
        == [("Reitoria", "Grupo de Pesquisa importado do SigPesq: Grupo Novo")]
    )
    assert (
        _consultar(
            conexao_horizon,
            """
        SELECT p.nome, pa.nome FROM membros_equipe m
        JOIN equipes e ON e.id = m.equipe_id
        JOIN pessoas p ON p.id = m.pessoa_id
        JOIN papeis pa ON pa.id = m.papel_id
        WHERE e.nome = 'Grupo Novo' ORDER BY p.nome
        """,
        )
        == [("Fábio Reis", "pesquisador"), ("Gabi Nunes", "estudante")]
    )


def test_projeto_repetido_atualiza_em_vez_de_criar(carregador, conexao_horizon):
    carregador.carregar_projetos(
        [
            _projeto(Id="PJ-7", Titulo="Título antigo", Resumo="v1"),
            _projeto(Id="PJ-7", Titulo="Título novo", Resumo="v2"),
        ]
    )

    assert _consultar(conexao_horizon, "SELECT nome, descricao FROM iniciativas") == [
        ("Título novo", "v2")
    ]


def test_bolsista_vira_orientacao_filha_com_bolsa(
    carregador, contexto, conexao_horizon
):
    carregador.carregar_projetos(
        [
            _projeto(
                Id="PJ-200",
                Titulo="Projeto Pai",
                Inicio="01/03/2022",
                Fim="28/02/2023",
                Coordenador="Helena Costa",
                CampusExecucao="Serra",
            )
        ]
    )
    carregador.carregar_bolsistas(
        [
            _bolsista(
                Id="55",
                Orientado="Igor Alves",
                OrientadoEmail="igor@estudante.ifes.edu.br",
                Orientador="Helena Costa",
                OrientadorEmail="helena@ifes.edu.br",
                TituloPT="Plano do Igor",
                CodPT="PT-1",
                CodPJ="PJ-200",
                TituloPJ="Projeto Pai (título no plano)",
                Inicio="01/03/2022",
                Fim="31/07/2023",
                Programa="pibic",
                Valor="700,00",
                AgFinanciadora="FAPES",
                CampusExecucao="Serra",
            )
        ]
    )

    assert (
        _consultar(
            conexao_horizon,
            """
        SELECT f.nome, t.nome, f.situacao, pai.nome
        FROM iniciativas f
        JOIN tipos_iniciativa t ON t.id = f.tipo_iniciativa_id
        JOIN hierarquia_iniciativas h ON h.iniciativa_id = f.id
        JOIN iniciativas pai ON pai.id = h.iniciativa_pai_id
        """,
        )
        == [("Plano do Igor", "orientacao", "concluida", "Projeto Pai")]
    )
    assert _participantes(conexao_horizon, "Plano do Igor") == [
        ("Helena Costa", "orientador"),
        ("Igor Alves", "orientando"),
    ]
    assert _participantes(conexao_horizon, "Projeto Pai") == [
        ("Helena Costa", "coordenador"),
        ("Igor Alves", "estudante"),
        ("Helena Costa", "pesquisador"),
    ]
    assert (
        _consultar(
            conexao_horizon,
            """
        SELECT b.nome, b.valor, o.nome, pe.nome
        FROM bolsas_participante bp
        JOIN bolsas b ON b.id = bp.bolsa_id
        JOIN organizacoes o ON o.id = b.financiador_id
        JOIN participantes_iniciativa pi ON pi.id = bp.participante_id
        JOIN pessoas pe ON pe.id = pi.pessoa_id
        """,
        )
        == [("PIBIC", 700, "FAPES", "Igor Alves")]
    )
    assert _consultar(
        conexao_horizon,
        "SELECT o.nome, o.tipo, oi.papel FROM organizacoes_iniciativa oi "
        "JOIN organizacoes o ON o.id = oi.organizacao_id",
    ) == [("FAPES", "fomento", "financiadora")]
    # O fim do pai foi ampliado pelo fim da orientação.
    assert _consultar(
        conexao_horizon,
        "SELECT data_inicio, data_fim FROM iniciativas WHERE nome = 'Projeto Pai'",
    ) == [(date(2022, 3, 1), date(2023, 7, 31))]


def test_bolsista_sem_projeto_cria_pai_provisorio_e_recalcula(
    carregador, contexto, conexao_horizon
):
    carregador.carregar_bolsistas(
        [
            _bolsista(
                Orientado="Júlia Ramos",
                Orientador="Kleber Silva",
                TituloPT="Plano da Júlia",
                CodPT="PT-2",
                CodPJ="PJ-999",
                TituloPJ="Projeto Sem Planilha",
                Inicio="01/03/2021",
                Fim="28/02/2022",
            ),
            _bolsista(
                Orientado="Lucas Teixeira",
                Orientador="Kleber Silva",
                TituloPT="Plano do Lucas",
                CodPT="PT-3",
                CodPJ="PJ-999",
                TituloPJ="Projeto Sem Planilha",
                Inicio="01/03/2020",
                Fim="28/02/2021",
            ),
        ]
    )

    assert (
        _consultar(
            conexao_horizon,
            """
        SELECT i.situacao, i.data_inicio, i.data_fim, o.sigla
        FROM iniciativas i JOIN organizacoes o ON o.id = i.organizacao_id
        WHERE i.nome = 'Projeto Sem Planilha'
        """,
        )
        == [("concluida", date(2020, 3, 1), date(2022, 2, 28), "IFES")]
    )
    contagens = contexto.relatorio.contagens()["bolsistas_sigpesq"]
    assert contagens["projetos_pai_provisorios"] == 1
    assert contagens["projetos_pai_recalculados"] == 1


def test_titulo_de_orientacao_repetido_ganha_sufixo(carregador, conexao_horizon):
    carregador.carregar_bolsistas(
        [
            _bolsista(
                Id="1",
                Orientado="Mara Lopes",
                TituloPT="Plano Comum",
                CodPT="PT-10",
                Inicio="01/03/2023",
            ),
            _bolsista(
                Id="2",
                Orientado="Nilo Vaz",
                TituloPT="Plano Comum",
                CodPT="PT-11",
                Inicio="01/03/2024",
            ),
        ]
    )

    assert _consultar(conexao_horizon, "SELECT nome FROM iniciativas ORDER BY id") == [
        ("Plano Comum",),
        ("Plano Comum | Orientacao Nilo Vaz | 2024 | sigpesq 2",),
    ]


def test_bolsa_sem_financiador_e_orientacao_cancelada(
    carregador, contexto, conexao_horizon
):
    carregador.carregar_bolsistas(
        [
            _bolsista(
                Orientado="Otávio Pires",
                TituloPT="Plano Cancelado",
                CodPT="PT-20",
                Cancelado="Sim",
                Programa="PIVIC",
            )
        ]
    )

    assert _consultar(conexao_horizon, "SELECT nome, situacao FROM iniciativas") == [
        ("Plano Cancelado", "cancelada")
    ]
    assert _consultar(conexao_horizon, "SELECT COUNT(*) FROM bolsas") == [(0,)]
    assert [p.motivo for p in contexto.relatorio.pendencias] == [
        "bolsa sem financiador"
    ]
    assert (
        contexto.relatorio.contagens()["bolsistas_sigpesq"][
            "descartado:dados_cancelamento"
        ]
        == 1
    )


def test_carregar_arquivos_excel(carregador, conexao_horizon, tmp_path):
    projetos = tmp_path / "projetos.xlsx"
    bolsistas = tmp_path / "bolsistas.xlsx"
    pd.DataFrame([_projeto(Id="PJ-1", Titulo="Projeto Excel")]).to_excel(
        projetos, index=False
    )
    pd.DataFrame(
        [
            _bolsista(
                Orientado="Paula", TituloPT="Plano Excel", CodPJ="PJ-1", TituloPJ="X"
            )
        ]
    ).to_excel(bolsistas, index=False)

    carregador.carregar_projetos_arquivo(str(projetos))
    carregador.carregar_bolsistas_arquivos([str(bolsistas)])

    assert _consultar(
        conexao_horizon,
        "SELECT f.nome, pai.nome FROM hierarquia_iniciativas h "
        "JOIN iniciativas f ON f.id = h.iniciativa_id "
        "JOIN iniciativas pai ON pai.id = h.iniciativa_pai_id",
    ) == [("Plano Excel", "Projeto Excel")]


def test_mesmo_titulo_com_codigos_diferentes_nao_se_junta(carregador, conexao_horizon):
    carregador.carregar_projetos(
        [
            _projeto(Id="PJ-31", Titulo="Projeto Homônimo", Coordenador="Rita"),
            _projeto(Id="PJ-32", Titulo="Projeto Homônimo", Coordenador="Sílvio"),
        ]
    )

    assert _consultar(
        conexao_horizon,
        "SELECT COUNT(*) FROM iniciativas WHERE nome = 'Projeto Homônimo'",
    ) == [(2,)]
