"""Subarbol BagToHost: llevar la bolsa siguiendo al anfitrion."""
import py_trees

from hri_orchestrator import blackboard_keys as bbk
from hri_orchestrator.behaviours.external.arm import MoveArmToPose, PlaceObject
from hri_orchestrator.behaviours.external.navigation import FollowPerson
from hri_orchestrator.behaviours.hri.converse import Converse
from hri_orchestrator.behaviours.hri.people import FindHost, WaitHostInFront
from hri_orchestrator.tree.receive_guest import while_looking


def create_bag_to_host() -> py_trees.behaviour.Behaviour:
    """
    [-] BagToHost
        --> FindHost
        /_/ mirar al anfitrion + Converse "ask_host"
        --> WaitHostInFront
        /_/ FollowHost: FollowPerson + Converse "wait_drop"  (termina con "drop it here")
        --> PlaceObject "floor"
        --> MoveArmToPose "home"
    """
    wait_drop = Converse('wait_drop', person_key=bbk.HOST_ID)
    follow = py_trees.composites.Parallel(
        name='FollowHost',
        policy=py_trees.common.ParallelPolicy.SuccessOnSelected(
            children=[wait_drop], synchronise=False),
        children=[FollowPerson(bbk.HOST_ID), wait_drop])

    return py_trees.composites.Sequence(name='BagToHost', memory=True, children=[
        FindHost(),
        while_looking(bbk.HOST_ID, Converse('ask_host', person_key=bbk.HOST_ID),
                      name='AskHostLooking'),
        WaitHostInFront(),
        follow,
        PlaceObject('floor'),
        MoveArmToPose('home'),
    ])
