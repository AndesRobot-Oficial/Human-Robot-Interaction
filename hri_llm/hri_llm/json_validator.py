"""Validacion de la respuesta del LLM en modo "reto".

El LLM debe devolver un JSON en texto, por ejemplo:
    {"nombre": "John", "bebida": null, "entendido": true}

Reglas:
    - Si el texto no es un JSON valido, se toma como no entendido.
    - Nunca inventa datos: el nombre o la bebida deben aparecer en lo que dijo
      la persona. Si no aparecen, se descartan.
"""
import json
from typing import Optional

EMPTY = {'nombre': None, 'bebida': None, 'entendido': False}


def _in_text(value: Optional[str], user_text: str) -> bool:
    return bool(value) and value.lower() in user_text.lower()


def validate_reto_reply(reply: str, user_text: str) -> dict:
    """Devuelve un dict con nombre, bebida y entendido, ya verificado."""
    try:
        data = json.loads(reply)
    except (json.JSONDecodeError, TypeError):
        return dict(EMPTY)
    if not isinstance(data, dict):
        return dict(EMPTY)

    nombre = data.get('nombre')
    bebida = data.get('bebida')
    nombre = nombre if _in_text(nombre, user_text) else None
    bebida = bebida if _in_text(bebida, user_text) else None

    return {
        'nombre': nombre,
        'bebida': bebida,
        'entendido': bool(data.get('entendido')) and (nombre is not None or bebida is not None),
    }
