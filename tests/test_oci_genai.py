# tests/test_oci_genai.py
import os
import unittest
from unittest.mock import MagicMock, patch

from app import oci_genai


class TestOciGenai(unittest.TestCase):
    def setUp(self):
        oci_genai._cliente = None
        self.env_patch = patch.dict(os.environ, {
            "OCI_SERVICE_ENDPOINT": "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com",
            "OCI_COMPARTMENT_ID": "ocid1.compartment.oc1..test",
        })
        self.env_patch.start()

    def tearDown(self):
        self.env_patch.stop()
        oci_genai._cliente = None

    @patch("app.oci_genai._obtener_cliente")
    def test_embed_texts_devuelve_vectores(self, mock_obtener):
        cliente_falso = MagicMock()
        cliente_falso.embed_text.return_value.data.embeddings = [[0.1, 0.2], [0.3, 0.4]]
        mock_obtener.return_value = cliente_falso

        vectores = oci_genai.embed_texts(["texto uno", "texto dos"])

        self.assertEqual(vectores, [[0.1, 0.2], [0.3, 0.4]])
        cliente_falso.embed_text.assert_called_once()
        detalles = cliente_falso.embed_text.call_args.args[0]
        self.assertEqual(detalles.inputs, ["texto uno", "texto dos"])
        self.assertEqual(detalles.compartment_id, "ocid1.compartment.oc1..test")
        self.assertEqual(detalles.truncate, "END")

    @patch("app.oci_genai._obtener_cliente")
    def test_chat_devuelve_texto(self, mock_obtener):
        cliente_falso = MagicMock()
        cliente_falso.chat.return_value.data.chat_response.text = "Respuesta generada"
        mock_obtener.return_value = cliente_falso

        respuesta = oci_genai.chat("¿pregunta?", ["contexto uno"])

        self.assertEqual(respuesta, "Respuesta generada")
        cliente_falso.chat.assert_called_once()
        detalles = cliente_falso.chat.call_args.args[0]
        self.assertEqual(detalles.compartment_id, "ocid1.compartment.oc1..test")
        self.assertEqual(detalles.chat_request.message, "¿pregunta?")
        self.assertEqual(detalles.chat_request.documents, [{"snippet": "contexto uno"}])
