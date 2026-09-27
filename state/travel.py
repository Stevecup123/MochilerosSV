"""Estado ligero para preferencias y destinos favoritos de la sesión."""

from __future__ import annotations

import re

import streamlit as st


KNOWN_DESTINATIONS = (
    "Suchitoto",
    "Ruta de las Flores",
    "El Tunco",
    "El Zonte",
    "Costa del Sol",
    "Las Flores",
    "El Sunzal",
    "Cerro Verde",
    "Volcán de Santa Ana",
    "Volcán de Izalco",
    "El Boquerón",
    "Parque El Imposible",
    "Juayúa",
    "Ataco",
    "Apaneca",
    "Concepción de Ataco",
    "Coatepeque",
    "Ilopango",
    "Tazumal",
    "San Andrés",
    "Joya de Cerén",
)

PREFERENCE_KEYWORDS = (
    "playas", "playa", "montañas", "montaña", "historia", "gastronomía",
    "aventura", "tranquilo", "tranquila", "familia", "familiar",
)


def initialize_travel_state() -> None:
    """Inicializa datos efímeros: no se persisten fuera de la sesión actual."""
    st.session_state.setdefault("favorite_destinations", [])


def add_favorite(destination: str) -> bool:
    """Guarda un destino una única vez, conservando el orden de la sesión."""
    cleaned = " ".join(destination.split()).strip(".,;:!¿? ")
    if not cleaned:
        return False
    favorites = st.session_state.favorite_destinations
    if any(item.casefold() == cleaned.casefold() for item in favorites):
        return False
    favorites.append(cleaned)
    return True


def find_requested_favorite(message: str) -> str | None:
    """Reconoce solicitudes explícitas para guardar uno de los destinos conocidos."""
    normalized = message.casefold()
    if not any(word in normalized for word in ("favorito", "favorita", "guardá", "guarda", "guardar")):
        return None
    for destination in KNOWN_DESTINATIONS:
        if re.search(rf"(?<!\w){re.escape(destination.casefold())}(?!\w)", normalized):
            return destination
    return None


def build_travel_context(messages: list[dict[str, str]]) -> str:
    """Resume preferencias explícitas y favoritos para el prompt sin duplicar memoria."""
    user_text = " ".join(
        message.get("content", "") for message in messages if message.get("role") == "user"
    ).casefold()
    preferences = [word for word in PREFERENCE_KEYWORDS if re.search(rf"(?<!\w){word}(?!\w)", user_text)]
    parts: list[str] = []
    if preferences:
        parts.append("Preferencias mencionadas: " + ", ".join(dict.fromkeys(preferences)) + ".")
    favorites = st.session_state.favorite_destinations
    if favorites:
        parts.append("Favoritos de esta sesión: " + ", ".join(favorites) + ".")
    return " ".join(parts) or "Sin preferencias ni favoritos guardados todavía."
