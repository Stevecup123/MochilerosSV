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
from ui.loading import dismiss_loading_screen, render_loading_screen
from ui.styles import apply_visual_styles


st.set_page_config(
    page_title="Mochileros SV",
    page_icon="🌎",
    layout="wide",
    # Streamlit abre el sidebar en escritorio y lo convierte en menú en pantallas pequeñas.
    initial_sidebar_state="auto",
)

# Se crea antes de cualquier inicialización potencialmente lenta. El CSS de la
# cubierta también la oculta por tiempo si la inicialización falla antes de retirarla.
loading_screen = render_loading_screen()

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
    """Actualiza una conversación sin perder su título personalizado."""
    messages = st.session_state.messages

    if not _has_user_messages(messages):
        return

    active_id = st.session_state.active_conversation_id

    if active_id is None:
        active_id = uuid4().hex
        st.session_state.active_conversation_id = active_id

    existing = next(
        (
            item
            for item in st.session_state.conversations
            if item["id"] == active_id
        ),
        None,
    )

    record = make_conversation(
        messages,
        active_id,
        existing["created_at"] if existing else None,
    )

    # Conservar el nombre personalizado si la conversación ya existe.
    if existing:
        record["title"] = existing["title"]

    st.session_state.conversations = [
        item
        for item in st.session_state.conversations
        if item["id"] != active_id
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


def rename_conversation(conversation_id: str, new_title: str) -> bool:
    """Cambia el título de una conversación y guarda el historial."""
    new_title = new_title.strip()

    if not new_title:
        return False

    for conversation in st.session_state.conversations:
        if conversation["id"] == conversation_id:
            conversation["title"] = new_title[:80]
            save_conversations(st.session_state.conversations)
            _sync_legacy_history()
            return True

    return False


def delete_conversation(conversation_id: str) -> None:
    """Elimina una conversación del historial guardado."""
    st.session_state.conversations = [
        conversation
        for conversation in st.session_state.conversations
        if conversation["id"] != conversation_id
    ]

    save_conversations(st.session_state.conversations)

    if st.session_state.active_conversation_id == conversation_id:
        st.session_state.messages = [
            {**WELCOME_MESSAGE, "message_id": uuid4().hex}
        ]
        st.session_state.active_conversation_id = uuid4().hex
        st.session_state.composer_text = ""
        st.session_state.selected_history_index = None
        _set_requested_conversation_id(None)

    st.session_state.rename_conversation_id = None
    _sync_legacy_history()

def render_sidebar() -> None:
    """Presenta el historial y las opciones de cada conversación."""
    with st.sidebar:
        st.session_state.setdefault("dark_mode", False)
        if not st.session_state.sidebar_open:
            return

        st.markdown(
            '<div class="sidebar-header"><span>Mochileros SV</span></div>',
            unsafe_allow_html=True,
        )

        
        theme_label = (
            "☀️  Cambiar a modo claro"
            if st.session_state.dark_mode
            else "🌙  Activar modo oscuro"
        )

        if st.button(
            theme_label,
            key="toggle_theme",
            use_container_width=True,
        ):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()


        if st.button("＋  Nuevo chat", key="new_conversation", use_container_width=True):
            st.session_state.rename_conversation_id = None
            start_new_conversation()
            st.rerun()

        with st.container(key="sidebar_history"):
            st.markdown(
                '<p class="sidebar-label">Historial</p>',
                unsafe_allow_html=True,
            )

            history = st.session_state.conversations
            st.session_state.setdefault("rename_conversation_id", None)

            if history:
                for conversation in history:
                    conversation_id = conversation["id"]
                    is_selected = (
                        st.session_state.active_conversation_id == conversation_id
                    )

                    title_column, menu_column = st.columns(
                        [0.88, 0.12],
                        gap="small",
                        vertical_alignment="center",
                    )

                    with title_column:
                        if st.button(
                            conversation["title"],
                            key=f"history_{conversation_id}",
                            type="primary" if is_selected else "secondary",
                            use_container_width=True,
                            help=conversation["title"],

                        ):
                            st.session_state.messages = _restore_messages(
                                conversation["messages"]
                            )
                            st.session_state.active_conversation_id = conversation_id
                            st.session_state.selected_history_index = next(
                                (
                                    index
                                    for index, item in enumerate(
                                        st.session_state.conversations
                                    )
                                    if item["id"] == conversation_id
                                ),
                                None,
                            )
                            st.session_state.rename_conversation_id = None
                            _set_requested_conversation_id(conversation_id)
                            _sync_legacy_history()
                            st.rerun()

                    with menu_column:
                        with st.popover(
                            "⋯",
                            help="Opciones del chat",
                            use_container_width=True,
                        ):
                            if st.button(
                                "✏️ Renombrar chat",
                                key=f"rename_{conversation_id}",
                                use_container_width=True,
                            ):
                                st.session_state.rename_conversation_id = conversation_id
                                st.session_state[
                                    f"rename_title_{conversation_id}"
                                ] = conversation["title"]
                                st.rerun()

                            if st.button(
                                "🗑️ Eliminar chat",
                                key=f"delete_{conversation_id}",
                                use_container_width=True,
                            ):
                                st.session_state.delete_confirmation_id = conversation_id
                                st.rerun()

                    if st.session_state.rename_conversation_id == conversation_id:
                        new_title = st.text_input(
                            "Nuevo nombre",
                            key=f"rename_title_{conversation_id}",
                            max_chars=80,
                        )

                        save_column, cancel_column = st.columns(2)

                        with save_column:
                            if st.button(
                                "Guardar",
                                key=f"save_rename_{conversation_id}",
                                use_container_width=True,
                            ):
                                if rename_conversation(conversation_id, new_title):
                                    st.session_state.rename_conversation_id = None
                                    st.rerun()
                                else:
                                    st.warning("Escribí un nombre para el chat.")

                        with cancel_column:
                            if st.button(
                                "Cancelar",
                                key=f"cancel_rename_{conversation_id}",
                                use_container_width=True,
                            ):
                                st.session_state.rename_conversation_id = None
                                st.rerun()

                    if st.session_state.get("delete_confirmation_id") == conversation_id:
                        st.warning(
                            f"¿Querés eliminar «{conversation['title']}»?"
                        )

                        confirm_column, cancel_column = st.columns(2)

                        with confirm_column:
                            if st.button(
                                "Sí, eliminar",
                                key=f"confirm_delete_{conversation_id}",
                                use_container_width=True,
                            ):
                                delete_conversation(conversation_id)
                                st.session_state.delete_confirmation_id = None
                                st.rerun()

                        with cancel_column:
                            if st.button(
                                "Cancelar",
                                key=f"cancel_delete_{conversation_id}",
                                use_container_width=True,
                            ):
                                st.session_state.delete_confirmation_id = None
                                st.rerun()

            else:
                st.markdown(
                    '<p class="sidebar-empty">No hay conversaciones todavía.</p>',
                    unsafe_allow_html=True,
                )

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
    """Muestra cada mensaje dentro de un bloque legible."""
    role = message["role"]

    with st.chat_message(role):
        st.markdown(
            f'<span class="message-role-marker {role}"></span>',
            unsafe_allow_html=True,
        )

        with st.container(border=True):
            st.markdown(message["content"])



def render_conversation() -> None:
    if not _has_user_messages(st.session_state.messages):
        st.markdown('<div class="empty-conversation-marker" aria-hidden="true"></div>', unsafe_allow_html=True)
        return
    for message in st.session_state.messages:
        render_message(message)



def render_suggestions() -> str | None:
    """Muestra destinos destacados y consultas rápidas."""

    st.markdown(
        '<div class="suggestions-label">Descubrí El Salvador</div>',
        unsafe_allow_html=True,
    )

    destinations = [
        {
            "name": "El Tunco",
            "icon": "🏖️",
            "description": "Playa, surf y atardeceres frente al mar.",
            "prompt": "Quiero conocer El Tunco",
            "style": "tunco",
            "image": "assets/destinos/Tunco.png",
        },

        {
            "name": "Ruta de las Flores",
            "icon": "🌺",
            "description": "Pueblos coloridos, café y gastronomía.",
            "prompt": "Planeame un viaje por la Ruta de las Flores",
            "style": "flores",
            "image": "assets/destinos/Ruta.png",

        },

                {
            "name": "Cerro Verde",
            "icon": "🌋",
            "description": "Naturaleza, senderos y vistas volcánicas.",
            "prompt": "¿Qué puedo hacer en Cerro Verde?",
            "style": "cerro",
            "image": "assets/destinos/Cerroverde.png",

        },
    ]

    columns = st.columns(3, gap="medium")

    for index, destination in enumerate(destinations):
        with columns[index]:
            st.image(
    destination["image"],
    use_container_width=True,
)
            st.markdown(
                f"""
                <div class="destination-card {destination['style']}">
                    <div class="destination-icon">{destination['icon']}</div>
                    <div class="destination-name">{destination['name']}</div>
                    <div class="destination-description">
                        {destination['description']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button(
                "Explorar destino ↗",
                key=f"destination_{index}",
                use_container_width=True,
            ):
                return destination["prompt"]

    st.markdown(
        '<div class="suggestions-label">¿Qué te gustaría planear?</div>',
        unsafe_allow_html=True,
    )

    suggestions = [
        "Recomendame lugares para visitar en El Salvador",
        "Buscame hoteles para un viaje",
        "¿Qué comidas típicas debería probar?",
        "Planeame un viaje de fin de semana",
    ]

    columns = st.columns(2, gap="small")

    for index, suggestion in enumerate(suggestions):
        with columns[index % 2]:
            if st.button(
                suggestion,
                key=f"suggestion_{index}",
                use_container_width=True,
            ):
                return suggestion

    return None



def respond_to_user(prompt: str) -> None:
    """Añade el mensaje y delega la respuesta al servicio conversacional."""
    prompt = prompt.strip()
    if not prompt:
        return

    st.session_state.messages.append(
        {
            "message_id": uuid4().hex,
            "role": "user",
            "content": prompt,
            "origin": "text",
        }
    )
    render_message({"role": "user", "content": prompt})

    requested_favorite = find_requested_favorite(prompt)

    if requested_favorite:
        was_added = add_favorite(requested_favorite)

        response = (
            f"¡Listo! Guardé **{requested_favorite}** en tus favoritos de esta sesión. ♥"
            if was_added
            else f"**{requested_favorite}** ya estaba en tus favoritos de esta sesión. ♥"
        )

        with st.chat_message("assistant"):
            with st.container(border=True):
                st.markdown(response)

        st.session_state.messages.append(
            {
                "message_id": uuid4().hex,
                "role": "assistant",
                "content": response,
                "origin": "text",
            }
        )

        persist_active_conversation()
        return

    with st.chat_message("assistant"):
        with st.container(border=True):
            with st.spinner("Pensando en una buena recomendación..."):
                try:
                    response = get_assistant_response(
                        llm,
                        st.session_state.messages,
                        build_travel_context(st.session_state.messages),
                    )
                    st.markdown(response)

                except Exception:
                    response = (
                        "Hubo un problema al procesar tu mensaje. "
                        "Intentá nuevamente."
                    )
                    st.error(response)

    st.session_state.messages.append(
        {
            "message_id": uuid4().hex,
            "role": "assistant",
            "content": response,
            "origin": "text",
        }
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
dismiss_loading_screen(loading_screen)

st.session_state.setdefault("dark_mode", False)
apply_visual_styles()

# Fondos turísticos: rotación en modo claro y fondo fijo en modo oscuro
if st.session_state.dark_mode:
    st.markdown(
    f'<span class="sidebar-state sidebar-{"open" if st.session_state.sidebar_open else "closed"}" aria-hidden="true"></span>',
    unsafe_allow_html=True,
)
else:
    st.markdown(
        """
        <div class="scenic-background scenic-beach" aria-hidden="true"></div>
        <div class="scenic-background scenic-forest" aria-hidden="true"></div>
        <div class="scenic-background scenic-village" aria-hidden="true"></div>
        """,
        unsafe_allow_html=True,
    )

# Fondos turísticos: rotación en modo claro y fondo fijo en modo oscuro
if st.session_state.dark_mode:
    st.markdown(
        '<div class="scenic-background scenic-night" aria-hidden="true"></div>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
        <div class="scenic-background scenic-beach" aria-hidden="true"></div>
        <div class="scenic-background scenic-forest" aria-hidden="true"></div>
        <div class="scenic-background scenic-village" aria-hidden="true"></div>
        """,
        unsafe_allow_html=True,
    )


initialize_interface_state()
dismiss_loading_screen(loading_screen)

st.session_state.setdefault("dark_mode", False)

apply_visual_styles()

if st.session_state.dark_mode:
    st.markdown(
        """
        <style>
        
        
/* Igualar el color de las opciones del menú en modo oscuro */
div[data-testid="stPopoverBody"] button,
div[data-testid="stPopoverBody"] button *,
div[data-baseweb="popover"] button,
div[data-baseweb="popover"] button * {
    color: #e5eee8 !important;
    -webkit-text-fill-color: #e5eee8 !important;
    opacity: 1 !important;
}


/* Botón de tema en modo oscuro */
section[data-testid="stSidebar"] .st-key-toggle_theme button {
    background: #285640 !important;
    color: #ffffff !important;
    border-color: #47775b !important;
    font-weight: 800 !important;
}

section[data-testid="stSidebar"] .st-key-toggle_theme button:hover {
    background: #356c4d !important;
}

/* Tres puntitos en modo oscuro */
section[data-testid="stSidebar"] [data-testid="stPopover"] > button {
    background: transparent !important;
    color: #e5eee8 !important;
    border-color: transparent !important;
    box-shadow: none !important;
    font-weight: 800 !important;
}

section[data-testid="stSidebar"] [data-testid="stPopover"] > button:hover {
    background: #285640 !important;
    color: #ffffff !important;
    border-color: #47775b !important;
}


        /* ===== Modo oscuro: fondo principal ===== */
        .stApp {
            background: #10251d !important;
            color: #e5eee8 !important;
        }

        [data-testid="stMain"] {
            background: #10251d !important;
        }

        /* ===== Barra lateral verde bosque ===== */
        section[data-testid="stSidebar"],
        section[data-testid="stSidebar"] > div:first-child {
            background: #173d2e !important;
        }

        section[data-testid="stSidebar"] .stButton button {
            color: #e5eee8 !important;
        }

        section[data-testid="stSidebar"] .stButton button:hover {
            background: #285640 !important;
        }

        section[data-testid="stSidebar"] .st-key-new_conversation button {
            background: #214b37 !important;
            border-color: #416b53 !important;
        }

        section[data-testid="stSidebar"] [class*="st-key-history_"] button[kind="primary"] {
            background: #315c43 !important;
            color: #ffffff !important;
        }

        .sidebar-header {
            color: #e5eee8 !important;
        }

        .sidebar-label,
        .sidebar-empty {
            color: #c0d4c7 !important;
        }

        /* ===== Barra superior ===== */
        .chat-topbar {
            border-color: #315442 !important;
        }

        .chat-topbar-title,
        .chat-topbar-status {
            color: #8bd5aa !important;
        }

        .chat-topbar-context {
            color: #b6c9bd !important;
        }

        /* ===== Tarjetas de conversación ===== */
        [data-testid="stChatMessage"]:has(.message-role-marker.assistant) {
            background: #19382b !important;
            border-color: #315442 !important;
            box-shadow: none !important;
        }

        [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"],
        [data-testid="stChatMessage"] p,
        [data-testid="stChatMessage"] li {
            color: #e5eee8 !important;
        }

        [data-testid="stChatMessage"]:has(.message-role-marker.user) {
            background: #244a37 !important;
            border-color: #39664d !important;
        }

        /* ===== Sugerencias ===== */
        .st-key-suggestion_0 button,
        .st-key-suggestion_1 button,
        .st-key-suggestion_2 button,
        .st-key-suggestion_3 button {
            background: #19382b !important;
            border-color: #315442 !important;
            color: #e5eee8 !important;
            box-shadow: none !important;
        }

        .st-key-suggestion_0 button:hover,
        .st-key-suggestion_1 button:hover,
        .st-key-suggestion_2 button:hover,
        .st-key-suggestion_3 button:hover {
            background: #285640 !important;
            border-color: #6eb98b !important;
            color: #ffffff !important;
        }

        .suggestions-label,
        .travel-note {
            color: #c0d4c7 !important;
        }

        /* ===== Tarjetas de destinos ===== */
        .destination-card,
        .destination-card.tunco,
        .destination-card.cerro,
        .destination-card.flores {
            background: #19382b !important;
            border-color: #315442 !important;
            box-shadow: none !important;
        }

        .destination-name {
            color: #8bd5aa !important;
        }

        .destination-description {
            color: #d0dfd5 !important;
        }

        .st-key-destination_0 button,
        .st-key-destination_1 button,
        .st-key-destination_2 button {
            background: #214b37 !important;
            border-color: #416b53 !important;
            color: #e5eee8 !important;
        }

        .st-key-destination_0 button:hover,
        .st-key-destination_1 button:hover,
        .st-key-destination_2 button:hover {
            background: #315c43 !important;
            color: #ffffff !important;
        }

        /* ===== Menús y formularios del historial ===== */
        


/* ===== Menú de los tres puntos: letras negras ===== */

div[data-baseweb="popover"],
div[data-baseweb="popover"] > div,
div[data-testid="stPopoverBody"],
div[data-testid="stPopoverBody"] > div {
    background-color: #19382b !important;
    color: #111111 !important;
}

/* Forzar letras negras en las opciones */
div[data-baseweb="popover"] button,
div[data-baseweb="popover"] button *,
div[data-testid="stPopoverBody"] button,
div[data-testid="stPopoverBody"] button *,
div[role="dialog"] button,
div[role="dialog"] button * {
    color: #111111 !important;
    -webkit-text-fill-color: #111111 !important;
    opacity: 1 !important;
    text-shadow: none !important;
}

/* Iconos visibles */
div[data-baseweb="popover"] svg,
div[data-testid="stPopoverBody"] svg,
div[role="dialog"] svg {
    color: #111111 !important;
    fill: currentColor !important;
    opacity: 1 !important;
}

/* Mantener las letras negras al pasar el cursor */
div[data-baseweb="popover"] button:hover,
div[data-testid="stPopoverBody"] button:hover,
div[role="dialog"] button:hover {
    background-color: #285640 !important;
    color: #111111 !important;
    -webkit-text-fill-color: #111111 !important;
}

/* Campo para renombrar con fondo blanco y texto negro */
section[data-testid="stSidebar"] input {
    background-color: #ffffff !important;
    color: #111111 !important;
    -webkit-text-fill-color: #111111 !important;
}


        section[data-testid="stSidebar"] input {
            background: #ffffff !important;
            color: #111111 !important;
            -webkit-text-fill-color: #111111 !important;
        }

        /* ===== Presentación: conservar letras verdosas ===== */
        .conversation-intro {
            background:
                radial-gradient(
                    ellipse at top right,
                    rgba(22, 132, 91, 0.13),
                    transparent 55%
                ),
                linear-gradient(135deg, #ffffff, #edf7ef) !important;
            border-color: #dce8df !important;
        }

        .conversation-intro h1 {
            color: #176b49 !important;
        }

        .conversation-intro p {
            color: #20352b !important;
        }

        .conversation-intro span {
            color: #718078 !important;
        }

        /* ===== Botón para abrir la barra lateral ===== */
        .st-key-open_sidebar button {
            background: #19382b !important;
            border-color: #315442 !important;
            color: #e5eee8 !important;
        }

        /* ===== Cuadro de escritura: siempre blanco ===== */
        .st-key-composer_shell {
            background: #ffffff !important;
            border-color: #315442 !important;
        }

        .st-key-composer_shell [data-testid="stTextArea"],
        .st-key-composer_shell div[data-baseweb="textarea"],
        .st-key-composer_shell textarea,
        .st-key-composer_shell input {
            background: #ffffff !important;
            color: #111111 !important;
            -webkit-text-fill-color: #111111 !important;
            caret-color: #111111 !important;
        }

        .st-key-composer_shell textarea::placeholder,
        .st-key-composer_shell input::placeholder {
            color: #707070 !important;
            -webkit-text-fill-color: #707070 !important;
        }

        .st-key-composer_shell .st-key-voice_composer_action button {
            color: #426650 !important;
        }

        .st-key-composer_shell .st-key-composer_send button {
            background: #16845b !important;
            color: #ffffff !important;
        }

        /* ===== Avisos y cuadros de diálogo ===== */
        [data-testid="stAlert"] {
            color: #e5eee8 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    f'<span class="sidebar-state sidebar-{"open" if st.session_state.sidebar_open else "closed"}" aria-hidden="true"></span>',
    unsafe_allow_html=True,
)
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
