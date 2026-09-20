"""Configuración no sensible y carga segura de secretos."""

import os

import streamlit as st
from dotenv import load_dotenv


MODEL_NAME = "gpt-4o-mini"
MODEL_TEMPERATURE = 0.7
REALTIME_MODEL_NAME = "gpt-realtime-2.1"
REALTIME_OUTPUT_VOICE = "marin"
REALTIME_TRANSCRIPTION_MODEL = "gpt-4o-mini-transcribe"
REALTIME_TRANSCRIPTION_LANGUAGE = "es"
REALTIME_VAD_CONFIG = {
    "type": "server_vad",
    "threshold": 0.5,
    "prefix_padding_ms": 300,
    "silence_duration_ms": 700,
    # El navegador solicita una sola respuesta tras el commit confirmado por VAD.
    "create_response": False,
    "interrupt_response": False,
}


def get_openai_api_key() -> str | None:
    """Obtiene la clave desde .env o, en despliegue, Streamlit Secrets."""
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        try:
            api_key = st.secrets["OPENAI_API_KEY"]
        except (FileNotFoundError, KeyError):
            pass

    return api_key
