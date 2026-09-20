import streamlit as st
from uuid import uuid4

from config.settings import (
    MODEL_NAME,
    MODEL_TEMPERATURE,
    REALTIME_MODEL_NAME,
    REALTIME_OUTPUT_VOICE,
    REALTIME_TRANSCRIPTION_LANGUAGE,
    REALTIME_TRANSCRIPTION_MODEL,
    REALTIME_VAD_CONFIG,
    get_openai_api_key,
)
from components.voice_client import render_voice_client
from services.conversation import SYSTEM_PROMPT, create_conversation_service, get_assistant_response
from services.realtime_session import RealtimeCredentialError, create_realtime_client_secret
from state.voice import (
    fail_voice_session,
    get_voice_state,
    handle_browser_voice_event,
    initialize_voice_state,
    request_microphone_access,
    request_microphone_stop,
    stage_realtime_client_secret,
)
from ui.composer import render_composer
from ui.styles import apply_visual_styles


st.set_page_config(
    page_title="Mochileros SV",
    page_icon="🌎",
    layout="centered",
    initial_sidebar_state="collapsed",
)


def render_brand() -> None:
    st.markdown(
        """
        <div class="brand-bar">
            <span class="brand-mark" aria-hidden="true">✦</span>
            <span class="brand-name">Mochileros SV</span>
            <span class="brand-context">Tu compañero para descubrir El Salvador</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def initialize_messages() -> None:
    """Conserva el historial de la sesión y el saludo original del asistente."""
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "¡Hola! 👋 Soy **Mochileros SV**, tu guía para descubrir El Salvador.\n\n"
                    "Contame qué tenés en mente: una playa, montaña, pueblo, "
                    "comida típica o un plan completo. ¡De una lo armamos! 🌋🏖️"
                ),
                "message_id": uuid4().hex,
                "origin": "text",
            }
        ]

    for message in st.session_state.messages:
        message.setdefault("message_id", uuid4().hex)
        message.setdefault("origin", "text")


def render_message(message: dict[str, str]) -> None:
    """Renderiza un mensaje del historial con el estilo de su rol."""
    with st.chat_message(message["role"]):
        st.markdown(
            f'<span class="message-role-marker {message["role"]}"></span>',
            unsafe_allow_html=True,
        )
        st.markdown(message["content"])


def render_conversation() -> None:
    if len(st.session_state.messages) == 1:
        st.markdown('<div class="empty-conversation-marker" aria-hidden="true"></div>', unsafe_allow_html=True)
        return
    for message in st.session_state.messages:
        render_message(message)


def respond_to_user(prompt: str) -> None:
    """Añade el mensaje y delega la respuesta al servicio conversacional."""
    prompt = prompt.strip()
    if not prompt:
        return

    st.session_state.messages.append(
        {"message_id": uuid4().hex, "role": "user", "content": prompt, "origin": "text"}
    )
    render_message({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        st.markdown('<span class="message-role-marker assistant"></span>', unsafe_allow_html=True)
        with st.spinner("Pensando en una buena recomendación..."):
            try:
                response = get_assistant_response(llm, st.session_state.messages)
                st.markdown(response)
            except Exception:
                response = "Hubo un problema al procesar tu mensaje. Intentá nuevamente."
                st.error(response)

    st.session_state.messages.append(
        {"message_id": uuid4().hex, "role": "assistant", "content": response, "origin": "text"}
    )


api_key = get_openai_api_key()
if not api_key:
    st.error(
        "No se encontró OPENAI_API_KEY. "
        "Configurá tu clave en el archivo .env o en los Secrets de Streamlit."
    )
    st.stop()

llm = create_conversation_service(api_key, MODEL_NAME, MODEL_TEMPERATURE)

initialize_messages()
initialize_voice_state()
apply_visual_styles()
render_brand()
if len(st.session_state.messages) == 1:
    st.markdown(
        '''<section class="conversation-intro">
            <h1>Mochileros SV</h1>
            <p>¿A dónde querés viajar?</p>
            <span>Tu compañero para descubrir El Salvador.</span>
        </section>''',
        unsafe_allow_html=True,
    )
render_conversation()

browser_event = render_voice_client(
    st.session_state.voice_component_command,
    st.session_state.voice_component_command_revision,
    st.session_state.voice_generation,
    st.session_state.voice_client_secret,
    {
        "model": REALTIME_MODEL_NAME,
        "voice": REALTIME_OUTPUT_VOICE,
        "instructions": SYSTEM_PROMPT,
        "transcription_model": REALTIME_TRANSCRIPTION_MODEL,
        "transcription_language": REALTIME_TRANSCRIPTION_LANGUAGE,
        "turn_detection": REALTIME_VAD_CONFIG,
    },
    st.session_state.messages,
)
if browser_event:
    browser_event_name = handle_browser_voice_event(browser_event)
    if browser_event_name == "MIC_READY":
        try:
            credential = create_realtime_client_secret(
                api_key,
                REALTIME_MODEL_NAME,
                REALTIME_OUTPUT_VOICE,
            )
            stage_realtime_client_secret(credential.value)
        except RealtimeCredentialError as error:
            fail_voice_session(str(error))
    if browser_event_name:
        st.rerun()

prompt, voice_action = render_composer(get_voice_state(), st.session_state.voice_browser_error)

if voice_action == "start" and request_microphone_access():
    st.rerun()
if voice_action == "stop" and request_microphone_stop():
    st.rerun()

if prompt:
    respond_to_user(prompt)
    st.rerun()

st.markdown(
    '<div class="travel-note"></div>',
    unsafe_allow_html=True,
)
