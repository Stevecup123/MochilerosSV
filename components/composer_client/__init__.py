"""Componente local del campo de escritura del composer."""

from pathlib import Path
from typing import Any

from streamlit.components.v1 import declare_component


_FRONTEND_PATH = Path(__file__).parent / "frontend"
_composer_client = declare_component("mochileros_composer_client", path=str(_FRONTEND_PATH))


def render_composer_client(conversation_id: str | None) -> dict[str, Any] | None:
    """Renderiza el input y devuelve únicamente acciones explícitas del usuario."""
    value = _composer_client(
        conversation_id=conversation_id,
        default=None,
        key="mochileros_composer_client",
        height=56,
    )
    return value if isinstance(value, dict) else None
