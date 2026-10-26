"""Rama de emergencia: tiene prioridad sobre todo lo demas."""
import py_trees

from hri_orchestrator.behaviours.external.base import SetLed
from hri_orchestrator.behaviours.hri.common import hold
from hri_orchestrator.behaviours.hri.conditions import IsEmergency


def create_emergency() -> py_trees.behaviour.Behaviour:
    """
    [-] Emergency
        --> IsEmergency?
        --> SetLed "alert"
        --> Hold           (RUNNING mientras dure el paro)
    """
    return py_trees.composites.Sequence(
        name='Emergency', memory=False,
        children=[IsEmergency(), SetLed('alert'), hold()])
