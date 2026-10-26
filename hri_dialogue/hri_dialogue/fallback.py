"""Respaldo cuando el LLM falla o tarda mas de llm_timeout_s.

Busca en lo que dijo la persona alguna palabra de la lista de nombres o bebidas
(config/vocabulary.yaml). Nunca inventa: si no encuentra nada, devuelve None.
"""
import re
from typing import List, Optional


def find_in_vocabulary(text: str, options: List[str]) -> Optional[str]:
    """Devuelve la primera opcion que aparece en el texto (sin importar mayusculas)."""
    # Quitar signos de puntuacion: "Hi, I'm John." -> " hi i m john "
    padded = ' ' + re.sub(r'[^a-z0-9]+', ' ', text.lower()) + ' '
    # Primero las opciones mas largas ("orange juice" antes que "juice")
    for option in sorted(options, key=len, reverse=True):
        if ' ' + re.sub(r'[^a-z0-9]+', ' ', option.lower()).strip() + ' ' in padded:
            return option
    return None
