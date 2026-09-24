import unittest
from collections import Counter

from scripts.extracao_horizon import carregar_horizon, parse_campus
from scripts.validacoes import slugs_duplicados


class ParseCampusTest(unittest.TestCase):
    def test_string_json(self):
        self.assertEqual(parse_campus('{"id": 6, "name": "Serra"}'), "Serra")

    def test_dict(self):
        self.assertEqual(parse_campus({"id": 6, "name": "Serra"}), "Serra")

    def test_none(self):
        self.assertIsNone(parse_campus(None))

    def test_nan(self):
        self.assertIsNone(parse_campus(float("nan")))

    def test_nome_vazio_no_json(self):
        self.assertIsNone(parse_campus('{"id": 6, "name": ""}'))

    def test_formato_inesperado_gera_erro(self):
        with self.assertRaises(ValueError):
            parse_campus(42)


class IntegracaoHorizonRealTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validos, cls.invalidos = carregar_horizon(ignorar_invalidos=True)

    def test_total_valido_10088_e_um_invalido(self):
        self.assertEqual(len(self.validos), 10088)
        self.assertEqual(len(self.invalidos), 1)
        self.assertEqual(self.invalidos[0]["nome"], "-")

    def test_padrao_e_fail_fast(self):
        with self.assertRaises(ValueError):
            carregar_horizon()

    def test_distribuicao_classification(self):
        contagem = Counter(p["classification"] for p in self.validos)
        self.assertEqual(
            dict(contagem),
            {"student": 6519, "researcher": 2472, "outside_ifes": 849, None: 248},
        )

    def test_campos_e_tipos(self):
        chaves = {
            "slug",
            "nome",
            "classification",
            "campus",
            "cnpq_url",
            "was_student",
            "was_staff",
        }
        for p in self.validos:
            self.assertEqual(set(p), chaves)
            self.assertIsInstance(p["campus"], (str, type(None)))
            self.assertIn(p["was_student"], (True, False, None))
            self.assertIn(p["was_staff"], (True, False, None))
            self.assertIn(
                p["classification"], ("researcher", "student", "outside_ifes", None)
            )
        self.assertEqual(slugs_duplicados(self.validos), {})


if __name__ == "__main__":
    unittest.main()
