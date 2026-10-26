"""Stubs: simulan los nodos de otros equipos mientras no esten listos.

Cada stub tiene los mismos parametros y escribe las mismas variables del
blackboard que tendra el cliente real. Cuando un equipo entregue su nodo,
se reemplaza el stub por el cliente real sin tocar los archivos de tree/.
"""
from typing import Any, Dict, Optional

import py_trees

S = py_trees.common.Status

# Valores de prueba (ver tambien config/stub_values.yaml)
STUB_POSE = {'frame_id': 'map', 'x': 1.0, 'y': 1.0, 'yaw': 0.0}
STUB_PERSONS = [{'id': 1, 'pose': STUB_POSE, 'posture': 'standing', 'confidence': 0.9}]
STUB_FACES = [{'person_id': 1, 'name': '', 'confidence': 0.9}]
STUB_GRIPPER = {'state': 'holding_object', 'object_detected': True}


class Stub(py_trees.behaviour.Behaviour):
    """Simula una accion o servicio de otro equipo.

    Args:
        name: nombre en el arbol
        interface: interfaz real que reemplaza (solo informativo)
        ticks: cuantos ticks tarda (simula que el otro equipo trabaja)
        outputs: variables que escribe en el blackboard al terminar
        succeed: resultado al terminar (True = SUCCESS, False = FAILURE)
        continuous: si es True, se queda en RUNNING (por ejemplo, mirar a alguien)
    """

    interface = ''

    def __init__(self, name: str, ticks: int = 2,
                 outputs: Optional[Dict[str, Any]] = None,
                 succeed: bool = True, continuous: bool = False):
        super().__init__(name=f'{name} (stub)')
        self.ticks = ticks
        self.outputs = outputs or {}
        self.succeed = succeed
        self.continuous = continuous
        self.count = 0
        self.bb = self.attach_blackboard_client(name=self.name)
        for key in self.outputs:
            self.bb.register_key(key=key, access=py_trees.common.Access.WRITE)

    def initialise(self):
        self.count = 0

    def update(self):
        self.count += 1
        if self.continuous:
            self.feedback_message = f'simulando {self.interface}'
            return S.RUNNING
        if self.count < self.ticks:
            self.feedback_message = f'simulando {self.interface} ({self.count}/{self.ticks})'
            return S.RUNNING
        for key, value in self.outputs.items():
            self.bb.set(key, value)
        return S.SUCCESS if self.succeed else S.FAILURE


class StubTopic(py_trees.behaviour.Behaviour):
    """Simula un topico de otro equipo copiado al blackboard (para Topics2BB)."""

    def __init__(self, name: str, key: str, value: Any):
        super().__init__(name=f'{name} (stub)')
        self.key = key
        self.value = value
        self.bb = self.attach_blackboard_client(name=self.name)
        self.bb.register_key(key=key, access=py_trees.common.Access.WRITE)

    def update(self):
        self.bb.set(self.key, self.value)
        return S.SUCCESS
