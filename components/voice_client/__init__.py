"""Puente Python para el componente local de preparación de voz."""

from pathlib import Path
from typing import Any

from streamlit.components.v1 import declare_component


_FRONTEND_PATH = Path(__file__).parent / "frontend"
_voice_client = declare_component("mochileros_voice_client", path=str(_FRONTEND_PATH))


def render_voice_client(
    command: str,
    command_revision: int,
    voice_generation: int,
    client_secret: str | None,
    realtime_config: dict[str, Any],
    conversation_messages: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """Monta el componente y devuelve su último evento JSON, si existe."""
    value = _voice_client(
        command=command,
        command_revision=command_revision,
        voice_generation=voice_generation,
        client_secret=client_secret,
        realtime_config=realtime_config,
        conversation_messages=conversation_messages,
        default=None,
        key="mochileros_voice_client",
        height=0,
    )
    return value if isinstance(value, dict) else None
