"""Avance de la prueba: permite reanudar sin repetir lo ya hecho (por ejemplo,
despues de un paro de emergencia)."""
import py_trees

from hri_orchestrator import blackboard_keys as bbk
from hri_orchestrator.behaviours.hri.common import ReadBlackboard

S = py_trees.common.Status


class IsGuestDone(ReadBlackboard):

    def __init__(self, n: int):
        self.key = bbk.guest(n, 'done')
        super().__init__(f'IsGuest{n}Done?', read=[self.key])

    def update(self):
        return S.SUCCESS if self.read(self.key, False) else S.FAILURE


class MarkGuestDone(ReadBlackboard):

    def __init__(self, n: int):
        self.key = bbk.guest(n, 'done')
        super().__init__(f'MarkGuest{n}Done', write=[self.key])

    def update(self):
        self.bb.set(self.key, True)
        return S.SUCCESS
