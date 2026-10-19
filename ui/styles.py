"""Estilos de la interfaz conversacional."""

import streamlit as st


def apply_visual_styles() -> None:
    """Aplica la apariencia oscura fija de la interfaz conversacional."""
    st.markdown(
        """
        <style>
            :root {
    --background: #f4f8f5;
    --surface: #ffffff;
    --surface-secondary: #e8f3eb;
    --sidebar: #ffffff;
    --text-primary: #20352b;
    --text-secondary: #718078;
    --primary: #16845b;
    --primary-hover: #116b49;
    --border: #dce8df;
    --hover: #edf5ef;
    --user-message: #e4f3e9;
    --input: #ffffff;
    --shadow: rgba(31, 67, 47, .12);
    --focus: rgba(22, 132, 91, .25);

}

/* ===== Títulos completos del historial ===== */
section[data-testid="stSidebar"] div[data-testid="stButton"] button {
    height: auto !important;
    min-height: 42px;
    white-space: normal !important;
    overflow: visible !important;
}

section[data-testid="stSidebar"] div[data-testid="stButton"] button p {
    white-space: normal !important;
    overflow-wrap: anywhere !important;
    word-break: normal !important;
    text-overflow: clip !important;
    line-height: 1.35 !important;
    text-align: left !important;
}

/* ===== Ajuste del ancho de la barra lateral ===== */
section[data-testid="stSidebar"] {
    min-width: 300px !important;
}

/* ===== Títulos del historial más compactos ===== */
section[data-testid="stSidebar"] div[data-testid="stButton"] button p {
    font-size: 14px !important;
    line-height: 1.25 !important;
}

/* ===== Color exclusivo de la barra lateral ===== */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div:first-child {
    background-color: #B8D8C0 !important;
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


/* Botón de modo oscuro/claro */
section[data-testid="stSidebar"] .st-key-toggle_theme button {
    font-weight: 800 !important;
    font-size: 15px !important;
    background: #16845b !important;
    color: #ffffff !important;
    border: 1px solid #126b49 !important;
    border-radius: 10px !important;
    transition: background 0.2s ease, transform 0.2s ease !important;
}

section[data-testid="stSidebar"] .st-key-toggle_theme button:hover {
    background: #126b49 !important;
    color: #ffffff !important;
}


/* Menú de opciones de cada conversación */

/* Menú de tres puntos: integrado con el historial */
section[data-testid="stSidebar"] [data-testid="stPopover"] {
    display: flex !important;
    align-items: center !important;
}

section[data-testid="stSidebar"] [data-testid="stPopover"] > button {
    min-width: 28px !important;
    width: 28px !important;
    height: 32px !important;
    min-height: 32px !important;
    padding: 0 !important;
    margin: 0 !important;
    background: transparent !important;
    color: #285640 !important;
    border: none !important;
    border-radius: 50% !important;
    box-shadow: none !important;
    font-size: 20px !important;
    font-weight: 800 !important;
    line-height: 1 !important;
}

section[data-testid="stSidebar"] [data-testid="stPopover"] > button:hover {
    background: rgba(40, 86, 64, 0.12) !important;
    border: none !important;
    box-shadow: none !important;
}




/* ===== Color del texto del cuadro de escritura ===== */

.st-key-composer_shell [data-testid="stTextArea"] textarea,
.st-key-composer_shell div[data-baseweb="textarea"] textarea,
.st-key-composer_shell textarea,
.st-key-composer_shell input {
    color: #111111 !important;
    -webkit-text-fill-color: #111111 !important;
    caret-color: #111111 !important;
    background: #ffffff !important;
    opacity: 1 !important;
}

.st-key-composer_shell textarea::placeholder,
.st-key-composer_shell input::placeholder {
    color: #707070 !important;
    -webkit-text-fill-color: #707070 !important;
    opacity: 1 !important;
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

            
/* ===== Nueva apariencia turística ===== */

.conversation-intro {
    position: relative;
    overflow: hidden;
    margin: min(15vh, 120px) 0 22px;
    padding: 42px 24px 38px;
    border: 1px solid var(--border);
    border-radius: 26px;
    background:
        radial-gradient(
            ellipse at top right,
            rgba(22, 132, 91, 0.13),
            transparent 55%
        ),
        linear-gradient(135deg, #ffffff, #edf7ef);
    box-shadow: 0 12px 35px rgba(31, 67, 47, 0.07);
}

.conversation-intro h1 {
    color: #176b49;
    font-size: clamp(34px, 5vw, 48px);
    font-weight: 800;
    letter-spacing: -0.045em;
    margin-bottom: 18px;
}

.conversation-intro p {
    color: var(--text-primary);
    font-size: clamp(22px, 3vw, 29px);
    font-weight: 700;
    margin-bottom: 12px;
}

.conversation-intro span {
    color: var(--text-secondary);
    font-size: 15px;
    line-height: 1.7;
}

.suggestions-label {
    color: var(--text-primary);
    font-size: 14px;
    font-weight: 700;
    margin: 24px auto 12px;
    max-width: 620px;
}

.st-key-suggestion_0 button,
.st-key-suggestion_1 button,
.st-key-suggestion_2 button,
.st-key-suggestion_3 button {
    background: #ffffff;
    border: 1px solid var(--border);
    border-radius: 15px;
    color: var(--text-primary);
    font-size: 13px;
    font-weight: 550;
    line-height: 1.5;
    min-height: 66px;
    padding: 13px 15px;
    text-align: left;
    box-shadow: 0 3px 12px rgba(31, 67, 47, 0.04);
    transition:
        background 0.2s ease,
        border-color 0.2s ease,
        transform 0.2s ease,
        box-shadow 0.2s ease;
}

.st-key-suggestion_0 button:hover,
.st-key-suggestion_1 button:hover,
.st-key-suggestion_2 button:hover,
.st-key-suggestion_3 button:hover {
    background: #edf7ef;
    border-color: #16845b;
    color: #116b49;
    transform: translateY(-2px);
    box-shadow: 0 7px 18px rgba(31, 67, 47, 0.09);
}

/* Mensajes más definidos */

[data-testid="stChatMessage"]:has(.message-role-marker.assistant) {
    background: #ffffff;
    border: 1px solid var(--border);
    border-radius: 5px 18px 18px 18px;
    margin-right: auto;
    padding: 14px 17px;
    box-shadow: 0 3px 12px rgba(31, 67, 47, 0.04);
}

/* Barra superior */

.chat-topbar {
    padding-bottom: 16px;
    margin-bottom: 18px;
}

.chat-topbar-title {
    color: #176b49;
    font-size: 17px;
    font-weight: 750;
}

.chat-topbar-status {
    color: #16845b;
    font-weight: 600;
}

/* Cuadro para escribir */

.st-key-composer_shell {
    border-color: #d3e5d8;
    box-shadow: 0 12px 32px rgba(31, 67, 47, 0.13);
}

.st-key-composer_shell:focus-within {
    border-color: #16845b;
    box-shadow: 0 0 0 3px rgba(22, 132, 91, 0.10);
}

/* Ajustes para celulares */

@media (max-width: 640px) {
    .conversation-intro {
        margin-top: 10vh;
        padding: 32px 18px;
        border-radius: 21px;
    }

    .conversation-intro h1 {
        font-size: 35px;
    }

    .conversation-intro p {
        font-size: 23px;
    }

    .st-key-suggestion_0 button,
    .st-key-suggestion_1 button,
    .st-key-suggestion_2 button,
    .st-key-suggestion_3 button {
        min-height: 76px;
        padding: 10px;
        font-size: 12px;
    }
}


/* ===== Tarjetas de destinos turísticos ===== */

.destination-card {
    box-sizing: border-box;
    min-height: 190px;
    padding: 18px 14px;
    margin-bottom: 10px;
    border: 1px solid rgba(22, 132, 91, 0.15);
    border-radius: 18px;
    background: linear-gradient(145deg, #ffffff, #edf7ef);
    box-shadow: 0 5px 16px rgba(31, 67, 47, 0.06);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.destination-card.tunco {
    background: linear-gradient(145deg, #ffffff, #e5f5f5);
}

.destination-card.cerro {
    background: linear-gradient(145deg, #ffffff, #e8f3e9);
}

.destination-card.flores {
    background: linear-gradient(145deg, #ffffff, #f8edf5);
}

.destination-icon {
    font-size: 34px;
    margin-bottom: 15px;
}

.destination-name {
    color: #176b49;
    font-size: 16px;
    font-weight: 750;
    line-height: 1.3;
    margin-bottom: 9px;
}

.destination-description {
    color: #65756b;
    font-size: 12px;
    line-height: 1.6;
}

.st-key-destination_0 button,
.st-key-destination_1 button,
.st-key-destination_2 button {
    background: #ffffff;
    color: #176b49;
    border: 1px solid #cfe3d5;
    border-radius: 11px;
    font-size: 12px;
    font-weight: 650;
    min-height: 40px;
}

.st-key-destination_0 button:hover,
.st-key-destination_1 button:hover,
.st-key-destination_2 button:hover {
    background: #e8f5ec;
    border-color: #16845b;
    color: #116b49;
}

@media (max-width: 640px) {
    .destination-card {
        min-height: 205px;
        padding: 13px 10px;
        border-radius: 14px;
    }

    .destination-icon {
        font-size: 28px;
        margin-bottom: 12px;
    }

    .destination-name {
        font-size: 14px;
    }

    .destination-description {
        font-size: 11px;
    }
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

            /* ===== Fotografías de destinos ===== */

div[data-testid="stImage"] img {
    border-radius: 16px;
    object-fit: cover;
}

.destination-card {
    margin-top: 0;
    border-radius: 0 0 16px 16px;
}

.destination-name {
    font-size: 17px;
}

.destination-description {
    font-size: 13px;
    line-height: 1.65;
}

@media (max-width: 640px) {
    div[data-testid="stImage"] img {
        border-radius: 12px;
    }

    .destination-name {
        font-size: 14px;
    }

    .destination-description {
        font-size: 12px;
    }
}

/* ===== FONDOS TURÍSTICOS DE MOCHILEROS SV ===== */

.scenic-background {
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 0;
    opacity: 0;
    transition: opacity 3s ease-in-out;
}

/* Playa tropical */
.scenic-beach {
    background:
        radial-gradient(circle at 82% 16%, #fff0a8 0 4%, transparent 4.5%),
        radial-gradient(ellipse at 20% 62%, rgba(255,255,255,.75), transparent 20%),
        linear-gradient(to bottom,
            #9cdef3 0%, #d3f3f7 34%,
            #43c9d2 35%, #087fa8 64%,
            #f3d5a0 65%, #e7bf83 100%);
}

/* Bosque al atardecer */
.scenic-forest {
    background:
        radial-gradient(circle at 75% 23%, #ffd18a 0 5%, transparent 5.5%),
        linear-gradient(to bottom,
            #f6c08c 0%, #e88c70 34%,
            #82936a 35%, #456b4b 58%,
            #2d5039 59%, #193629 100%);
}

/* Pueblo bajo las estrellas */
.scenic-village {
    background:
        radial-gradient(circle at 12% 15%, #fff0a3 0 2px, transparent 3px),
        radial-gradient(circle at 30% 23%, #fff0a3 0 2px, transparent 3px),
        radial-gradient(circle at 55% 12%, #fff0a3 0 2px, transparent 3px),
        radial-gradient(circle at 79% 20%, #fff0a3 0 2px, transparent 3px),
        radial-gradient(circle at 90% 9%, #fff0a3 0 2px, transparent 3px),
        linear-gradient(to bottom,
            #292c63 0%, #4c4381 42%,
            #79618c 65%, #59454e 66%, #332b32 100%);
}

/* Rotación automática: cada ambiente ocupa 2 minutos */
@keyframes showBeach {
    0%, 30% { opacity: 1; }
    33.333%, 100% { opacity: 0; }
}

@keyframes showForest {
    0%, 30% { opacity: 0; }
    33.333%, 63.333% { opacity: 1; }
    66.666%, 100% { opacity: 0; }
}

@keyframes showVillage {
    0%, 63.333% { opacity: 0; }
    66.666%, 96.666% { opacity: 1; }
    100% { opacity: 0; }
}

.scenic-beach {
    animation: showBeach 360s ease-in-out infinite;
}

.scenic-forest {
    animation: showForest 360s ease-in-out infinite;
}

.scenic-village {
    animation: showVillage 360s ease-in-out infinite;
}


/* ===== INTERFAZ LEGIBLE SOBRE LOS PAISAJES ===== */

/* Mantener los fondos decorativos detrás del contenido */
.scenic-background {
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 0;
}

/* Barra superior legible en modo claro */
.chat-topbar {
    position: relative;
    background: rgba(255, 255, 255, 0.93);
    border-radius: 14px;
    padding: 12px 14px 16px;
}

/* Etiquetas legibles sobre cualquier paisaje */
.suggestions-label,
.travel-note {
    display: table;
    background: rgba(255, 255, 255, 0.94);
    color: #20352b;
    border-radius: 8px;
    padding: 7px 11px;
}

/* La barra de escritura conserva su posición fija */
.st-key-composer_shell {
    position: fixed !important;
    z-index: 100 !important;
    background: #ffffff !important;
    border: 1px solid #cbd8ce !important;
    box-shadow: 0 8px 28px rgba(0, 0, 0, 0.18) !important;
}

.st-key-composer_shell textarea,
.st-key-composer_shell input,
.st-key-composer_shell [data-baseweb="textarea"] {
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

/* Fondo nocturno fijo */
.scenic-night {
    opacity: 1 !important;
    animation: none !important;
    background:
        radial-gradient(circle at 83% 14%, #dce8ff 0 1.5px, transparent 3px),
        radial-gradient(circle at 17% 26%, #dce8ff 0 1.5px, transparent 3px),
        radial-gradient(circle at 65% 38%, #dce8ff 0 1px, transparent 3px),
        linear-gradient(145deg, #10251d 0%, #173d2e 55%, #0c1c16 100%);
}

/* Ajustes específicos del modo oscuro */
body:has(.scenic-night) .chat-topbar {
    background: rgba(25, 56, 43, 0.96) !important;
}

body:has(.scenic-night) .suggestions-label,
body:has(.scenic-night) .travel-note {
    background: rgba(25, 56, 43, 0.96) !important;
    color: #e5eee8 !important;
}


}

/* Consultas del usuario */
[data-testid="stChatMessage"]:has(.message-role-marker.user) {
    background: rgba(225, 243, 232, 0.97) !important;
    border: 1px solid #c5dfce !important;
    border-radius: 16px 16px 5px 16px !important;
    padding: 12px 17px !important;
    margin: 10px 0 16px auto !important;
    box-shadow: 0 3px 10px rgba(25, 55, 35, 0.10) !important;
}

/* Texto dentro de los bloques */
[data-testid="stChatMessage"]:has(.message-role-marker.assistant) p,
[data-testid="stChatMessage"]:has(.message-role-marker.assistant) li,
[data-testid="stChatMessage"]:has(.message-role-marker.assistant) span,
[data-testid="stChatMessage"]:has(.message-role-marker.assistant) h1,
[data-testid="stChatMessage"]:has(.message-role-marker.assistant) h2,
[data-testid="stChatMessage"]:has(.message-role-marker.assistant) h3,
[data-testid="stChatMessage"]:has(.message-role-marker.user) p,
[data-testid="stChatMessage"]:has(.message-role-marker.user) li,
[data-testid="stChatMessage"]:has(.message-role-marker.user) span {
    color: #20352b !important;
}

/* Evitar que los bloques tapen los fondos decorativos */
.scenic-background {
    z-index: 0;
    pointer-events: none;
}

@media (prefers-reduced-motion: reduce) {
    .scenic-background {
        animation: none !important;
        transition: none !important;
    }
}


/* ===== MENSAJES CON FONDO SOLIDO ===== */

/* Bloque del asistente: lado izquierdo */
[data-testid="stChatMessage"]:has(.message-role-marker.assistant)
[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #ffffff !important;
    background: #ffffff !important;
    border: 1px solid #d5e3d9 !important;
    border-radius: 14px !important;
    opacity: 1 !important;
}

/* Bloque del usuario: lado derecho */
[data-testid="stChatMessage"]:has(.message-role-marker.user) {
    flex-direction: row-reverse !important;
}

[data-testid="stChatMessage"]:has(.message-role-marker.user)
[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #d9f3e4 !important;
    background: #d9f3e4 !important;
    border: 1px solid #9bcdb1 !important;
    border-radius: 14px !important;
    opacity: 1 !important;
}

/* Texto oscuro y legible en ambos bloques */
[data-testid="stChatMessage"]:has(.message-role-marker.assistant)
[data-testid="stVerticalBlockBorderWrapper"] p,
[data-testid="stChatMessage"]:has(.message-role-marker.user)
[data-testid="stVerticalBlockBorderWrapper"] p {
    color: #17251c !important;
}

/* Evitar fondos transparentes en el contenido interior */
[data-testid="stChatMessage"]:has(.message-role-marker.assistant)
[data-testid="stVerticalBlockBorderWrapper"] > div,
[data-testid="stChatMessage"]:has(.message-role-marker.user)
[data-testid="stVerticalBlockBorderWrapper"] > div {
    background-color: #ffffff !important;
}

[data-testid="stChatMessage"]:has(.message-role-marker.user)
[data-testid="stVerticalBlockBorderWrapper"] > div {
    background-color: #d9f3e4 !important;
}


/* Texto legible en las respuestas y consultas */
.stApp [data-testid="stChatMessage"] p,
.stApp [data-testid="stChatMessage"] li,
.stApp [data-testid="stChatMessage"] h1,
.stApp [data-testid="stChatMessage"] h2,
.stApp [data-testid="stChatMessage"] h3 {
    color: #20352b !important;
}

/* Consulta del usuario: verde claro */
.stApp [data-testid="stChatMessage"]:has(.message-role-marker.user) {
    background: #e4f3e9 !important;
    border-color: #b9d8c3 !important;
}

/* Respuesta del chatbot: blanco */
.stApp [data-testid="stChatMessage"]:has(.message-role-marker.assistant) {
    background: #ffffff !important;
    border-color: #cbded0 !important;
}

        </style>
        """,
        unsafe_allow_html=True,
   
    )

