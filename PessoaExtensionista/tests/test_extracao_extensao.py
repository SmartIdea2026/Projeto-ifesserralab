import json
import tempfile
import unittest
from pathlib import Path

from scripts.extracao_extensao import (
    contagens,
    extrair_catalogados,
    extrair_coordenacoes_acoes,
    extrair_pessoas_extensao,
    extrair_pontuais,
)
from scripts.normalizacao import normalizar


def _escrever_json(caminho: Path, dado) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(json.dumps(dado, ensure_ascii=False), encoding="utf-8")


def _montar_src(
    raiz: Path,
    catalogados: list[dict],
    atividades: dict,
    acoes: dict | None = None,
) -> tuple[Path, Path, Path]:
    _escrever_json(raiz / "api" / "extensionistas" / "index.json", catalogados)
    pasta_atividades = raiz / "api" / "atividades"
    pasta_atividades.mkdir(parents=True, exist_ok=True)
    for atividade_id, conteudo in atividades.items():
        _escrever_json(pasta_atividades / f"{atividade_id}.json", conteudo)
    pasta_acoes = raiz / "api" / "acoes"
    pasta_acoes.mkdir(parents=True, exist_ok=True)
    for acao_id, conteudo in (acoes or {}).items():
        _escrever_json(pasta_acoes / f"{acao_id}.json", conteudo)
    return (
        raiz / "api" / "extensionistas" / "index.json",
        pasta_atividades,
        pasta_acoes,
    )


def _item_catalogado(nome: str) -> dict:
    return {
        "slug": normalizar(nome),
        "nome": nome,
        "funcoes": ["ALUNO(A) VOLUNTARIO"],
        "anos": ["2020"],
        "coordena": 0,
        "equipe": 1,
        "imp_coord": 0,
        "imp_eq": 0,
        "impacto": 0,
    }


class ExtracaoCatalogadosTest(unittest.TestCase):
    def test_registro_catalogado_completo(self):
        with tempfile.TemporaryDirectory() as tmp:
            index, _, _ = _montar_src(Path(tmp), [_item_catalogado("Ana Silva")], {})
            pessoas = extrair_catalogados(index)
        self.assertEqual(len(pessoas), 1)
        registro = pessoas[0]
        self.assertEqual(registro["slug"], "ana-silva")
        self.assertEqual(registro["nome"], "Ana Silva")
        self.assertEqual(registro["origem"], ["SRC", "DIRETORIA"])
        self.assertEqual(registro["tipo"], "catalogado")
        self.assertEqual(registro["funcoes"], ["ALUNO(A) VOLUNTARIO"])
        self.assertEqual(registro["anos"], ["2020"])
        self.assertEqual(registro["coordena"], 0)
        self.assertEqual(registro["equipe"], 1)
        self.assertEqual(registro["impacto"], 0)
        self.assertIsNone(registro["atividades"])
        self.assertIsNone(registro["acoes"])

    def test_slug_duplicado_gera_erro(self):
        with tempfile.TemporaryDirectory() as tmp:
            index, _, _ = _montar_src(
                Path(tmp), [_item_catalogado("Ana Silva"), _item_catalogado("Ana Silva")], {}
            )
            with self.assertRaises(ValueError):
                extrair_catalogados(index)


class ExtracaoPontuaisTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        raiz = Path(self.tmp.name)
        catalogados = [_item_catalogado("Ana Silva")]
        atividades = {
            "1": {
                "atividade_id": "1",
                "coordenador_acao": "Ana Silva",
                "equipe_execucao": [
                    {"nome": "Carla Dias", "funcao": "MENTOR(A)", "vinculo": "Servidor"},
                    {"nome": "Carla Dias", "funcao": "MONITOR(A)", "vinculo": "Servidor"},
                ],
            },
            "2": {
                "atividade_id": "2",
                "coordenador_acao": "Carla Dias",
                "equipe_execucao": [
                    {"nome": "Duda Rocha", "funcao": "  ", "vinculo": "Externo"}
                ],
            },
        }
        index, pasta, _ = _montar_src(raiz, catalogados, atividades)
        self.catalogados = extrair_catalogados(index)
        self.pontuais = extrair_pontuais({p["slug"] for p in self.catalogados}, pasta)
        self.por_slug = {p["slug"]: p for p in self.pontuais}

    def test_deduplicado_por_slug(self):
        self.assertEqual(set(self.por_slug), {"carla-dias", "duda-rocha"})
        carla = self.por_slug["carla-dias"]
        self.assertEqual(carla["funcoes"], ["MENTOR(A)", "MONITOR(A)"])
        self.assertEqual(carla["atividades"], ["1", "2"])
        self.assertEqual(carla["nome"], "Carla Dias")

    def test_campos_nao_aplicaveis_null(self):
        carla = self.por_slug["carla-dias"]
        self.assertEqual(carla["tipo"], "pontual")
        for campo in ["anos", "coordena", "equipe", "imp_coord", "imp_eq", "impacto"]:
            self.assertIsNone(carla[campo])
        self.assertEqual(carla["origem"], ["SRC", "DIRETORIA"])

    def test_coordenador_sem_funcao_tem_funcoes_vazias(self):
        duda = self.por_slug["duda-rocha"]
        self.assertEqual(duda["funcoes"], [])
        self.assertEqual(duda["atividades"], ["2"])

    def test_catalogado_citado_em_atividade_nao_vira_pontual(self):
        self.assertNotIn("ana-silva", set(self.por_slug))


class CoordenacoesAcoesTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        raiz = Path(self.tmp.name)
        catalogados = [_item_catalogado("Ana Silva"), _item_catalogado("Beto Almeida")]
        atividades = {
            "1": {
                "atividade_id": "1",
                "coordenador_acao": "Carla Dias",
                "equipe_execucao": [],
            }
        }
        acoes = {
            "10": {"acao_id": "10", "Coordenador(a)": "Beto Almeida"},
            "11": {"acao_id": "11", "Coordenador(a)": "Carla Dias"},
            "12": {"acao_id": "12", "Coordenador(a)": "Erico Fontes"},
            "13": {"acao_id": "13", "Coordenador(a)": "  "},
        }
        self.index, self.pasta_atividades, self.pasta_acoes = _montar_src(
            raiz, catalogados, atividades, acoes
        )

    def test_mapa_de_coordenacoes(self):
        mapa = extrair_coordenacoes_acoes(self.pasta_acoes)
        self.assertEqual(
            {s: sorted(v["acoes"]) for s, v in mapa.items()},
            {"beto-almeida": ["10"], "carla-dias": ["11"], "erico-fontes": ["12"]},
        )
        self.assertEqual(mapa["erico-fontes"]["nome"], "Erico Fontes")

    def test_regra_uniforme_acoes_na_composicao(self):
        pessoas = extrair_pessoas_extensao(Path(self.tmp.name))
        por_slug = {p["slug"]: p for p in pessoas}
        self.assertEqual(por_slug["beto-almeida"]["acoes"], ["10"])
        self.assertIsNone(por_slug["ana-silva"]["acoes"])
        carla = por_slug["carla-dias"]
        self.assertEqual(carla["tipo"], "pontual")
        self.assertEqual(carla["atividades"], ["1"])
        self.assertEqual(carla["acoes"], ["11"])
        erico = por_slug["erico-fontes"]
        self.assertEqual(erico["tipo"], "pontual")
        self.assertIsNone(erico["atividades"])
        self.assertEqual(erico["acoes"], ["12"])
        self.assertEqual(erico["funcoes"], [])


class ComposicaoExtensaoTest(unittest.TestCase):
    def test_contagens(self):
        pessoas = [{"tipo": "catalogado"}, {"tipo": "catalogado"}, {"tipo": "pontual"}]
        self.assertEqual(contagens(pessoas), {"total": 3, "catalogados": 2, "pontuais": 1})


class IntegracaoExtensaoRealTest(unittest.TestCase):
    def test_bases_reais_914(self):
        pessoas = extrair_pessoas_extensao()
        self.assertEqual(
            contagens(pessoas), {"total": 914, "catalogados": 757, "pontuais": 157}
        )

    def test_coordenadores_de_acoes(self):
        pessoas = extrair_pessoas_extensao()
        por_slug = {p["slug"]: p for p in pessoas}
        com_acoes = [p for p in pessoas if p["acoes"]]
        self.assertEqual(len(com_acoes), 68)
        for slug in [
            "alexander-jeferson-nassau-borges",
            "cibelle-zanforlin-cesconetto-toresani",
            "livia-de-azevedo-silveira-rangel",
        ]:
            self.assertEqual(por_slug[slug]["tipo"], "pontual")
            self.assertIsNone(por_slug[slug]["atividades"])
            self.assertTrue(por_slug[slug]["acoes"])


if __name__ == "__main__":
    unittest.main()
