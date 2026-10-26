"""Intenciones de /hri/converse (contrato del equipo HRI).

Cada intencion dice si el robot solo habla o si tambien espera una respuesta.
Las frases estan en config/phrases.yaml.
"""

INTENTS = {
    # intent            espera respuesta   dato que extrae
    'greet':          {'listens': False, 'field': None},
    'ask_name':       {'listens': True,  'field': 'name'},
    'ask_drink':      {'listens': True,  'field': 'drink'},
    'ask_follow':     {'listens': False, 'field': None},
    'offer_seat':     {'listens': False, 'field': None},
    'describe_guest': {'listens': False, 'field': None},
    'introduce':      {'listens': False, 'field': None},
    'ask_bag':        {'listens': False, 'field': None},
    'ask_host':       {'listens': False, 'field': None},
    'wait_drop':      {'listens': True,  'field': 'drop'},   # (*propuesta)
}


def is_valid(intent: str) -> bool:
    return intent in INTENTS
