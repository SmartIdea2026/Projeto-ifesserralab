import json

from src.core.logic.carga.relatorio import RelatorioCarga


def test_relatorio_conta_pula_e_descarta():
    relatorio = RelatorioCarga()

    relatorio.contar("grupos_sigpesq", "gravados", 3)
    relatorio.pular("grupos_sigpesq", "sem nome", "linha 7")
    relatorio.descartar("projetos_sigpesq", "valor_aprovado", 2)

    assert relatorio.contagens() == {
        "grupos_sigpesq": {"gravados": 3, "pulados": 1},
        "projetos_sigpesq": {"descartado:valor_aprovado": 2},
    }
    assert [p.motivo for p in relatorio.pendencias] == ["sem nome"]


def test_relatorio_salva_com_data_e_copia_mais_recente(tmp_path):
    relatorio = RelatorioCarga()
    relatorio.pular("cnpq", "URL já usada por outro grupo", "Grupo X")

    caminho = relatorio.salvar(str(tmp_path))

    assert caminho.startswith(str(tmp_path / "carga_postgres_"))
    for arquivo in (caminho, tmp_path / "carga_postgres.json"):
        dados = json.loads(open(arquivo, encoding="utf-8").read())
        assert dados["contagens"] == {"cnpq": {"pulados": 1}}
        assert dados["pendencias"] == [
            {
                "passo": "cnpq",
                "motivo": "URL já usada por outro grupo",
                "registro": "Grupo X",
            }
        ]


def test_relatorio_lista_itens_para_revisar(tmp_path):
    relatorio = RelatorioCarga()

    relatorio.revisar("enriquecimento_pj", "casado por título aproximado", "Projeto X")

    assert relatorio.contagens() == {"enriquecimento_pj": {"a_revisar": 1}}
    assert relatorio.resumo()["revisar"] == [
        {
            "passo": "enriquecimento_pj",
            "motivo": "casado por título aproximado",
            "registro": "Projeto X",
        }
    ]
