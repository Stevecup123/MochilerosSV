"""Persistencia local y segura del historial de conversaciones."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any
from uuid import uuid4


_STORAGE_PATH = Path(__file__).resolve().parent.parent / "data" / "conversations.json"
_ALLOWED_ROLES = {"user", "assistant"}


def now_iso() -> str:
    """Devuelve una marca de tiempo estable para el archivo local."""
    return datetime.now(timezone.utc).isoformat()


def clean_messages(messages: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Conserva solo datos conversacionales, nunca estado interno ni secretos."""
    cleaned: list[dict[str, str]] = []
    for message in messages:
        role = message.get("role")
        content = message.get("content")
        if role in _ALLOWED_ROLES and isinstance(content, str) and content.strip():
            cleaned.append({"role": role, "content": content})
    return cleaned


def title_from_messages(messages: list[dict[str, Any]]) -> str:
    """Crea un título legible a partir del primer mensaje del usuario."""
    for message in messages:
        if message.get("role") == "user" and isinstance(message.get("content"), str):
            title = " ".join(message["content"].split()).strip(" .,:;!?¿¡")
            if title:
                return title[:52] + ("…" if len(title) > 52 else "")
    return "Nueva conversación"


def make_conversation(messages: list[dict[str, Any]], conversation_id: str | None = None, created_at: str | None = None) -> dict[str, Any]:
    """Construye el formato que se guarda y permite reconstruir un chat."""
    timestamp = now_iso()
    return {
        "id": conversation_id or uuid4().hex,
        "title": title_from_messages(messages),
        "messages": clean_messages(messages),
        "created_at": created_at or timestamp,
        "updated_at": timestamp,
    }


def load_conversations() -> list[dict[str, Any]]:
    """Lee conversaciones válidas; un archivo inexistente o corrupto no bloquea la app."""
    try:
        with _STORAGE_PATH.open("r", encoding="utf-8") as storage_file:
            raw_conversations = json.load(storage_file)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return []

    if not isinstance(raw_conversations, list):
        return []

    conversations: list[dict[str, Any]] = []
    for raw in raw_conversations:
        if not isinstance(raw, dict) or not isinstance(raw.get("messages"), list):
            continue
        messages = clean_messages(raw["messages"])
        if not any(message["role"] == "user" for message in messages):
            continue
        conversation_id = raw.get("id") if isinstance(raw.get("id"), str) else uuid4().hex
        created_at = raw.get("created_at") if isinstance(raw.get("created_at"), str) else now_iso()
        updated_at = raw.get("updated_at") if isinstance(raw.get("updated_at"), str) else created_at
        conversations.append(
            {
                "id": conversation_id,
                "title": raw.get("title") if isinstance(raw.get("title"), str) and raw["title"].strip() else title_from_messages(messages),
                "messages": messages,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )
    return sorted(conversations, key=lambda conversation: conversation["updated_at"], reverse=True)


def save_conversations(conversations: list[dict[str, Any]]) -> None:
    """Escribe de forma atómica para no reemplazar el historial por un archivo parcial."""
    _STORAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(conversations, ensure_ascii=False, indent=2)
    temporary_path: str | None = None
    try:
        with NamedTemporaryFile("w", encoding="utf-8", dir=_STORAGE_PATH.parent, delete=False) as temporary_file:
            temporary_path = temporary_file.name
            temporary_file.write(payload)
            temporary_file.flush()
            os.fsync(temporary_file.fileno())
        os.replace(temporary_path, _STORAGE_PATH)
    finally:
        if temporary_path and os.path.exists(temporary_path):
            os.unlink(temporary_path)
