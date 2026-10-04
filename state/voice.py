"""Contrato de estado conversacional y ciclo de sesión de voz."""

from enum import Enum
from uuid import uuid4

import streamlit as st


class VoiceState(str, Enum):
    IDLE = "IDLE"
    CONNECTING = "CONNECTING"
    LISTENING = "LISTENING"
    PROCESSING = "PROCESSING"
    SPEAKING = "SPEAKING"
    STOPPED = "STOPPED"
    ERROR = "ERROR"


ACTIVE_VOICE_STATES = frozenset({VoiceState.CONNECTING, VoiceState.LISTENING, VoiceState.PROCESSING, VoiceState.SPEAKING})

VOICE_STATE_DETAILS = {
    VoiceState.IDLE: ("Voz lista", "Podés activar el micrófono."),
    VoiceState.CONNECTING: ("Conectando voz", "Se está preparando una sesión segura."),
    VoiceState.LISTENING: ("Escuchando", "Podés hablar cuando estés listo."),
    VoiceState.PROCESSING: ("Procesando", "Se está procesando tu turno."),
    VoiceState.SPEAKING: ("Respondiendo", "Mochileros SV está respondiendo por voz."),
    VoiceState.STOPPED: ("Voz detenida", "Podés volver a activar el micrófono."),
    VoiceState.ERROR: ("Error de voz", "No se pudo continuar la sesión de voz."),
}

ALLOWED_TRANSITIONS = {
    VoiceState.IDLE: {VoiceState.CONNECTING, VoiceState.ERROR},
    VoiceState.CONNECTING: {VoiceState.LISTENING, VoiceState.STOPPED, VoiceState.ERROR},
    VoiceState.LISTENING: {VoiceState.PROCESSING, VoiceState.STOPPED, VoiceState.ERROR},
    VoiceState.PROCESSING: {VoiceState.SPEAKING, VoiceState.STOPPED, VoiceState.ERROR},
    VoiceState.SPEAKING: {VoiceState.LISTENING, VoiceState.STOPPED, VoiceState.ERROR},
    VoiceState.STOPPED: {VoiceState.IDLE, VoiceState.ERROR},
    VoiceState.ERROR: {VoiceState.IDLE},
}

_BROWSER_ERROR_EVENTS = {
    "MIC_NOT_SUPPORTED", "MIC_PERMISSION_DENIED", "MIC_INITIALIZATION_ERROR", "MIC_STOP_ERROR",
    "REALTIME_CREDENTIAL_ERROR", "REALTIME_CONNECTION_ERROR", "REALTIME_SDP_ERROR",
    "REALTIME_CLOSED_UNEXPECTEDLY", "REALTIME_SESSION_CONFIGURATION_ERROR", "REMOTE_AUDIO_ERROR",
    "VOICE_TRANSCRIPTION_ERROR", "VOICE_RESPONSE_ERROR",
}


