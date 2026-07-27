import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


class TestChatEndpoint(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    @patch("app.main.generar_respuesta")
    @patch("app.main.buscar")
    def test_responde_con_fuentes(self, mock_buscar, mock_generar):
        mock_buscar.return_value = [
            {"texto": "15 días hábiles al año.", "archivo": "politica-vacaciones.docx", "area": "rh"}
        ]
        mock_generar.return_value = "Tienes 15 días hábiles de vacaciones al año."

        respuesta = self.client.post("/chat", json={"pregunta": "¿Cuántos días de vacaciones tengo?"})

        self.assertEqual(respuesta.status_code, 200)
        cuerpo = respuesta.json()
        self.assertIn("15 días hábiles", cuerpo["respuesta"])
        self.assertIn("politica-vacaciones.docx — rh", cuerpo["fuentes"])

    @patch("app.main.buscar")
    def test_sin_documentos_indexados(self, mock_buscar):
        mock_buscar.return_value = []

        respuesta = self.client.post("/chat", json={"pregunta": "cualquier cosa"})

        self.assertEqual(respuesta.status_code, 200)
        self.assertIn("indexar_documentos.py", respuesta.json()["respuesta"])

    @patch("app.main.generar_respuesta")
    @patch("app.main.buscar")
    def test_error_del_servicio_ia(self, mock_buscar, mock_generar):
        mock_buscar.return_value = [{"texto": "algo", "archivo": "a.md", "area": "calidad"}]
        mock_generar.side_effect = Exception("timeout")

        respuesta = self.client.post("/chat", json={"pregunta": "¿algo?"})

        self.assertEqual(respuesta.status_code, 200)
        self.assertIn("No pude conectar", respuesta.json()["respuesta"])

    def test_pagina_principal_carga(self):
        respuesta = self.client.get("/")
        self.assertEqual(respuesta.status_code, 200)

    def test_pregunta_demasiado_larga_devuelve_422(self):
        respuesta = self.client.post("/chat", json={"pregunta": "a" * 501})
        self.assertEqual(respuesta.status_code, 422)
