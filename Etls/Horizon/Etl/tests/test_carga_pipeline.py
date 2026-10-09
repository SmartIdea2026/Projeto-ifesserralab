import json
import uuid
from contextlib import contextmanager
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from psycopg import sql

from src.core.logic.carga.pipeline import ConfiguracaoCarga, executar_carga
from src.core.logic.carga.relatorio import RelatorioCarga

URL_CNPQ = "http://dgp.cnpq.br/dgp/espelhogrupo/99"


class AdaptadorCnpqFalso:
    def get_group_data(self, url):
        if url != URL_CNPQ:
            return None
        return {"identificacao": {"ano_de_formacao": "2015"}}

    def extract_members(self, dados):
        return [
            {"name": "Bruno Lima", "role": "Estudante", "data_inicio": "01/03/2020"}
        ]

    def extract_leaders(self, dados):
        return ["Ana Souza"]

    def extract_research_lines(self, dados):
        return [{"nome_da_linha_de_pesquisa": "Robótica"}]


@pytest.fixture
def schema_da_carga(conexao_horizon):
    """Schema próprio para a carga (ela recria o schema que recebe)."""
    schema = f"teste_carga_{uuid.uuid4().hex[:8]}"
    yield schema
    conexao_horizon.rollback()
    with conexao_horizon.cursor() as cursor:
        cursor.execute(
            sql.SQL("DROP SCHEMA IF EXISTS {} CASCADE").format(sql.Identifier(schema))
        )
    conexao_horizon.commit()


def _escrever_fontes(raiz):
    sigpesq = raiz / "sigpesq"
    for pasta in ("research_group", "research_projects", "advisorships"):
        (sigpesq / pasta).mkdir(parents=True)
    pd.DataFrame(
        [
            {
                "Nome": "Grupo de Robótica",
                "Sigla": "GR",
                "Unidade": "Serra",
                "AreaConhecimento": "Engenharias",
                "Column1": URL_CNPQ,
                "Lideres": "Ana Souza (ana@ifes.edu.br)",
            }
        ]
    ).to_excel(sigpesq / "research_group" / "grupos.xlsx", index=False)
    pd.DataFrame(
        [
            {
                "Id": "PJ 6020",
                "Titulo": "Robôs na Escola",
                "ParecerDiretoria": "Aprovado",
                "Inicio": "01/03/2020",
                "Fim": "28/02/2021",
                "Coordenador": "Ana Souza",
                "GrupoPesquisa": "Grupo de Robótica",
                "CampusExecucao": "Serra",
            }
        ]
    ).to_excel(sigpesq / "research_projects" / "projetos.xlsx", index=False)
    pd.DataFrame(
        [
            {
                "Id": "10",
                "Orientado": "Bruno Lima",
                "Orientador": "Ana Souza",
                "TituloPT": "Plano do Bruno",
                "CodPT": "PT 1",
                "CodPJ": "PJ 6020",
                "TituloPJ": "Robôs na Escola",
                "Inicio": "01/03/2020",
                "Fim": "28/02/2021",
                "Programa": "PIBIC",
                "Valor": "700",
                "AgFinanciadora": "FAPES",
                "CampusExecucao": "Serra",
            }
        ]
    ).to_excel(sigpesq / "advisorships" / "bolsistas.xlsx", index=False)

    lattes = raiz / "lattes"
    lattes.mkdir()
    (lattes / "Ana_1111111111111111.json").write_text(
        json.dumps(
            {
                "informacoes_pessoais": {
                    "nome_completo": "Ana Souza",
                    "texto_resumo": "Resumo",
                    "nome_citacoes": "SOUZA, A.",
                    "atualizacao_cv": "15/03/2025",
                },
                "premios_titulos": [{"descricao": "Prêmio", "ano": "2021"}],
            }
        ),
        encoding="utf-8",
    )

    pj = raiz / "pj"
    pj.mkdir()
    (pj / "PJ_6020.json").write_text(
        json.dumps({"codigo": "6020", "titulo": "?", "descricao": "Descrição do PJ"}),
        encoding="utf-8",
    )
    return ConfiguracaoCarga(
        pasta_sigpesq=str(sigpesq), pasta_lattes=str(lattes), pasta_pj=str(pj)
    )


def _contar(conexao, schema, tabela):
    with conexao.cursor() as cursor:
        cursor.execute(
            sql.SQL("SELECT COUNT(*) FROM {}").format(sql.Identifier(schema, tabela))
        )
        return cursor.fetchone()[0]


