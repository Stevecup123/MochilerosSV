import streamlit as st
from uuid import uuid4
from html import escape

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
from state.travel import add_favorite, build_travel_context, find_requested_favorite, initialize_travel_state
from ui.composer import render_composer
from ui.styles import apply_visual_styles


st.set_page_config(
    page_title="Mochileros SV",
    page_icon="🌎",
    layout="wide",
    # Streamlit abre el sidebar en escritorio y lo convierte en menú en pantallas pequeñas.
    initial_sidebar_state="auto",
)

WELCOME_MESSAGE = {
    "role": "assistant",
    "content": (
        "¡Hola! 👋 Soy **Mochileros SV**, tu guía para descubrir El Salvador.\n\n"
        "Contame qué tenés en mente: una playa, montaña, pueblo, "
        "comida típica o un plan completo. ¡De una lo armamos! 🌋🏖️"
    ),
    "origin": "text",
}


def render_top_bar() -> None:
    st.markdown(
        """
        <div class="chat-topbar">
            <div>
                <span class="chat-topbar-title">Mochileros SV</span>
                <span class="chat-topbar-context">Tu compañero para descubrir El Salvador</span>
            </div>
            <span class="chat-topbar-status"><i></i> Disponible</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _conversation_title(messages: list[dict[str, str]]) -> str:
    """Genera una etiqueta breve para el historial local de la sesión."""
    for message in messages:
        if message["role"] == "user":
            return message["content"].replace("\n", " ").strip()[:38] or "Nueva conversación"
    return "Nueva conversación"


def start_new_conversation() -> None:
    """Archiva la conversación visible y prepara un chat vacío en esta sesión."""
    messages = st.session_state.messages
    if any(message["role"] == "user" for message in messages):
        st.session_state.conversation_history.insert(
            0, {"title": _conversation_title(messages), "messages": [message.copy() for message in messages]}
        )
    st.session_state.messages = [{**WELCOME_MESSAGE, "message_id": uuid4().hex}]
    st.session_state.composer_text = ""


def render_sidebar() -> None:
    """Agrupa navegación, historial y favoritos sin alterar el estado de viaje."""
    with st.sidebar:
        st.markdown(
            """<div class="sidebar-brand"><span class="sidebar-mark">⌁</span>
            <span>Mochileros <b>SV</b></span></div>""",
            unsafe_allow_html=True,
        )
        if st.button("＋  Nueva conversación", key="new_conversation", use_container_width=True):
            start_new_conversation()
            st.rerun()

        st.markdown('<p class="sidebar-label">HISTORIAL</p>', unsafe_allow_html=True)
        history = st.session_state.conversation_history
        if history:
            for index, conversation in enumerate(history[:6]):
                if st.button(f"◷  {conversation['title']}", key=f"history_{index}", use_container_width=True):
                    st.session_state.messages = [message.copy() for message in conversation["messages"]]
                    st.rerun()
        else:
            st.markdown('<p class="sidebar-empty">Tus conversaciones aparecerán aquí.</p>', unsafe_allow_html=True)

        st.markdown('<p class="sidebar-label favorites-label">FAVORITOS</p>', unsafe_allow_html=True)
        destination_column, save_column = st.columns([4, 1], vertical_alignment="bottom")
        with destination_column:
            destination = st.text_input(
                "Destino favorito", key="favorite_destination_input",
                placeholder="Ej. Suchitoto", label_visibility="collapsed",
            )
        with save_column:
            if st.button("Guardar", key="save_favorite", use_container_width=True):
                if add_favorite(destination):
                    st.rerun()
                elif destination.strip():
                    st.caption("Ese destino ya está en tus favoritos.")
        favorites = st.session_state.favorite_destinations
        if favorites:
            st.markdown(
                " ".join(f"<span class='favorite-chip'>♥ {escape(item)}</span>" for item in favorites),
                unsafe_allow_html=True,
            )
        else:
            st.markdown('<p class="sidebar-empty">Guardá tus destinos favoritos.</p>', unsafe_allow_html=True)

        st.markdown(
            """<div class="sidebar-user"><span class="sidebar-avatar">U</span><span>
            <strong>Viajero</strong><small>Sesión actual</small></span></div>""",
            unsafe_allow_html=True,
        )


def initialize_messages() -> None:
    """Conserva el historial de la sesión y el saludo original del asistente."""
    if "messages" not in st.session_state:
        st.session_state.messages = [{**WELCOME_MESSAGE, "message_id": uuid4().hex}]

    st.session_state.setdefault("conversation_history", [])

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


def render_suggestions() -> str | None:
    """Muestra inicios rápidos que usan exactamente el mismo flujo de mensajes."""
    suggestions = (
        "Recomendame lugares para visitar en El Salvador",
        "Quiero conocer El Tunco",
        "¿Qué puedo hacer en Cerro Verde?",
        "Planeame un viaje de fin de semana",
    )
    st.markdown('<div class="suggestions-label">Empezá con una idea</div>', unsafe_allow_html=True)
    columns = st.columns(2, gap="small")
    for index, suggestion in enumerate(suggestions):
        with columns[index % 2]:
            if st.button(suggestion, key=f"suggestion_{index}", use_container_width=True):
                return suggestion
    return None


def respond_to_user(prompt: str) -> None:
    """Añade el mensaje y delega la respuesta al servicio conversacional."""
    prompt = prompt.strip()
    if not prompt:
        return

    st.session_state.messages.append(
        {"message_id": uuid4().hex, "role": "user", "content": prompt, "origin": "text"}
    )
    render_message({"role": "user", "content": prompt})

    requested_favorite = find_requested_favorite(prompt)
    if requested_favorite:
        was_added = add_favorite(requested_favorite)
        response = (
            f"¡Listo! Guardé **{requested_favorite}** en tus favoritos de esta sesión. ♥"
            if was_added else f"**{requested_favorite}** ya estaba en tus favoritos de esta sesión. ♥"
        )
        with st.chat_message("assistant"):
            st.markdown('<span class="message-role-marker assistant"></span>', unsafe_allow_html=True)
            st.markdown(response)
        st.session_state.messages.append(
            {"message_id": uuid4().hex, "role": "assistant", "content": response, "origin": "text"}
        )
        return

    with st.chat_message("assistant"):
        st.markdown('<span class="message-role-marker assistant"></span>', unsafe_allow_html=True)
        with st.spinner("Pensando en una buena recomendación..."):
            try:
                response = get_assistant_response(
                    llm, st.session_state.messages, build_travel_context(st.session_state.messages)
                )
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
initialize_travel_state()
initialize_voice_state()
apply_visual_styles()
render_sidebar()
render_top_bar()
suggestion_prompt = None
if len(st.session_state.messages) == 1:
    st.markdown(
        '''<section class="conversation-intro">
            <h1>Mochileros SV</h1>
            <p>¿A dónde querés viajar?</p>
            <span>Tu compañero para descubrir El Salvador.</span>
        </section>''',
        unsafe_allow_html=True,
    )
    suggestion_prompt = render_suggestions()
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

if suggestion_prompt or prompt:
    respond_to_user(suggestion_prompt or prompt)
    st.rerun()

st.markdown(
    '<div class="travel-note"></div>',
    unsafe_allow_html=True,
)
