"""Busqueda de personas con los datos de Vision copiados al blackboard.

Fuentes: /vision/persons (id, pose, postura) y /vision/faces (id, nombre).

Estado: PLANTILLA. Escriben valores de prueba.
"""
import py_trees

from hri_orchestrator import blackboard_keys as bbk
from hri_orchestrator.behaviours.hri.common import ReadBlackboard

S = py_trees.common.Status


class FindPersonAtDoor(ReadBlackboard):
    """Encuentra al invitado que espera en la puerta -> guestN_id, guestN_pose."""

    def __init__(self, n: int):
        self.id_key = bbk.guest(n, 'id')
        self.pose_key = bbk.guest(n, 'pose')
        super().__init__(f'FindGuest{n}AtDoor', read=[bbk.PERSONS],
                         write=[self.id_key, self.pose_key])
        self.n = n

    def update(self):
        persons = self.read(bbk.PERSONS, [])
        # TODO: elegir a la persona de pie mas cercana a la puerta que no sea otro invitado
        if not persons:
            self.feedback_message = 'no hay personas'
            return S.FAILURE
        person = persons[0]
        self.bb.set(self.id_key, person.get('id', self.n))
        self.bb.set(self.pose_key, person.get('pose'))
        return S.SUCCESS


class LocateGuests(ReadBlackboard):
    """Actualiza donde esta cada invitado (pueden haber cambiado de asiento)."""

    def __init__(self, name='LocateGuests'):
        keys = [bbk.guest(n, f) for n in (1, 2) for f in ('id', 'pose')]
        super().__init__(name, read=[bbk.PERSONS, bbk.FACES], write=keys)

    def update(self):
        # TODO: con /vision/faces y /vision/persons, actualizar guest1_pose y guest2_pose
        return S.SUCCESS


class FindHost(ReadBlackboard):
    """Encuentra al anfitrion (sentado, y que no sea uno de los invitados)."""

    def __init__(self, name='FindHost'):
        super().__init__(name, read=[bbk.PERSONS], write=[bbk.HOST_ID, bbk.HOST_POSE])

    def update(self):
        # TODO: elegir a la persona sentada que no sea guest1_id ni guest2_id
        self.bb.set(bbk.HOST_ID, 99)
        self.bb.set(bbk.HOST_POSE, None)
        return S.SUCCESS


class WaitHostInFront(ReadBlackboard):
    """RUNNING hasta que el anfitrion este de pie frente al robot."""

    def __init__(self, name='WaitHostInFront'):
        super().__init__(name, read=[bbk.PERSONS, bbk.HOST_ID])

    def update(self):
        # TODO: verificar distancia y orientacion del anfitrion respecto al robot
        return S.SUCCESS
