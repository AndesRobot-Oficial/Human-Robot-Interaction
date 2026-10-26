"""Pipeline BERT + T5 (Juan River) como respaldo del LLM en modo "libre".

BERT etiqueta la orden (accion, objeto, lugar, persona) y T5 genera un plan.
Se usa solo si el LLM tarda o devuelve un JSON invalido. Las acciones de T5 se
traducen a las habilidades de /hri/skill_request.

Estado: PARA MAS ADELANTE (modo "libre"). Los modelos van en models/bert_t5/.
"""
from typing import List


class BertT5Pipeline:

    def __init__(self, bert_path: str, t5_path: str):
        self.bert_path = bert_path
        self.t5_path = t5_path
        # TODO: cargar los modelos

    def plan(self, command: str) -> List[str]:
        """Devuelve la lista de pasos del plan (por ejemplo ['navigate to kitchen', ...])."""
        # TODO
        return []
