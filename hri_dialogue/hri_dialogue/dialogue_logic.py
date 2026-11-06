"""Logica del gestor de dialogo, sin ROS 2 (se puede probar sola).

    build_phrase()     arma la frase de una intencion con config/phrases.yaml
    parse_llm_reply()  saca el nombre o la bebida del JSON del LLM
    fallback_extract() respaldo con la lista de config/vocabulary.yaml
"""
import json
import random
import re
from typing import Dict, List, Optional

import yaml

from hri_dialogue.fallback import find_in_vocabulary
from hri_dialogue.guest_memory import GuestMemory

# dato que espera la intencion -> clave del JSON del LLM / lista de vocabulary.yaml
LLM_KEYS = {'name': 'nombre', 'drink': 'bebida'}
VOCAB_KEYS = {'name': 'names', 'drink': 'drinks', 'drop': 'drop_commands'}


def load_yaml(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f) or {}


class _Blank(dict):
    """Para format_map: una variable que no se conoce queda vacia."""

    def __missing__(self, key):
        return ''


def build_phrase(phrases: Dict[str, List[str]], intent: str, memory: GuestMemory,
                 person_id: int) -> str:
    """Frase de la intencion con los datos de la memoria de invitados.

    {name} {drink}             invitado person_id
    {other_name} {other_drink} el otro invitado que haya en la memoria
    {attribute}                descripcion del otro invitado (describe_guest)
    """
    options = phrases.get(intent) or []
    if not options:
        return ''
    guest = memory.get(person_id)
    other = memory.other(person_id)
    values = _Blank(
        name=guest.name if guest else '',
        drink=guest.drink if guest else '',
        other_name=other.name if other else '',
        other_drink=other.drink if other else '',
        attribute=other.attribute if other else (guest.attribute if guest else ''),
    )
    text = random.choice(options).format_map(values)
    # si falta un dato: "Please take a seat here, ." -> "Please take a seat here."
    text = re.sub(r'\s+([,.?!])', r'\1', text)
    text = re.sub(r',([.?!])', r'\1', text)
    return text.lstrip(' ,')


def parse_llm_reply(reply: str, field: str) -> Optional[str]:
    """Valor del dato en la respuesta del LLM, o None si no lo entendio."""
    key = LLM_KEYS.get(field)
    if not key:
        return None
    try:
        data = json.loads(reply)
    except (json.JSONDecodeError, TypeError):
        return None
    if not isinstance(data, dict) or not data.get('entendido'):
        return None
    value = data.get(key)
    return value.strip() if isinstance(value, str) and value.strip() else None


def fallback_extract(text: str, field: str, vocabulary: dict) -> Optional[str]:
    """Busca el dato en la lista de vocabulary.yaml. Nunca inventa."""
    options = vocabulary.get(VOCAB_KEYS.get(field, ''), []) or []
    return find_in_vocabulary(text, options)
