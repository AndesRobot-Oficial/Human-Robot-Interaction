"""Memoria de invitados: lo que llega por /hri/remember (RememberGuest.srv)."""
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class Guest:
    person_id: int
    name: str = ''
    drink: str = ''
    attribute: str = ''


class GuestMemory:

    def __init__(self):
        self._guests: Dict[int, Guest] = {}

    def remember(self, person_id: int, name: str, drink: str, attribute: str) -> None:
        self._guests[person_id] = Guest(person_id, name, drink, attribute)

    def get(self, person_id: int) -> Optional[Guest]:
        return self._guests.get(person_id)

    def other(self, person_id: int) -> Optional[Guest]:
        """Otro invitado de la memoria (el que no es person_id), o None."""
        for pid, guest in self._guests.items():
            if pid != person_id:
                return guest
        return None

    def clear(self) -> None:
        self._guests.clear()
