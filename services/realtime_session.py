"""Creación segura de credenciales efímeras para OpenAI Realtime."""

from dataclasses import dataclass
import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


CLIENT_SECRETS_URL = "https://api.openai.com/v1/realtime/client_secrets"


class RealtimeCredentialError(RuntimeError):
    """Error seguro para la interfaz al crear una credencial temporal."""


@dataclass(frozen=True)
class RealtimeClientSecret:
    """Solo los datos temporales necesarios para el navegador."""

    value: str
    expires_at: int | None


def create_realtime_client_secret(api_key: str, model_name: str, output_voice: str) -> RealtimeClientSecret:
    """Solicita una credencial efímera sin registrar ni persistir secretos."""
    payload = {
        "session": {
            "type": "realtime",
            "model": model_name,
            "audio": {"output": {"voice": output_voice}},
        }
    }
    request = Request(
        CLIENT_SECRETS_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=20) as response:
            response_data: dict[str, Any] = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        raise RealtimeCredentialError("No se pudo preparar la conversación por voz.") from error
    except (URLError, TimeoutError, json.JSONDecodeError) as error:
        raise RealtimeCredentialError("No se pudo conectar con el servicio de voz.") from error

    value = response_data.get("value")
    if not isinstance(value, str) or not value:
        raise RealtimeCredentialError("No se recibió una credencial temporal válida.")

    expires_at = response_data.get("expires_at")
    return RealtimeClientSecret(value=value, expires_at=expires_at if isinstance(expires_at, int) else None)