def initialize_voice_state() -> None:
    """Inicializa estado serializable; los secretos se crean solo durante conexión."""
    defaults = {
        "voice_state": VoiceState.IDLE.value,
        "voice_component_command": "NOOP",
        "voice_component_command_revision": 0,
        "voice_browser_state": "permission_required",
        "voice_browser_error": None,
        "voice_last_browser_event_id": None,
        "voice_session_id": None,
        "voice_openai_session_id": None,
        "voice_turn_id": None,
        "voice_operation_id": None,
        "voice_generation": 0,
        "voice_client_secret": None,
        "voice_client_secret_generation": None,
        "voice_openai_turns": {},
        "voice_confirmed_user_items": set(),
        "voice_confirmed_assistant_items": set(),
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_voice_state() -> VoiceState:
    try:
        return VoiceState(st.session_state.voice_state)
    except ValueError:
        st.session_state.voice_state = VoiceState.ERROR.value
        return VoiceState.ERROR


def transition_voice_state(next_state: VoiceState) -> bool:
    current_state = get_voice_state()
    if next_state not in ALLOWED_TRANSITIONS[current_state]:
        return False
    _set_voice_state(next_state)
    return True


def request_microphone_access() -> bool:
    """Inicia un ciclo técnico de voz, sin crear turnos conversacionales."""
    current_state = get_voice_state()
    if current_state in {VoiceState.STOPPED, VoiceState.ERROR}:
        transition_voice_state(VoiceState.IDLE)
        current_state = VoiceState.IDLE
    if current_state != VoiceState.IDLE or not transition_voice_state(VoiceState.CONNECTING):
        return False

    st.session_state.voice_generation += 1
    st.session_state.voice_session_id = uuid4().hex
    st.session_state.voice_operation_id = uuid4().hex
    st.session_state.voice_turn_id = None
    st.session_state.voice_openai_session_id = None
    st.session_state.voice_openai_turns = {}
    st.session_state.voice_confirmed_user_items = set()
    st.session_state.voice_confirmed_assistant_items = set()
    st.session_state.voice_browser_error = None
    _clear_client_secret()
    _issue_component_command("START_MIC")
    return True


def request_microphone_stop() -> bool:
    """Invalida la sesión y ordena cerrar recursos del navegador."""
    if get_voice_state() not in ACTIVE_VOICE_STATES:
        return False

    _set_voice_state(VoiceState.STOPPED)
    _clear_client_secret()
    st.session_state.voice_generation += 1
    st.session_state.voice_session_id = None
    st.session_state.voice_openai_session_id = None
    st.session_state.voice_operation_id = None
    st.session_state.voice_turn_id = None
    st.session_state.voice_openai_turns = {}
    st.session_state.voice_confirmed_user_items = set()
    st.session_state.voice_confirmed_assistant_items = set()
    _issue_component_command("STOP_SESSION")
    return True


def stage_realtime_client_secret(client_secret: str) -> bool:
    """Conserva brevemente la credencial efímera para el único render que la consume."""
    if get_voice_state() != VoiceState.CONNECTING:
        return False
    st.session_state.voice_client_secret = client_secret
    st.session_state.voice_client_secret_generation = st.session_state.voice_generation
    _issue_component_command("CONNECT_REALTIME")
    return True


def fail_voice_session(message: str) -> None:
    """Muestra un error seguro, invalida resultados previos y cierra el navegador."""
    st.session_state.voice_browser_error = message
    already_stopping = (
        get_voice_state() == VoiceState.ERROR
        and st.session_state.voice_component_command == "STOP_SESSION"
    )
    _set_voice_state(VoiceState.ERROR)
    _clear_client_secret()
    _clear_voice_turn_references()
    st.session_state.voice_session_id = None
    st.session_state.voice_openai_session_id = None
    st.session_state.voice_operation_id = None
    st.session_state.voice_openai_turns = {}
    st.session_state.voice_confirmed_user_items = set()
    st.session_state.voice_confirmed_assistant_items = set()
    if already_stopping:
        return
    st.session_state.voice_generation += 1
    _issue_component_command("STOP_SESSION")


def handle_browser_voice_event(event_data: dict) -> str | None:
    """Acepta eventos solo si pertenecen a la generación vigente."""
    event_id = event_data.get("browser_event_id")
    if not isinstance(event_id, str) or event_id == st.session_state.voice_last_browser_event_id:
        return None

    event_generation = event_data.get("voice_generation")
    current_generation = st.session_state.voice_generation
    if isinstance(event_generation, int) and event_generation >= 0 and event_generation != current_generation:
        return None

    event_revision = event_data.get("command_revision")
    current_revision = st.session_state.voice_component_command_revision
    if isinstance(event_revision, int) and event_revision >= 0 and event_revision < current_revision:
        return None

    st.session_state.voice_last_browser_event_id = event_id
    browser_state = event_data.get("browser_voice_state")
    if isinstance(browser_state, str):
        st.session_state.voice_browser_state = browser_state

    event = event_data.get("event")
    if event == "REALTIME_CREDENTIAL_CONSUMED":
        _clear_client_secret()
    elif event in {"REALTIME_SESSION_CONFIGURED", "REALTIME_CONNECTED"}:
        if get_voice_state() == VoiceState.CONNECTING:
            transition_voice_state(VoiceState.LISTENING)
        openai_session_id = event_data.get("openai_session_id")
        if isinstance(openai_session_id, str):
            st.session_state.voice_openai_session_id = openai_session_id
    elif event == "VOICE_TURN_STARTED" and get_voice_state() == VoiceState.LISTENING:
        turn_id = uuid4().hex
        st.session_state.voice_turn_id = turn_id
        openai_item_id = event_data.get("openai_item_id")
        if isinstance(openai_item_id, str):
            st.session_state.voice_openai_turns[openai_item_id] = turn_id
    elif event == "VOICE_TURN_ENDED" and get_voice_state() == VoiceState.LISTENING:
        transition_voice_state(VoiceState.PROCESSING)
    elif event in {"VOICE_RESPONSE_STARTED", "VOICE_RESPONSE_AUDIO_STARTED"}:
        if get_voice_state() == VoiceState.PROCESSING:
            transition_voice_state(VoiceState.SPEAKING)
    elif event == "VOICE_RESPONSE_INTERRUPTED" and get_voice_state() == VoiceState.SPEAKING:
        transition_voice_state(VoiceState.LISTENING)
        _clear_voice_turn_references()
    elif event == "VOICE_USER_TRANSCRIPT_FINAL":
        _append_confirmed_voice_message(event_data, "user")
    elif event == "VOICE_ASSISTANT_TRANSCRIPT_FINAL":
        _append_confirmed_voice_message(event_data, "assistant")
    elif event == "VOICE_RESPONSE_DONE":
        assistant_voice_message = event_data.get("assistant_voice_message")
        if isinstance(assistant_voice_message, dict):
            _append_confirmed_voice_message(assistant_voice_message, "assistant")
        if get_voice_state() == VoiceState.SPEAKING:
            transition_voice_state(VoiceState.LISTENING)
        _clear_voice_turn_references()
    elif event == "MIC_STOPPED" and get_voice_state() in ACTIVE_VOICE_STATES:
        _set_voice_state(VoiceState.STOPPED)
    elif event in _BROWSER_ERROR_EVENTS:
        fail_voice_session(event_data.get("detail") or "No se pudo iniciar la conversación por voz.")

    return event if isinstance(event, str) else None


def _clear_client_secret() -> None:
    st.session_state.voice_client_secret = None
    st.session_state.voice_client_secret_generation = None


def _set_voice_state(state: VoiceState) -> None:
    st.session_state.voice_state = state.value


def _clear_voice_turn_references() -> None:
    """Descarta el vínculo del turno terminado sin perder deduplicación de la sesión."""
    turn_id = st.session_state.voice_turn_id
    if turn_id:
        st.session_state.voice_openai_turns = {
            item_id: saved_turn_id
            for item_id, saved_turn_id in st.session_state.voice_openai_turns.items()
            if saved_turn_id != turn_id
        }
    st.session_state.voice_turn_id = None


def _issue_component_command(command: str) -> None:
    st.session_state.voice_component_command = command
    st.session_state.voice_component_command_revision += 1


def _append_confirmed_voice_message(event_data: dict, role: str) -> bool:
    """Agrega una vez cada transcripción final, identificada por OpenAI."""
    text = event_data.get("transcript")
    openai_item_id = event_data.get("openai_item_id")
    if not isinstance(text, str) or not text.strip() or not isinstance(openai_item_id, str):
        return False

    content_index = event_data.get("content_index", 0)
    if role == "user":
        key = f"{openai_item_id}:{content_index}"
        confirmed = st.session_state.voice_confirmed_user_items
    else:
        response_id = event_data.get("openai_response_id")
        if not isinstance(response_id, str):
            return False
        key = f"{response_id}:{openai_item_id}:{content_index}"
        confirmed = st.session_state.voice_confirmed_assistant_items

    if key in confirmed:
        return False
    confirmed.add(key)
    st.session_state.messages.append(
        {
            "message_id": uuid4().hex,
            "role": role,
            "content": text.strip(),
            "origin": "voice",
            "voice_turn_id": st.session_state.voice_openai_turns.get(openai_item_id),
            "openai_item_id": openai_item_id,
            **({"openai_response_id": response_id} if role == "assistant" else {}),
        }
    )
    return True
