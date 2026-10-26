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

    def clear(self) -> None:
        self._guests.clear()
