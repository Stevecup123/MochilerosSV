"""Estilos de la interfaz conversacional."""

import streamlit as st


def apply_visual_styles() -> None:
    """Aplica la apariencia oscura fija de la interfaz conversacional."""
    st.markdown(
        """
        <style>
            :root {
                --background: #202124;
                --surface: #2a2c31;
                --surface-secondary: #34363c;
                --sidebar: #18191c;
                --text-primary: #f3f4f6;
                --text-secondary: #a4a8b0;
                --primary: #35bcb8;
                --primary-hover: #68d3ce;
                --border: #40434a;
                --hover: #292b30;
                --user-message: #31343a;
                --input: #292b30;
                --shadow: rgba(0, 0, 0, .24);
                --focus: rgba(53, 188, 184, .38);
            }

            .stApp {
                background: var(--background);
                color: var(--text-primary);
                font-family: Inter, ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
            }

            [data-testid="stHeader"] {
                background: transparent;
            }

            [data-testid="stToolbar"],
            #MainMenu,
            footer {
                visibility: hidden;
            }

            .block-container {
                max-width: 920px;
                min-height: 100vh;
                padding: 20px 36px 32px;
            }

            /* El composer es fixed y no ocupa espacio en el flujo del documento.
               Este bloque real permite desplazar el último mensaje por encima de él. */
            [data-testid="stMain"] .block-container::after {
                content: "";
                display: block;
                height: 224px;
                pointer-events: none;
            }

            .sidebar-state {
                display: none;
            }

            [data-testid="stSidebar"] {
                background: var(--sidebar);
                border-right: 1px solid var(--border);
                min-width: 270px !important;
                max-width: 270px !important;
            }

            [data-testid="stSidebar"] > div:first-child {
                box-sizing: border-box;
                position: relative;
                display: flex;
                flex-direction: column;
                height: 100vh;
                min-height: 100vh;
                overflow: hidden;
                padding: 14px 12px;
                width: 270px !important;
            }

            [data-testid="stSidebar"] .block-container {
                box-sizing: border-box;
                position: relative;
                display: flex;
                flex: 1 1 auto;
                flex-direction: column;
                min-height: 0;
                height: 100%;
                padding: 0;
                overflow: hidden;
            }

            [data-testid="stSidebar"] .stButton button {
                background: transparent;
                border: 1px solid transparent;
                color: var(--text-primary);
                font-size: 14px;
                font-weight: 500;
                justify-content: flex-start;
                min-height: 38px;
                overflow: hidden;
                padding: 0 10px;
                text-align: left;
                text-overflow: ellipsis;
                white-space: nowrap;
            }

            [data-testid="stSidebar"] .stButton button:hover {
                background: var(--hover);
            }

            .sidebar-header {
                color: var(--text-primary);
                font-size: 17px;
                font-weight: 680;
                letter-spacing: -.025em;
                padding: 7px 8px 21px;
            }

            .sidebar-label {
                color: var(--text-secondary);
                font-size: 11px;
                font-weight: 700;
                letter-spacing: .08em;
                margin: 0 9px 8px;
                text-transform: uppercase;
            }

            .sidebar-empty {
                color: var(--text-secondary);
                font-size: 12px;
                line-height: 1.45;
                margin: 0 10px;
            }

            [data-testid="stSidebar"] .st-key-new_conversation button {
                background: var(--surface);
                border-color: var(--border);
                border-radius: 9px;
                font-weight: 620;
                margin: 0 0 20px;
            }

            [data-testid="stSidebar"] .st-key-new_conversation button:hover {
                background: var(--hover);
            }

            [data-testid="stSidebar"] [class*="st-key-history_"] button {
                border-radius: 8px;
                margin: 1px 0;
            }

            [data-testid="stSidebar"] [class*="st-key-history_"] button[kind="primary"] {
                background: var(--surface-secondary);
                color: var(--text-primary);
            }

            .st-key-sidebar_history {
                box-sizing: border-box;
                height: calc(100vh - 205px);
                height: calc(100dvh - 205px);
                max-height: calc(100vh - 205px);
                max-height: calc(100dvh - 205px);
                min-height: 0;
                overflow-x: hidden;
                overflow-y: auto;
                padding-right: 4px;
                padding-bottom: 10px;
            }

            body:has(.sidebar-state.sidebar-closed) [data-testid="stSidebar"] {
                display: none !important;
            }

            body:has(.sidebar-state.sidebar-closed) .st-key-composer_shell {
                left: 50%;
                width: min(760px, calc(100vw - 48px));
            }

            .st-key-open_sidebar button {
                background: var(--surface);
                border: 1px solid var(--border);
                border-radius: 9px;
                color: var(--text-primary);
                font-size: 18px;
                height: 36px;
                min-height: 36px;
                min-width: 36px;
                padding: 0;
            }

            .st-key-open_sidebar button:hover {
                background: var(--hover);
            }

            .chat-topbar {
                align-items: center;
                border-bottom: 1px solid var(--border);
                display: flex;
                justify-content: space-between;
                margin-bottom: 12px;
                min-height: 42px;
                padding: 0 2px 13px;
            }

            .chat-topbar-title {
                color: var(--text-primary);
                display: block;
                font-size: 15px;
                font-weight: 690;
                letter-spacing: -.02em;
            }

            .chat-topbar-context {
                color: var(--text-secondary);
                display: block;
                font-size: 12px;
                margin-top: 2px;
            }

            .chat-topbar-status {
                align-items: center;
                color: var(--text-secondary);
                display: flex;
                font-size: 11px;
                gap: 6px;
            }

            .chat-topbar-status i {
                background: #36c28b;
                border-radius: 50%;
                display: inline-block;
                height: 6px;
                width: 6px;
            }

            .conversation-intro {
                color: var(--text-primary);
                margin: min(23vh, 188px) 0 14px;
                text-align: center;
            }

            .conversation-intro h1 {
                font-size: clamp(29px, 5vw, 42px);
                font-weight: 740;
                letter-spacing: -.045em;
                line-height: 1.05;
                margin: 0 0 12px;
            }

            .conversation-intro p {
                font-size: clamp(20px, 3vw, 27px);
                font-weight: 620;
                letter-spacing: -.03em;
                margin: 0 0 8px;
            }

            .conversation-intro span,
            .suggestions-label {
                color: var(--text-secondary);
            }

            .conversation-intro span {
                font-size: 15px;
            }

            .empty-conversation-marker {
                height: 0;
            }

            .suggestions-label {
                font-size: 12px;
                margin: 28px auto 9px;
                max-width: 620px;
                text-align: left;
            }

            .st-key-suggestion_0 button,
            .st-key-suggestion_1 button,
            .st-key-suggestion_2 button,
            .st-key-suggestion_3 button {
                background: var(--surface);
                border: 1px solid var(--border);
                border-radius: 12px;
                color: var(--text-primary);
                font-size: 13px;
                line-height: 1.35;
                min-height: 54px;
                padding: 9px 13px;
                text-align: left;
            }

            .st-key-suggestion_0 button:hover,
            .st-key-suggestion_1 button:hover,
            .st-key-suggestion_2 button:hover,
            .st-key-suggestion_3 button:hover {
                background: var(--hover);
            }

            [data-testid="stChatMessage"] {
                background: transparent;
                border: 0;
                max-width: 740px;
                padding: 13px 0;
            }

            [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {
                color: var(--text-primary);
                font-size: 16px;
                line-height: 1.6;
            }

            [data-testid="stChatMessage"] p {
                margin-bottom: .72rem;
            }

            [data-testid="stChatMessage"] li {
                margin-bottom: .28rem;
            }

            [data-testid="stChatMessage"] h1,
            [data-testid="stChatMessage"] h2,
            [data-testid="stChatMessage"] h3 {
                color: var(--text-primary);
                letter-spacing: -.02em;
                margin-top: 1rem;
            }

            [data-testid="stChatMessage"]:has(.message-role-marker.user) {
                background: var(--user-message);
                border: 1px solid var(--border);
                border-radius: 18px 18px 5px 18px;
                margin-left: auto;
                max-width: 72%;
                padding: 11px 16px;
            }

            [data-testid="stChatMessage"]:has(.message-role-marker.assistant) {
                margin-right: auto;
            }

            .message-role-marker {
                display: none;
            }

            .st-key-composer_shell {
                background: var(--input);
                border: 1px solid var(--border);
                border-radius: 20px;
                bottom: 26px;
                box-shadow: 0 16px 36px var(--shadow);
                box-sizing: border-box;
                left: calc(50% + 135px);
                margin: 0;
                max-width: 760px;
                padding: 6px 8px 6px 13px;
                position: fixed;
                transform: translateX(-50%);
                width: min(760px, calc(100vw - 334px));
                z-index: 10;
            }

            .st-key-composer_shell [data-testid="stHorizontalBlock"] {
                align-items: end;
                flex-wrap: nowrap !important;
            }

            .st-key-composer_shell [data-testid="stColumn"] {
                min-width: 0 !important;
                width: auto !important;
            }

            .st-key-composer_shell [data-testid="stColumn"]:first-child {
                flex: 1 1 auto !important;
            }

            .st-key-composer_shell [data-testid="stColumn"]:nth-child(2),
            .st-key-composer_shell [data-testid="stColumn"]:nth-child(3) {
                flex: 0 0 42px !important;
            }

            .st-key-composer_shell [data-testid="stTextArea"] {
                background: transparent;
                border: 0;
            }

            .st-key-composer_shell [data-testid="stTextArea"]:focus-within {
                box-shadow: none;
            }

            .st-key-composer_shell textarea {
                background: transparent;
                color: var(--text-primary);
                font-size: 15px;
                line-height: 1.45;
                padding: 11px 2px 3px;
                resize: none;
            }

            .st-key-composer_shell textarea::placeholder {
                color: var(--text-secondary);
                opacity: 1;
            }

            .st-key-composer_shell .st-key-voice_composer_action button,
            .st-key-composer_shell .st-key-composer_send button {
                border-radius: 11px;
                font-size: 18px;
                height: 42px;
                min-height: 42px;
                min-width: 42px;
                padding: 0;
            }

            .st-key-composer_shell .st-key-voice_composer_action button {
                background: transparent;
                border: 1px solid transparent;
                color: var(--text-secondary);
            }

            .st-key-composer_shell .st-key-voice_composer_action button:hover {
                background: var(--hover);
                border-color: var(--border);
                color: var(--primary);
            }

            .st-key-composer_shell .st-key-composer_send button {
                background: var(--primary);
                border-color: var(--primary);
                color: #ffffff;
            }

            .st-key-composer_shell .st-key-composer_send button:hover {
                background: var(--primary-hover);
                border-color: var(--primary-hover);
            }

            .composer-voice-state {
                align-items: center;
                color: var(--text-primary);
                display: flex;
                font-size: 15px;
                font-weight: 560;
                gap: 9px;
                height: 42px;
                padding: 0 10px;
            }

            .composer-voice-state.listening {
                color: #d95f5a;
            }

            .composer-voice-state.processing {
                color: #c88922;
            }

            .composer-voice-state.speaking {
                color: var(--primary);
            }

            .voice-error {
                color: #b54743;
                font-size: 12px;
                margin: 8px auto 0;
                max-width: 760px;
                text-align: center;
            }

            .travel-note {
                color: var(--text-secondary);
                font-size: 12px;
                line-height: 1.45;
                margin: 8px auto 0;
                max-width: 760px;
                text-align: center;
            }

            button:focus-visible,
            [role="button"]:focus-visible,
            textarea:focus-visible {
                outline: 3px solid var(--focus) !important;
                outline-offset: 2px;
            }

            @media (max-width: 640px) {
                .block-container {
                    max-width: 100%;
                    padding: 15px 16px 24px;
                }

                [data-testid="stMain"] .block-container::after {
                    height: 208px;
                }

                .chat-topbar {
                    margin-bottom: 14px;
                    padding-bottom: 12px;
                }

                .chat-topbar-context,
                .chat-topbar-status {
                    display: none;
                }

                .conversation-intro {
                    margin-top: 19vh;
                }

                .conversation-intro span {
                    font-size: 14px;
                }

                [data-testid="stChatMessage"]:has(.message-role-marker.user) {
                    max-width: 86%;
                }

                .st-key-composer_shell,
                body:has(.sidebar-state.sidebar-closed) .st-key-composer_shell {
                    bottom: 14px;
                    left: 16px;
                    margin: 0;
                    padding: 5px 6px;
                    right: 16px;
                    transform: none;
                    width: auto;
                }

                .st-key-composer_shell .st-key-voice_composer_action button,
                .st-key-composer_shell .st-key-composer_send button {
                    min-width: 40px;
                }

                .suggestions-label {
                    margin-top: 24px;
                }
            }

            @media (prefers-reduced-motion: reduce) {
                *,
                *::before,
                *::after {
                    animation-duration: .01ms !important;
                    scroll-behavior: auto !important;
                    transition-duration: .01ms !important;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
