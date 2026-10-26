"""Converse: pide un turno de dialogo al dialogue_manager_node.

Contrato: /hri/converse  hri_interfaces/action/Converse
    Meta:      intent, person_id
    Resultado: answer, understood

Estado: PLANTILLA. Escribe respuestas fijas en el blackboard.
TODO: reemplazar por un cliente de accion (py_trees_ros.action_clients.FromBlackboard
      o una clase propia), leyendo person_id del blackboard.
"""
import py_trees

from hri_orchestrator.behaviours.hri.common import ReadBlackboard

S = py_trees.common.Status

INTENTS = ('greet', 'ask_name', 'ask_drink', 'ask_follow', 'offer_seat',
           'describe_guest', 'introduce', 'ask_bag', 'ask_host', 'wait_drop')

PLACEHOLDER_ANSWERS = {'ask_name': 'John', 'ask_drink': 'coffee', 'wait_drop': 'drop it here'}


class Converse(ReadBlackboard):

    def __init__(self, intent: str, person_key: str = '', output_key: str = ''):
        if intent not in INTENTS:
            raise ValueError(f'Intencion desconocida: {intent}')
        super().__init__(f'Converse "{intent}"',
                         read=[person_key] if person_key else [],
                         write=[output_key] if output_key else [])
        self.intent = intent
        self.person_key = person_key      # variable con el person_id (ej. guest1_id)
        self.output_key = output_key      # donde guardar la respuesta (ej. guest1_name)

    def update(self):
        person_id = self.read(self.person_key, 0) if self.person_key else 0
        self.logger.info(f'[plantilla] {self.intent} (persona {person_id})')
        if self.output_key:
            self.bb.set(self.output_key, PLACEHOLDER_ANSWERS.get(self.intent, ''))
        return S.SUCCESS
