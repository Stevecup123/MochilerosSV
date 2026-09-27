"""Composer único para texto y los estados visuales de voz."""

import streamlit as st

from state.voice import ACTIVE_VOICE_STATES, VoiceState


_ACTIVE_VOICE_COPY = {
    VoiceState.CONNECTING: ("", "Preparando voz..."),
    VoiceState.LISTENING: ("🎙️", "Escuchando..."),
    VoiceState.PROCESSING: ("", "Procesando..."),
    VoiceState.SPEAKING: ("🔊", "Mochileros está respondiendo..."),
}


def _submit_text_from_composer() -> None:
    """Guarda el texto antes de que Streamlit limpie el campo del composer."""
    prompt = st.session_state.get("composer_text", "").strip()
    if prompt:
        st.session_state.composer_pending_prompt = prompt
    st.session_state.composer_text = ""


def render_composer(voice_state: VoiceState, voice_error: str | None = None) -> tuple[str | None, str | None]:
    """Mantiene un único composer y representa la voz dentro de él."""
    state_class = voice_state.value.lower()
    if st.session_state.pop("composer_clear_after_submit", False):
        st.session_state.composer_text = ""

    with st.container(key="composer_shell"):
        text_column, voice_column, send_column = st.columns([8, 1.05, 1], gap="small", vertical_alignment="bottom")
        with text_column:
            if voice_state in ACTIVE_VOICE_STATES:
                icon, message = _ACTIVE_VOICE_COPY[voice_state]
                st.markdown(
                    f'<div class="composer-voice-state {state_class}">'
                    f'<span aria-hidden="true">{icon}</span>{message}</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.text_area(
                    "Mensaje",
                    key="composer_text",
                    placeholder="Contame qué lugar de El Salvador querés descubrir...",
                    label_visibility="collapsed",
                    height=68,
                    on_change=_submit_text_from_composer,
                )

        with voice_column:
            if voice_state in ACTIVE_VOICE_STATES:
                voice_action = "stop" if st.button("✕", key="voice_composer_action", help="Cerrar voz", use_container_width=True) else None
            elif voice_state == VoiceState.STOPPED:
                voice_action = "start" if st.button("🎙️", key="voice_composer_action", help="Reanudar voz", use_container_width=True) else None
            else:
                voice_action = "start" if st.button("🎙️", key="voice_composer_action", help="Hablar con Mochileros", use_container_width=True) else None

        with send_column:
            send_pressed = st.button("➤", key="composer_send", help="Enviar mensaje", type="primary", use_container_width=True)
            if send_pressed:
                prompt = st.session_state.get("composer_text", "").strip()
                if prompt:
                    st.session_state.composer_clear_after_submit = True

    if voice_error:
        st.markdown(f'<p class="voice-error">{voice_error}</p>', unsafe_allow_html=True)

    if send_pressed and prompt:
        return prompt, voice_action
    return st.session_state.pop("composer_pending_prompt", None), voice_action
