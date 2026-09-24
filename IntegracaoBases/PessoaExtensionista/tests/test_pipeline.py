import json
import tempfile
import unittest
from pathlib import Path

from scripts.normalizacao import normalizar
from scripts.pipeline import BASELINE, cruzar, gerar_outputs


def _pessoa_ext(slug: str, tipo: str = "pontual") -> dict:
    return {
        "slug": slug,
        "nome": slug.replace("-", " ").title(),
        "origem": ["SRC", "DIRETORIA"],
        "tipo": tipo,
        "funcoes": [],
        "anos": None,
        "coordena": None,
        "equipe": None,
        "imp_coord": None,
        "imp_eq": None,
        "impacto": None,
        "atividades": None,
        "acoes": None,
    }


def _pessoa_hor(slug: str, classification: str = "researcher") -> dict:
    return {
        "slug": slug,
        "nome": slug.replace("-", " ").title(),
        "classification": classification,
        "campus": "Serra",
        "cnpq_url": None,
        "was_student": None,
        "was_staff": None,
    }


class CruzarTest(unittest.TestCase):
    def test_split_por_termos_e_motivo(self):
        ext = [
            _pessoa_ext("ana-da-silva"),
            _pessoa_ext("leticia-comissario-da-silva"),
            _pessoa_ext("fabricio"),
        ]
        hor = [
            _pessoa_hor("ana-da-silva"),
            _pessoa_hor("leticia-comissario-da-silva"),
            _pessoa_hor("fabricio"),
        ]
        r = cruzar(ext, hor)
        self.assertEqual(
            [m["slug"] for m in r["confirmados"]], ["leticia-comissario-da-silva"]
        )
        motivos = {m["slug"]: m["motivo"] for m in r["a_validar"]}
        self.assertEqual(
            motivos,
            {"ana-da-silva": "nome_curto_2_termos", "fabricio": "nome_curto_1_termo"},
        )

    def test_bloco_aninhado_sem_slug(self):
        r = cruzar(
            [_pessoa_ext("leticia-comissario-da-silva", tipo="catalogado")],
            [_pessoa_hor("leticia-comissario-da-silva")],
        )
        m = r["confirmados"][0]
        self.assertEqual(m["slug"], "leticia-comissario-da-silva")
        self.assertNotIn("slug", m["extensao"])
        self.assertNotIn("slug", m["horizon"])
        self.assertEqual(m["horizon"]["classification"], "researcher")
        self.assertEqual(m["extensao"]["tipo"], "catalogado")

    def test_exclusivos_e_br06(self):
        r = cruzar(
            [_pessoa_ext("ana-da-silva"), _pessoa_ext("sofia-alarcao")],
            [_pessoa_hor("ana-da-silva")],
        )
        self.assertEqual([p["slug"] for p in r["exclusivos_extensao"]], ["sofia-alarcao"])
        self.assertEqual([p["slug"] for p in r["exclusivos_horizon"]], [])
        self.assertEqual(r["a_validar"][0]["slug"], "ana-da-silva")
        self.assertNotIn(
            "ana-da-silva", [p["slug"] for p in r["exclusivos_extensao"]]
        )

    def test_duplicidade_gera_erro(self):
        with self.assertRaises(ValueError):
            cruzar(
                [_pessoa_ext("ana-silva")],
                [_pessoa_hor("ana-silva"), _pessoa_hor("ana-silva")],
            )


class IntegracaoPipelineRealTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.resumo = gerar_outputs(Path(cls.tmp.name))

    def test_universos(self):
        self.assertEqual(
            self.resumo["universos"],
            {
                "extensao_total": 914,
                "catalogados": 757,
                "pontuais": 157,
                "horizon_lidas": 10089,
                "horizon_validas": 10088,
                "horizon_invalidas": 1,
            },
        )

    def test_cruzamento_e_invariancias(self):
        c = self.resumo["cruzamento"]
        self.assertEqual(c["matches_confirmados"], 388)
        self.assertEqual(c["matches_a_validar"], 14)
        self.assertEqual(c["matches_confirmados"] + c["matches_a_validar"], 402)
        self.assertEqual(c["exclusivos_extensao"], 914 - 402)
        self.assertEqual(c["exclusivos_horizon"], 10088 - 402)

    def test_baseline_e_desvios(self):
        self.assertEqual(self.resumo["baseline_analise_consolidada"], BASELINE)
        metricas = {d["metrica"]: d["obtido"] for d in self.resumo["desvios"]}
        self.assertNotIn("matches_catalogados", metricas)
        self.assertEqual(metricas["total_matches"], 402)
        self.assertEqual(metricas["matches_pontuais"], 60)
        self.assertEqual(metricas["exclusivos_extensao"], 512)
        self.assertEqual(metricas["exclusivos_horizon"], 9686)
        for d in self.resumo["desvios"]:
            self.assertTrue(d["explicacao"])
            self.assertEqual(d["diferenca"], d["obtido"] - d["esperado"])

    def test_auditoria(self):
        aud = self.resumo["auditoria"]
        self.assertTrue(aud["slug_unico_extensao"])
        self.assertTrue(aud["slug_unico_horizon"])
        self.assertTrue(aud["cardinalidade_1_1"])
        self.assertEqual(aud["particulas_excluidas"], ["da", "das", "de", "do", "dos", "e"])
        self.assertEqual(len(aud["registros_invalidos_horizon"]), 1)
        self.assertEqual(aud["registros_invalidos_horizon"][0]["nome"], "-")

    def test_arquivos_gerados(self):
        pasta = Path(self.tmp.name)
        esperados = {
            "matches_confirmados.json",
            "matches_a_validar.json",
            "exclusivos_extensao.json",
            "exclusivos_horizon.json",
            "resumo_auditoria.json",
        }
        self.assertEqual({p.name for p in pasta.glob("*.json")}, esperados)
        texto = (pasta / "matches_confirmados.json").read_text(encoding="utf-8")
        self.assertIn("Vinícius", texto)
        confirmados = json.loads(texto)
        self.assertTrue(
            all("slug" in m and "slug" not in m["extensao"] and "slug" not in m["horizon"] for m in confirmados)
        )
        self.assertTrue(
            all(m["termo_count"] >= 3 for m in confirmados)
        )

    def test_idempotencia_dos_dados(self):
        with tempfile.TemporaryDirectory() as outro:
            resumo2 = gerar_outputs(Path(outro))
        r1 = {k: v for k, v in self.resumo.items() if k != "gerado_em"}
        r2 = {k: v for k, v in resumo2.items() if k != "gerado_em"}
        self.assertEqual(r1, r2)


if __name__ == "__main__":
    unittest.main()
