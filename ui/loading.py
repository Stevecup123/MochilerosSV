"""Pantalla de carga visual para la primera inicialización de Mochileros SV."""

from __future__ import annotations

import streamlit as st


def render_loading_screen() -> st.delta_generator.DeltaGenerator | None:
    """Muestra una cubierta breve y no bloqueante durante el primer render de la sesión."""
    if st.session_state.get("loading_screen_seen"):
        return None

    slot = st.empty()
    slot.markdown(
        """
        <style>
            .mochileros-loading-overlay {
                align-items: center;
                animation: loading-exit .45s ease 2.05s forwards;
                background: #f4f8f5;
                display: flex;
                inset: 0;
                justify-content: center;
                pointer-events: none;
                position: fixed;
                z-index: 999999;
            }
            .mochileros-loading-card { color: #176b49; text-align: center; }
            .mochileros-loading-map { display: block; height: auto; margin: 0 auto 18px; width: min(250px, 64vw); }
            .mochileros-loading-map path {
                fill: rgba(22, 132, 91, .045);
                stroke: #16845b;
                stroke-dasharray: 1;
                stroke-dashoffset: 1;
                stroke-linecap: round;
                stroke-linejoin: round;
                stroke-width: .42;
                animation: draw-el-salvador 1.55s cubic-bezier(.5, 0, .2, 1) .1s forwards;
            }
            .mochileros-loading-card strong { display: block; font-size: 20px; letter-spacing: -.02em; }
            .mochileros-loading-card span { color: #65756b; font-size: 13px; }
            @keyframes draw-el-salvador { to { stroke-dashoffset: 0; } }
            @keyframes loading-exit { to { opacity: 0; pointer-events: none; visibility: hidden; } }
            @media (prefers-reduced-motion: reduce) {
                .mochileros-loading-overlay, .mochileros-loading-map path { animation: none; }
            }
        </style>
        <div class="mochileros-loading-overlay" role="status" aria-live="polite">
            <div class="mochileros-loading-card">
                <!-- Contorno geográfico simplificado de El Salvador. -->
                <svg class="mochileros-loading-map" viewBox="220 421 10 6" aria-label="Contorno de El Salvador" role="img">
                    <path pathLength="1" d="M229.09 425.76 228.78 426.43 227.16 426.39 226.15 426.12 224.99 425.55 223.43 425.37 222.64 424.75 222.73 424.33 223.69 423.61 224.21 423.29 224.06 422.95 224.72 422.78 225.55 423.02 226.15 423.59 227 424.05 227.1 424.44 228.33 424.1 228.91 424.3 229.29 424.61 Z" />
                </svg>
                <strong>Mochileros SV</strong>
                <span>Preparando tu próxima aventura…</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    return slot


def dismiss_loading_screen(_slot: st.delta_generator.DeltaGenerator | None) -> None:
    """Marca la sesión como inicializada; el CSS retira la cubierta tras el trazo."""
    st.session_state.loading_screen_seen = True
