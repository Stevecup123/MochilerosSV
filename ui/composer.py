"""Composer único para texto y los estados visuales de voz."""

import streamlit as st

from components.composer_client import render_composer_client
from state.voice import ACTIVE_VOICE_STATES, VoiceState


_ACTIVE_VOICE_COPY = {
    VoiceState.CONNECTING: ("", "Preparando voz..."),
    VoiceState.LISTENING: ("🎙️", "Escuchando..."),
    VoiceState.PROCESSING: ("", "Procesando..."),
    VoiceState.SPEAKING: ("🔊", "Mochileros está respondiendo..."),
}


def render_composer(voice_state: VoiceState, voice_error: str | None = None) -> tuple[str | None, str | None]:
    """Mantiene un único composer y representa la voz dentro de él."""
    state_class = voice_state.value.lower()
    composer_event: dict | None = None
    voice_action: str | None = None

    with st.container(key="composer_shell"):
        if voice_state in ACTIVE_VOICE_STATES:
            text_column, action_column = st.columns([9, 1], gap="small", vertical_alignment="bottom")
            with text_column:
                icon, message = _ACTIVE_VOICE_COPY[voice_state]
                st.markdown(
                    f'<div class="composer-voice-state {state_class}">'
                    f'<span aria-hidden="true">{icon}</span>{message}</div>',
                    unsafe_allow_html=True,
                )
            with action_column:
                voice_action = "stop" if st.button("✕", key="voice_composer_action", help="Cerrar voz", use_container_width=True) else None
        else:
            composer_event = render_composer_client(st.session_state.active_conversation_id)

    if voice_error:
        st.markdown(f'<p class="voice-error">{voice_error}</p>', unsafe_allow_html=True)

    event_id = composer_event.get("event_id") if composer_event else None
    if event_id == st.session_state.get("composer_last_event_id"):
        composer_event = None
    elif isinstance(event_id, str):
        st.session_state.composer_last_event_id = event_id

    if composer_event and composer_event.get("event") == "submit":
        prompt = composer_event.get("text")
        return (prompt.strip() if isinstance(prompt, str) else None), voice_action
    if composer_event and composer_event.get("event") == "start_voice":
        voice_action = "start"
    return None, voice_action