def test_executar_carga_de_ponta_a_ponta(conexao_horizon, schema_da_carga, tmp_path):
    configuracao = _escrever_fontes(tmp_path)
    configuracao.schema = schema_da_carga
    configuracao.campus = "Serra"
    relatorio = RelatorioCarga()

    executar_carga(
        conexao_horizon,
        relatorio,
        configuracao,
        adaptador_cnpq=AdaptadorCnpqFalso(),
        registrar=lambda _: None,
    )

    contagens = {
        tabela: _contar(conexao_horizon, schema_da_carga, tabela)
        for tabela in (
            "pessoas",
            "equipes",
            "iniciativas",
            "hierarquia_iniciativas",
            "participantes_iniciativa",
            "bolsas",
            "membros_equipe",
            "perfis_lattes",
            "premios",
        )
    }
    assert contagens == {
        "pessoas": 2,
        "equipes": 1,
        "iniciativas": 2,
        "hierarquia_iniciativas": 1,
        "participantes_iniciativa": 5,
        "bolsas": 1,
        "membros_equipe": 2,
        "perfis_lattes": 1,
        "premios": 1,
    }
    with conexao_horizon.cursor() as cursor:
        cursor.execute(
            sql.SQL("SELECT descricao FROM {} WHERE nome = 'Robôs na Escola'").format(
                sql.Identifier(schema_da_carga, "iniciativas")
            )
        )
        assert cursor.fetchone() == ("Descrição do PJ",)
    assert relatorio.pendencias == []
    for passo in (
        "grupos_sigpesq",
        "projetos_sigpesq",
        "bolsistas_sigpesq",
        "cnpq",
        "lattes_pessoas",
        "lattes_curriculos",
        "lattes_orientacoes",
        "enriquecimento_pj",
    ):
        assert relatorio.contagens()[passo]["concluido"] == 1


def test_executar_carga_sem_arquivos_relata_o_que_falta(
    conexao_horizon, schema_da_carga, tmp_path
):
    relatorio = RelatorioCarga()

    executar_carga(
        conexao_horizon,
        relatorio,
        ConfiguracaoCarga(
            pasta_sigpesq=str(tmp_path / "sigpesq"),
            pasta_lattes=str(tmp_path / "lattes"),
            pasta_pj=str(tmp_path / "pj"),
            schema=schema_da_carga,
        ),
        adaptador_cnpq=AdaptadorCnpqFalso(),
        registrar=lambda _: None,
    )

    assert [p.motivo for p in relatorio.pendencias] == [
        "planilha de grupos não encontrada",
        "planilha de projetos não encontrada",
        "planilha de bolsistas não encontrada",
        "nenhum currículo encontrado",
    ]


@contextmanager
def _conexao_falsa():
    yield MagicMock(name="conexao")


def test_flow_baixa_carrega_e_salva_relatorio(tmp_path):
    from src.flows.pipelines import horizon_postgres

    with (
        patch.object(horizon_postgres, "get_run_logger", return_value=MagicMock()),
        patch.object(horizon_postgres, "download_all_sigpesq_reports") as baixar,
        patch.object(horizon_postgres, "abrir_conexao", _conexao_falsa),
        patch.object(horizon_postgres, "executar_carga") as executar,
    ):
        caminho = horizon_postgres.pipeline_horizon_postgres.fn(
            campus_name="Serra", baixar_sigpesq=True, pasta_relatorio=str(tmp_path)
        )

    baixar.assert_called_once_with()
    configuracao = executar.call_args.args[2]
    assert configuracao.campus == "Serra"
    assert caminho.startswith(str(tmp_path))
    assert (tmp_path / "carga_postgres.json").exists()


def test_flow_salva_relatorio_mesmo_com_erro(tmp_path):
    from src.flows.pipelines import horizon_postgres

    with (
        patch.object(horizon_postgres, "get_run_logger", return_value=MagicMock()),
        patch.object(horizon_postgres, "download_all_sigpesq_reports") as baixar,
        patch.object(horizon_postgres, "abrir_conexao", _conexao_falsa),
        patch.object(
            horizon_postgres, "executar_carga", side_effect=RuntimeError("falhou")
        ),
    ):
        with pytest.raises(RuntimeError):
            horizon_postgres.pipeline_horizon_postgres.fn(
                baixar_sigpesq=False, pasta_relatorio=str(tmp_path)
            )

    baixar.assert_not_called()
    assert (tmp_path / "carga_postgres.json").exists()
