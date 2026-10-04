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
from services.conversation_storage import load_conversations, make_conversation, save_conversations
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

_ACTIVE_CONVERSATION_QUERY_PARAM = "conversation_id"


def initialize_interface_state() -> None:
    """Conserva las preferencias estrictamente visuales durante la sesión."""
    st.session_state.setdefault("sidebar_open", True)
    st.session_state.setdefault("selected_history_index", None)


def render_top_bar() -> None:
    """Muestra un control para recuperar la navegación si está oculta."""
    toggle_column, title_column = st.columns([0.55, 12], gap="small", vertical_alignment="center")
    with toggle_column:
        if not st.session_state.sidebar_open and st.button(
            "☰", key="open_sidebar", help="Abrir barra lateral"
        ):
            st.session_state.sidebar_open = True
            st.rerun()
    with title_column:
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


def _has_user_messages(messages: list[dict]) -> bool:
    return any(message.get("role") == "user" and message.get("content", "").strip() for message in messages)


def _restore_messages(messages: list[dict[str, str]]) -> list[dict[str, str]]:
    """Restaura mensajes persistidos y genera IDs solo para la interfaz actual."""
    return [{**message, "message_id": uuid4().hex, "origin": "text"} for message in messages]


def _get_requested_conversation_id() -> str | None:
    """Lee el chat que el navegador debe recuperar después de un refresh."""
    value = st.query_params.get(_ACTIVE_CONVERSATION_QUERY_PARAM)
    return value if isinstance(value, str) and value else None


def _set_requested_conversation_id(conversation_id: str | None) -> None:
    """Mantiene en la URL solo la identidad del chat activo, nunca sus mensajes."""
    if conversation_id:
        st.query_params[_ACTIVE_CONVERSATION_QUERY_PARAM] = conversation_id
    else:
        st.query_params.pop(_ACTIVE_CONVERSATION_QUERY_PARAM, None)


def _sync_legacy_history() -> None:
    """Mantiene la clave anterior disponible durante esta transición de interfaz."""
    active_id = st.session_state.active_conversation_id
    st.session_state.conversation_history = [
        {"title": conversation["title"], "messages": _restore_messages(conversation["messages"])}
        for conversation in st.session_state.conversations
        if conversation["id"] != active_id
    ]


def persist_active_conversation() -> None:
    """Actualiza una sola conversación activa, sin crear duplicados por mensaje."""
    messages = st.session_state.messages
    if not _has_user_messages(messages):
        return

    active_id = st.session_state.active_conversation_id
    if active_id is None:
        active_id = uuid4().hex
        st.session_state.active_conversation_id = active_id
    existing = next((item for item in st.session_state.conversations if item["id"] == active_id), None)
    record = make_conversation(messages, active_id, existing["created_at"] if existing else None)
    st.session_state.conversations = [
        item for item in st.session_state.conversations if item["id"] != active_id
    ]
    st.session_state.conversations.insert(0, record)
    save_conversations(st.session_state.conversations)
    _set_requested_conversation_id(active_id)
    _sync_legacy_history()


def start_new_conversation() -> None:
    """Guarda el chat activo y prepara un borrador vacío con identidad propia."""
    persist_active_conversation()
    st.session_state.messages = [{**WELCOME_MESSAGE, "message_id": uuid4().hex}]
    st.session_state.composer_text = ""
    st.session_state.selected_history_index = None
    st.session_state.active_conversation_id = uuid4().hex
    _set_requested_conversation_id(None)
    _sync_legacy_history()


