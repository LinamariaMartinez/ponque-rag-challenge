import unittest

from ingesta.chunking import dividir_en_fragmentos


class TestChunking(unittest.TestCase):
    def test_texto_vacio_no_produce_fragmentos(self):
        self.assertEqual(dividir_en_fragmentos(""), [])
        self.assertEqual(dividir_en_fragmentos("   "), [])

    def test_texto_corto_produce_un_fragmento(self):
        fragmentos = dividir_en_fragmentos("Texto corto de ejemplo.")
        self.assertEqual(fragmentos, ["Texto corto de ejemplo."])

    def test_texto_largo_produce_varios_fragmentos(self):
        parrafo = "Ponqué Ponqué Calarcá vende tortas. " * 60  # ~2200 caracteres
        fragmentos = dividir_en_fragmentos(parrafo)
        self.assertGreater(len(fragmentos), 1)
        for fragmento in fragmentos:
            self.assertLessEqual(len(fragmento), 900)
