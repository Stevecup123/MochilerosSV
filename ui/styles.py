"""Estilos de la interfaz conversacional."""

import streamlit as st


def apply_visual_styles() -> None:
    """Aplica una identidad visual enfocada en la conversación."""
    st.markdown(
        """
        <style>
            :root {
                --background: #F8FAFA;
                --surface: #FFFFFF;
                --surface-secondary: #EEF7F7;
                --text-primary: #18302F;
                --text-secondary: #6B7A79;
                --primary: #087F8C;
                --primary-hover: #056B76;
                --border: #DCE7E6;
                --focus: #0A98A8;
            }

            .stApp { background: var(--background); color: var(--text-primary); font-family: Inter, ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif; }
            [data-testid="stHeader"] { background: transparent; }
            [data-testid="stToolbar"], #MainMenu, footer { visibility: hidden; }
            .block-container { max-width: 800px; min-height: 100vh; padding: 22px 28px 150px; }

            .brand-bar { align-items: center; border-bottom: 1px solid var(--border); display: flex; gap: 9px; margin-bottom: 12px; padding: 0 2px 14px; }
            .brand-mark { align-items: center; background: var(--primary); border-radius: 9px; color: white; display: inline-flex; font-size: 14px; height: 29px; justify-content: center; width: 29px; }
            .brand-name { color: var(--text-primary); font-size: 15px; font-weight: 720; letter-spacing: -0.02em; }
            .brand-context { color: var(--text-secondary); font-size: 12px; margin-left: auto; }
            .conversation-intro { color: var(--text-primary); margin: min(23vh, 188px) 0 14px; text-align: center; }
            .conversation-intro h1 { font-size: clamp(29px, 5vw, 42px); font-weight: 740; letter-spacing: -.045em; line-height: 1.05; margin: 0 0 12px; }
            .conversation-intro p { font-size: clamp(20px, 3vw, 27px); font-weight: 620; letter-spacing: -.03em; margin: 0 0 8px; }
            .conversation-intro span { color: var(--text-secondary); font-size: 15px; }
            .empty-conversation-marker { height: 0; }

            [data-testid="stChatMessage"] { background: transparent; border: 0; max-width: 690px; padding: 12px 0; }
            [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] { color: var(--text-primary); font-size: 16px; line-height: 1.6; }
            [data-testid="stChatMessage"] p { margin-bottom: .72rem; }
            [data-testid="stChatMessage"] li { margin-bottom: .28rem; }
            [data-testid="stChatMessage"] h1, [data-testid="stChatMessage"] h2, [data-testid="stChatMessage"] h3 { color: var(--text-primary); letter-spacing: -.02em; margin-top: 1rem; }
            [data-testid="stChatMessage"]:has(.message-role-marker.user) { background: #E3F3F3; border-radius: 18px 18px 5px 18px; margin-left: auto; max-width: 72%; padding: 11px 16px; }
            [data-testid="stChatMessage"]:has(.message-role-marker.assistant) { margin-right: auto; }
            .message-role-marker { display: none; }

            .st-key-composer_shell { background: var(--surface); border: 1px solid var(--border); border-radius: 18px; bottom: 14px; box-shadow: 0 4px 16px rgba(24, 48, 47, .08); margin-top: 22px; padding: 6px 8px; position: sticky; z-index: 10; }
            .st-key-composer_shell [data-testid="stHorizontalBlock"] { align-items: center; }
            .st-key-composer_shell [data-testid="stTextInputRootElement"] { background: transparent; border: 0; box-shadow: none; }
            .st-key-composer_shell [data-testid="stTextInputRootElement"]:focus-within { box-shadow: none; }
            .st-key-composer_shell input { color: var(--text-primary); font-size: 16px; }
            .st-key-composer_shell input::placeholder { color: var(--text-secondary); opacity: 1; }
            .st-key-composer_shell .st-key-voice_composer_action button, .st-key-composer_shell .st-key-composer_send button { border-radius: 11px; font-size: 18px; height: 42px; min-height: 42px; min-width: 42px; padding: 0; }
            .st-key-composer_shell .st-key-voice_composer_action button { background: var(--surface-secondary); border: 1px solid #B8DBDA; color: var(--primary); }
            .st-key-composer_shell .st-key-voice_composer_action button:hover { background: #D5EEEE; border-color: var(--primary); color: var(--primary-hover); }
            .composer-voice-state { align-items: center; color: var(--text-primary); display: flex; font-size: 15px; font-weight: 560; gap: 9px; height: 42px; padding: 0 10px; }
            .composer-voice-state.listening { color: #A8413B; }
            .composer-voice-state.processing { color: #9B641F; }
            .composer-voice-state.speaking { color: var(--primary); }
            .voice-error { color: #A8413B; font-size: 12px; margin: 8px auto 0; max-width: 760px; text-align: center; }
            .travel-note { color: var(--text-secondary); font-size: 12px; line-height: 1.45; margin: 8px auto 0; max-width: 760px; text-align: center; }
            button:focus-visible, [role="button"]:focus-visible, textarea:focus-visible { outline: 3px solid rgba(12, 157, 176, .35) !important; outline-offset: 2px; }

            @media (max-width: 640px) {
                .block-container { max-width: 100%; padding: 16px 16px 145px; }
                .brand-bar { margin-bottom: 14px; padding-bottom: 12px; }
                .brand-context { display: none; }
                .conversation-intro { margin-top: 19vh; }
                .conversation-intro span { font-size: 14px; }
                [data-testid="stChatMessage"]:has(.message-role-marker.user) { max-width: 86%; }
                .st-key-composer_shell { bottom: 8px; margin-top: 16px; padding: 5px 6px; }
                .st-key-composer_shell .st-key-voice_composer_action button, .st-key-composer_shell .st-key-composer_send button { min-width: 40px; }
            }

            @media (prefers-reduced-motion: reduce) {
                *, *::before, *::after { animation-duration: .01ms !important; scroll-behavior: auto !important; transition-duration: .01ms !important; }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
