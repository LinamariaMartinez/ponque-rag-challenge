"""Cliente delgado sobre OCI Generative AI: embeddings y chat con grounding.

Aísla el SDK de oci en un solo módulo para que el resto de la app no dependa
de sus tipos exactos ni de cómo está configurada la cuenta."""

import os

import oci
from oci.generative_ai_inference import GenerativeAiInferenceClient
from oci.generative_ai_inference.models import (
    ChatDetails,
    CohereChatRequest,
    EmbedTextDetails,
    OnDemandServingMode,
)

_cliente = None


def _obtener_cliente() -> GenerativeAiInferenceClient:
    global _cliente
    if _cliente is None:
        perfil = os.environ.get("OCI_CONFIG_PROFILE", "DEFAULT")
        configuracion = oci.config.from_file(profile_name=perfil)
        _cliente = GenerativeAiInferenceClient(
            config=configuracion,
            service_endpoint=os.environ["OCI_SERVICE_ENDPOINT"],
        )
    return _cliente


def embed_texts(textos: list[str]) -> list[list[float]]:
    """Genera un embedding por cada texto de entrada."""
    detalles = EmbedTextDetails(
        inputs=textos,
        serving_mode=OnDemandServingMode(
            model_id=os.environ.get("OCI_EMBED_MODEL_ID", "cohere.embed-multilingual-v3.0")
        ),
        compartment_id=os.environ["OCI_COMPARTMENT_ID"],
        truncate="END",
    )
    respuesta = _obtener_cliente().embed_text(detalles)
    return list(respuesta.data.embeddings)


def chat(pregunta: str, contexto: list[str]) -> str:
    """Genera una respuesta usando los fragmentos de contexto como grounding."""
    documentos = [{"snippet": fragmento} for fragmento in contexto]
    solicitud = CohereChatRequest(
        message=pregunta,
        documents=documentos,
        max_tokens=600,
        temperature=0.2,
        is_stream=False,
    )
    detalles = ChatDetails(
        serving_mode=OnDemandServingMode(
            model_id=os.environ.get("OCI_CHAT_MODEL_ID", "cohere.command-r-08-2024")
        ),
        chat_request=solicitud,
        compartment_id=os.environ["OCI_COMPARTMENT_ID"],
    )
    respuesta = _obtener_cliente().chat(detalles)
    return respuesta.data.chat_response.text
