"""Estilos de la interfaz conversacional."""

import streamlit as st


def apply_visual_styles() -> None:
    """Aplica una identidad visual enfocada en la conversación."""
    st.markdown(
        """
        <style>
            :root {
                --background: #212121;
                --surface: #292929;
                --surface-secondary: #303030;
                --sidebar: #171717;
                --text-primary: #F5F5F5;
                --text-secondary: #A0A0A0;
                --primary: #20B8B7;
                --primary-hover: #5AD1CB;
                --border: #3A3A3A;
                --focus: #20B8B7;
            }

            .stApp { background: var(--background); color: var(--text-primary); font-family: Inter, ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif; }
            [data-testid="stHeader"] { background: transparent; }
            [data-testid="stToolbar"], #MainMenu, footer { visibility: hidden; }
            .block-container { max-width: 920px; min-height: 100vh; padding: 20px 36px 156px; }
            [data-testid="stSidebar"] { background: var(--sidebar); border-right: 1px solid #292929; min-width: 270px !important; max-width: 270px !important; }
            [data-testid="stSidebar"] > div:first-child { display: flex; flex-direction: column; min-height: 100vh; padding: 14px 12px; width: 270px !important; }
            [data-testid="stSidebar"] .block-container { padding: 0; }
            [data-testid="stSidebar"] .stButton button { background: transparent; border: 1px solid transparent; color: #CECECE; font-size: 14px; font-weight: 500; justify-content: flex-start; min-height: 38px; padding: 0 10px; text-align: left; }
            [data-testid="stSidebar"] .stButton button:hover { background: #292929; border-color: #343434; color: white; }
            [data-testid="stSidebar"] .st-key-new_conversation button { background: #252525; border-color: #3C3C3C; color: var(--text-primary); font-weight: 650; margin: 14px 0 19px; }
            [data-testid="stSidebar"] .st-key-new_conversation button:hover { background: #303030; border-color: #555; }
            .sidebar-brand { align-items: center; color: #F6F6F6; display: flex; font-size: 17px; font-weight: 620; gap: 9px; letter-spacing: -.025em; padding: 7px 8px; }
            .sidebar-brand b { color: var(--primary); font-weight: 740; }
            .sidebar-mark { align-items: center; background: #163E40; border: 1px solid #276164; border-radius: 9px; color: #70E1DB; display: inline-flex; font-size: 21px; height: 29px; justify-content: center; width: 29px; }
            .sidebar-label { color: #7E7E7E; font-size: 10px; font-weight: 750; letter-spacing: .1em; margin: 0 9px 7px; }
            .favorites-label { border-top: 1px solid #303030; margin-top: 21px; padding-top: 20px; }
            .sidebar-empty { color: #777; font-size: 12px; line-height: 1.45; margin: 0 10px; }
            .sidebar-user { align-items: center; border-top: 1px solid #303030; color: #DDD; display: flex; gap: 9px; margin-top: auto; padding: 16px 8px 4px; }
            .sidebar-user strong, .sidebar-user small { display: block; font-size: 12px; font-weight: 600; }
            .sidebar-user small { color: #777; font-size: 11px; font-weight: 400; margin-top: 2px; }
            .sidebar-avatar { align-items: center; background: #333; border: 1px solid #484848; border-radius: 50%; color: #DDD; display: inline-flex; font-size: 12px; height: 29px; justify-content: center; width: 29px; }

            .chat-topbar { align-items: center; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; margin-bottom: 12px; min-height: 42px; padding: 0 2px 13px; }
            .chat-topbar-title { color: var(--text-primary); display: block; font-size: 15px; font-weight: 690; letter-spacing: -.02em; }
            .chat-topbar-context { color: var(--text-secondary); display: block; font-size: 12px; margin-top: 2px; }
            .chat-topbar-status { align-items: center; color: #8E8E8E; display: flex; font-size: 11px; gap: 6px; }
            .chat-topbar-status i { background: #36C28B; border-radius: 50%; display: inline-block; height: 6px; width: 6px; }
            .conversation-intro { color: var(--text-primary); margin: min(23vh, 188px) 0 14px; text-align: center; }
            .conversation-intro h1 { font-size: clamp(29px, 5vw, 42px); font-weight: 740; letter-spacing: -.045em; line-height: 1.05; margin: 0 0 12px; }
            .conversation-intro p { font-size: clamp(20px, 3vw, 27px); font-weight: 620; letter-spacing: -.03em; margin: 0 0 8px; }
            .conversation-intro span { color: var(--text-secondary); font-size: 15px; }
            .empty-conversation-marker { height: 0; }
            .suggestions-label { color: var(--text-secondary); font-size: 12px; margin: 28px auto 9px; max-width: 620px; text-align: left; }
            .st-key-suggestion_0 button, .st-key-suggestion_1 button, .st-key-suggestion_2 button, .st-key-suggestion_3 button { background: #292929; border: 1px solid var(--border); border-radius: 12px; color: #D9D9D9; font-size: 13px; line-height: 1.35; min-height: 54px; padding: 9px 13px; text-align: left; }
            .st-key-suggestion_0 button:hover, .st-key-suggestion_1 button:hover, .st-key-suggestion_2 button:hover, .st-key-suggestion_3 button:hover { background: #303030; border-color: #555; color: white; }
            .favorite-chip { background: #203B3C; border: 1px solid #35676A; border-radius: 999px; color: #CDEEEE; display: inline-block; font-size: 11px; margin: 7px 4px 0 0; padding: 4px 8px; }
            [data-testid="stSidebar"] [data-testid="stTextInputRootElement"] { background: #252525; border-color: #3A3A3A; border-radius: 9px; }
            [data-testid="stSidebar"] input { color: #EEE; font-size: 12px; }
            [data-testid="stSidebar"] .st-key-save_favorite button { color: var(--primary); min-height: 36px; padding: 0; text-align: center; }

            [data-testid="stChatMessage"] { background: transparent; border: 0; max-width: 740px; padding: 13px 0; }
            [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] { color: var(--text-primary); font-size: 16px; line-height: 1.6; }
            [data-testid="stChatMessage"] p { margin-bottom: .72rem; }
            [data-testid="stChatMessage"] li { margin-bottom: .28rem; }
            [data-testid="stChatMessage"] h1, [data-testid="stChatMessage"] h2, [data-testid="stChatMessage"] h3 { color: var(--text-primary); letter-spacing: -.02em; margin-top: 1rem; }
            [data-testid="stChatMessage"]:has(.message-role-marker.user) { background: #303030; border: 1px solid #3C3C3C; border-radius: 18px 18px 5px 18px; margin-left: auto; max-width: 72%; padding: 11px 16px; }
            [data-testid="stChatMessage"]:has(.message-role-marker.assistant) { margin-right: auto; }
            .message-role-marker { display: none; }

            .st-key-composer_shell { background: #2B2B2B; border: 1px solid #444; border-radius: 18px; bottom: 14px; box-shadow: 0 10px 28px rgba(0, 0, 0, .22); box-sizing: border-box; left: calc(50% + 135px); margin: 0; max-width: 790px; padding: 6px 8px 6px 13px; position: fixed; transform: translateX(-50%); width: min(790px, calc(100vw - 334px)); z-index: 10; }
            .st-key-composer_shell [data-testid="stHorizontalBlock"] { align-items: end; flex-wrap: nowrap !important; }
            .st-key-composer_shell [data-testid="stColumn"] { min-width: 0 !important; width: auto !important; }
            .st-key-composer_shell [data-testid="stColumn"]:first-child { flex: 1 1 auto !important; }
            .st-key-composer_shell [data-testid="stColumn"]:nth-child(2), .st-key-composer_shell [data-testid="stColumn"]:nth-child(3) { flex: 0 0 42px !important; }
            .st-key-composer_shell [data-testid="stTextArea"] { background: transparent; border: 0; }
            .st-key-composer_shell [data-testid="stTextArea"]:focus-within { box-shadow: none; }
            .st-key-composer_shell textarea { background: transparent; color: var(--text-primary); font-size: 15px; line-height: 1.45; padding: 11px 2px 3px; resize: none; }
            .st-key-composer_shell textarea::placeholder { color: #929292; opacity: 1; }
            .st-key-composer_shell .st-key-voice_composer_action button, .st-key-composer_shell .st-key-composer_send button { border-radius: 11px; font-size: 18px; height: 42px; min-height: 42px; min-width: 42px; padding: 0; }
            .st-key-composer_shell .st-key-voice_composer_action button { background: transparent; border: 1px solid transparent; color: #B9B9B9; }
            .st-key-composer_shell .st-key-voice_composer_action button:hover { background: #383838; border-color: #494949; color: var(--primary-hover); }
            .st-key-composer_shell .st-key-composer_send button { background: var(--primary); border-color: var(--primary); color: #102525; }
            .st-key-composer_shell .st-key-composer_send button:hover { background: var(--primary-hover); border-color: var(--primary-hover); }
            .composer-voice-state { align-items: center; color: var(--text-primary); display: flex; font-size: 15px; font-weight: 560; gap: 9px; height: 42px; padding: 0 10px; }
            .composer-voice-state.listening { color: #FF9C96; }
            .composer-voice-state.processing { color: #F5C06F; }
            .composer-voice-state.speaking { color: var(--primary); }
            .voice-error { color: #A8413B; font-size: 12px; margin: 8px auto 0; max-width: 760px; text-align: center; }
            .travel-note { color: var(--text-secondary); font-size: 12px; line-height: 1.45; margin: 8px auto 0; max-width: 760px; text-align: center; }
            button:focus-visible, [role="button"]:focus-visible, textarea:focus-visible { outline: 3px solid rgba(12, 157, 176, .35) !important; outline-offset: 2px; }

            @media (max-width: 640px) {
                .block-container { max-width: 100%; padding: 15px 16px 145px; }
                .chat-topbar { margin-bottom: 14px; padding-bottom: 12px; }
                .chat-topbar-context, .chat-topbar-status { display: none; }
                .conversation-intro { margin-top: 19vh; }
                .conversation-intro span { font-size: 14px; }
                [data-testid="stChatMessage"]:has(.message-role-marker.user) { max-width: 86%; }
                .st-key-composer_shell { bottom: 8px; left: 16px; margin: 0; padding: 5px 6px; right: 16px; transform: none; width: auto; }
                .st-key-composer_shell .st-key-voice_composer_action button, .st-key-composer_shell .st-key-composer_send button { min-width: 40px; }
                .suggestions-label { margin-top: 24px; }
            }

            @media (prefers-reduced-motion: reduce) {
                *, *::before, *::after { animation-duration: .01ms !important; scroll-behavior: auto !important; transition-duration: .01ms !important; }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
