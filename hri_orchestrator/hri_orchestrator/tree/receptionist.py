"""Tarea principal de la prueba 5.1 (Receptionist)."""
import py_trees

from hri_orchestrator.behaviours.external.base import SetLed
from hri_orchestrator.behaviours.external.navigation import SetInitialPose
from hri_orchestrator.behaviours.hri.conditions import WaitForStart
from hri_orchestrator.behaviours.hri.load_places import LoadPlaces
from hri_orchestrator.behaviours.hri.progress import IsGuestDone
from hri_orchestrator.behaviours.hri.publish_mode import PublishMode
from hri_orchestrator.tree.bag_to_host import create_bag_to_host
from hri_orchestrator.tree.introduce import create_introduce
from hri_orchestrator.tree.receive_guest import create_receive_guest

Seq = py_trees.composites.Sequence
Sel = py_trees.composites.Selector


def create_receptionist(places_file: str = '',
                        doorbell_timeout_s: float = 30.0) -> py_trees.behaviour.Behaviour:
    """
    [-] Receptionist
        [-] Setup
        [o] Guest1: IsGuest1Done? | ReceiveGuest1
        [o] Guest2: IsGuest2Done? | ReceiveGuest2
        [-] Introduce
        [-] BagToHost
        --> SetLed "idle"
    """
    setup = Seq(name='Setup', memory=True, children=[
        LoadPlaces(places_file),
        PublishMode('reto'),
        SetLed('idle'),
        WaitForStart(),
        SetInitialPose('start'),
    ])

    guests = [
        Sel(name=f'Guest{n}', memory=True, children=[
            IsGuestDone(n), create_receive_guest(n, doorbell_timeout_s)])
        for n in (1, 2)
    ]

    return Seq(name='Receptionist', memory=True, children=[
        setup, *guests, create_introduce(), create_bag_to_host(), SetLed('idle')])