def render_sidebar() -> None:
    """Presenta navegación mínima reutilizando el historial ya existente."""
    with st.sidebar:
        if not st.session_state.sidebar_open:
            return

        st.markdown(
            """<div class="sidebar-header"><span>Mochileros SV</span></div>""",
            unsafe_allow_html=True,
        )
        if st.button("＋  Nuevo chat", key="new_conversation", use_container_width=True):
            start_new_conversation()
            st.rerun()

        with st.container(key="sidebar_history"):
            st.markdown('<p class="sidebar-label">Historial</p>', unsafe_allow_html=True)
            history = st.session_state.conversations
            if history:
                for index, conversation in enumerate(history):
                    is_selected = st.session_state.active_conversation_id == conversation["id"]
                    if st.button(
                        conversation["title"],
                        key=f"history_{index}",
                        type="primary" if is_selected else "secondary",
                        use_container_width=True,
                    ):
                        st.session_state.messages = _restore_messages(conversation["messages"])
                        st.session_state.active_conversation_id = conversation["id"]
                        st.session_state.selected_history_index = index
                        _set_requested_conversation_id(conversation["id"])
                        _sync_legacy_history()
                        st.rerun()
            else:
                st.markdown('<p class="sidebar-empty">No hay conversaciones todavía.</p>', unsafe_allow_html=True)

def initialize_messages() -> None:
    """Prepara un borrador vacío para una sesión nueva."""
    if "messages" not in st.session_state:
        st.session_state.messages = []

    st.session_state.setdefault("conversation_history", [])

    for message in st.session_state.messages:
        message.setdefault("message_id", uuid4().hex)
        message.setdefault("origin", "text")


def initialize_conversation_storage() -> None:
    """Carga el historial local una vez y migra el historial temporal previo."""
    if "conversations" not in st.session_state:
        conversations = load_conversations()
        known_ids = {conversation["id"] for conversation in conversations}
        for legacy_conversation in st.session_state.conversation_history:
            legacy_messages = legacy_conversation.get("messages", [])
            if _has_user_messages(legacy_messages):
                migrated = make_conversation(legacy_messages)
                if migrated["id"] not in known_ids:
                    conversations.append(migrated)
        st.session_state.conversations = sorted(
            conversations, key=lambda conversation: conversation["updated_at"], reverse=True
        )
        if st.session_state.conversations:
            save_conversations(st.session_state.conversations)

    if "active_conversation_id" not in st.session_state:
        requested_id = _get_requested_conversation_id()
        requested_conversation = next(
            (conversation for conversation in st.session_state.conversations if conversation["id"] == requested_id),
            None,
        )
        if requested_conversation:
            # F5 conserva el ID en la URL y recupera exactamente ese chat, no el último.
            st.session_state.active_conversation_id = requested_conversation["id"]
            st.session_state.messages = _restore_messages(requested_conversation["messages"])
        else:
            # Una apertura sin ID de chat muestra el borrador inicial limpio.
            st.session_state.active_conversation_id = None
            if requested_id:
                _set_requested_conversation_id(None)
        if _has_user_messages(st.session_state.messages) and not any(
            conversation["id"] == st.session_state.active_conversation_id
            for conversation in st.session_state.conversations
        ):
            persist_active_conversation()
    _sync_legacy_history()


def render_message(message: dict[str, str]) -> None:
    """Renderiza un mensaje del historial con el estilo de su rol."""
    with st.chat_message(message["role"]):
        st.markdown(
            f'<span class="message-role-marker {message["role"]}"></span>',
            unsafe_allow_html=True,
        )
        st.markdown(message["content"])


def render_conversation() -> None:
    if not _has_user_messages(st.session_state.messages):
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
        persist_active_conversation()
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
    persist_active_conversation()


api_key = get_openai_api_key()
if not api_key:
    st.error(
        "No se encontró OPENAI_API_KEY. "
        "Configurá tu clave en el archivo .env o en los Secrets de Streamlit."
    )
    st.stop()

llm = create_conversation_service(api_key, MODEL_NAME, MODEL_TEMPERATURE)

initialize_messages()
initialize_conversation_storage()
initialize_travel_state()
initialize_voice_state()
initialize_interface_state()
st.markdown(
    f'<span class="sidebar-state sidebar-{"open" if st.session_state.sidebar_open else "closed"}" aria-hidden="true"></span>',
    unsafe_allow_html=True,
)
apply_visual_styles()
render_sidebar()
render_top_bar()
suggestion_prompt = None
if not _has_user_messages(st.session_state.messages):
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
        persist_active_conversation()
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
