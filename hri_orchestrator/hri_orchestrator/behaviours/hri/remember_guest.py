"""RememberGuest: envia los datos de un invitado al dialogue_manager_node.

Contrato: /hri/remember  hri_interfaces/srv/RememberGuest
    Peticion:  person_id, name, drink, attribute
    Respuesta: success

Estado: PLANTILLA. Solo muestra los datos.
TODO: reemplazar por un cliente de servicio (py_trees_ros.service_clients).
"""
import py_trees

from hri_orchestrator import blackboard_keys as bbk
from hri_orchestrator.behaviours.hri.common import ReadBlackboard

S = py_trees.common.Status


class RememberGuest(ReadBlackboard):

    def __init__(self, n: int):
        self.keys = {f: bbk.guest(n, f) for f in ('id', 'name', 'drink', 'attr')}
        super().__init__(f'RememberGuest{n}', read=list(self.keys.values()))
        self.n = n

    def update(self):
        data = {f: self.read(k, '') for f, k in self.keys.items()}
        self.logger.info(f'[plantilla] recordar invitado {self.n}: {data}')
        return S.SUCCESS
