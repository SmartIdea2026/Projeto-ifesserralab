import unittest

from scripts.normalizacao import contar_termos, normalizar


class NormalizarTest(unittest.TestCase):
    def test_remove_acentos_e_espacos_viram_hifen(self):
        self.assertEqual(normalizar("Letícia Comissário da Silva"), "leticia-comissario-da-silva")

    def test_mantem_particulas(self):
        self.assertEqual(
            normalizar("Juliana Yuri Kanezaki De Souza"),
            "juliana-yuri-kanezaki-de-souza",
        )

    def test_colapsa_especiais_e_hifens_multiplos(self):
        self.assertEqual(normalizar("José  O'Brien-Netto"), "jose-o-brien-netto")

    def test_minusculas_e_trim(self):
        self.assertEqual(normalizar("  MARIA DA SILVA  "), "maria-da-silva")

    def test_nome_simples(self):
        self.assertEqual(normalizar("Ana"), "ana")

    def test_cedilha_e_til(self):
        self.assertEqual(normalizar("José Conceição Nunes Júnior"), "jose-conceicao-nunes-junior")

    def test_nome_vazio_gera_erro(self):
        with self.assertRaises(ValueError):
            normalizar("   ")

    def test_none_gera_erro(self):
        with self.assertRaises(ValueError):
            normalizar(None)

    def test_so_especiais_gera_erro(self):
        with self.assertRaises(ValueError):
            normalizar("--- *** ---")


class ContarTermosTest(unittest.TestCase):
    def test_dois_termos_com_particula(self):
        self.assertEqual(contar_termos("ana-da-silva"), 2)

    def test_tres_termos_com_particula(self):
        self.assertEqual(contar_termos("leticia-comissario-da-silva"), 3)

    def test_um_termo(self):
        self.assertEqual(contar_termos("ana"), 1)

    def test_somente_particulas(self):
        self.assertEqual(contar_termos("da-do-e"), 0)

    def test_hifens_multiplos(self):
        self.assertEqual(contar_termos("ana--silva"), 2)

    def test_slug_vazio_gera_erro(self):
        with self.assertRaises(ValueError):
            contar_termos("")

    def test_none_gera_erro(self):
        with self.assertRaises(ValueError):
            contar_termos(None)

    def test_nome_bruto_com_espaco_gera_erro(self):
        with self.assertRaises(ValueError):
            contar_termos("Ana da Silva")


if __name__ == "__main__":
    unittest.main()
