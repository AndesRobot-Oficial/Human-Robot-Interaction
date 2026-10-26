"""Subarbol Introduce: presentar a los dos invitados mirando al correcto."""
import py_trees

from hri_orchestrator import blackboard_keys as bbk
from hri_orchestrator.behaviours.hri.converse import Converse
from hri_orchestrator.behaviours.hri.people import LocateGuests
from hri_orchestrator.tree.receive_guest import while_looking


def create_introduce() -> py_trees.behaviour.Behaviour:
    """
    [-] Introduce
        --> LocateGuests                     (pueden haber cambiado de asiento)
        /_/ mirar al invitado 1  +  Converse "introduce" (datos del invitado 2)
        /_/ mirar al invitado 2  +  Converse "introduce" (datos del invitado 1)
    """
    g1, g2 = bbk.guest(1, 'id'), bbk.guest(2, 'id')
    return py_trees.composites.Sequence(name='Introduce', memory=True, children=[
        LocateGuests(),
        while_looking(g1, Converse('introduce', person_key=g2), name='IntroduceToGuest1'),
        while_looking(g2, Converse('introduce', person_key=g1), name='IntroduceToGuest2'),
    ])
