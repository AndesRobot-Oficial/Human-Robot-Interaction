"""Subarbol ReceiveGuest(n): recibir a un invitado y llevarlo a un asiento."""
import py_trees

from hri_orchestrator import blackboard_keys as bbk
from hri_orchestrator.behaviours.external.arm import MoveArmToPose, OpenDoor, PickObject, PointTo
from hri_orchestrator.behaviours.external.base import SetLed
from hri_orchestrator.behaviours.external.navigation import (
    DoorIsOpen, LookAhead, LookAt, NavigateToPose)
from hri_orchestrator.behaviours.external.vision import (
    DescribePerson, DetectFreeSeat, DetectHandle)
from hri_orchestrator.behaviours.hri.conditions import (
    IsAtStart, IsHoldingObject, WaitDoorbell)
from hri_orchestrator.behaviours.hri.converse import Converse
from hri_orchestrator.behaviours.hri.people import FindPersonAtDoor
from hri_orchestrator.behaviours.hri.progress import MarkGuestDone
from hri_orchestrator.behaviours.hri.remember_guest import RememberGuest

Seq = py_trees.composites.Sequence
Sel = py_trees.composites.Selector
Par = py_trees.composites.Parallel


def navigate(target: str, name: str) -> py_trees.behaviour.Behaviour:
    """Navegar mirando hacia adelante: LookAhead on -> NavigateToPose -> LookAhead off."""
    return Seq(name=name, memory=True, children=[
        LookAhead(True), NavigateToPose(target), LookAhead(False)])


def while_looking(person_key: str, child: py_trees.behaviour.Behaviour,
                  name: str) -> py_trees.behaviour.Behaviour:
    """Ejecuta child mientras mira a la persona. Termina cuando termina child."""
    return Par(name=name,
               policy=py_trees.common.ParallelPolicy.SuccessOnSelected(
                   children=[child], synchronise=False),
               children=[LookAt(person_key), child])


def create_receive_guest(n: int, doorbell_timeout_s: float = 30.0) -> py_trees.behaviour.Behaviour:
    gid = bbk.guest(n, 'id')

    # 1. Esperar en la posicion inicial (el timbre solo cuenta ahi)
    wait_at_start = Seq(name='WaitAtStart', memory=True, children=[
        Sel(name='GoToStart', memory=False, children=[
            IsAtStart(), navigate('start', 'NavigateToStart')]),
        Sel(name='Doorbell (opcional)', memory=True, children=[
            py_trees.decorators.Timeout(
                name='TimeoutDoorbell', child=WaitDoorbell(), duration=doorbell_timeout_s),
            py_trees.behaviours.Success(name='SinTimbre')]),
    ])

    # 2. Ir a la puerta y abrirla si esta cerrada
    go_to_door = navigate('entrance_door', 'GoToDoor')
    open_door = Sel(name='OpenDoorIfClosed', memory=True, children=[
        DoorIsOpen(),
        Seq(name='OpenDoor', memory=True, children=[DetectHandle(), OpenDoor()])])

    # 3. Encontrar al invitado
    find_guest = py_trees.decorators.Retry(
        name='RetryFindGuest', child=FindPersonAtDoor(n), num_failures=3)

    # 4. Conversar mirandolo
    dialogue = [
        Converse('greet', person_key=gid),
        Converse('ask_name', person_key=gid, output_key=bbk.guest(n, 'name')),
        Converse('ask_drink', person_key=gid, output_key=bbk.guest(n, 'drink')),
    ]
    if n == 1:
        dialogue.append(DescribePerson(gid, output_key=bbk.guest(1, 'attr')))
    else:
        dialogue.append(Converse('describe_guest', person_key=gid))
    talk = while_looking(gid, Seq(name='Dialogue', memory=True, children=dialogue),
                         name='TalkToGuest')

    children = [wait_at_start, go_to_door, open_door, find_guest, talk, RememberGuest(n)]

    # 5. Bolsa (solo el segundo invitado)
    if n == 2:
        children.append(Seq(name='ReceiveBag', memory=True, children=[
            Converse('ask_bag', person_key=gid),
            SetLed('ready_handover'),
            MoveArmToPose('ready_handover'),
            PickObject('handover'),
            IsHoldingObject(),
            MoveArmToPose('carry'),
            SetLed('idle'),
        ]))

    # 6. Guiar a la sala y ofrecer asiento
    children += [
        Seq(name='GuideToLivingRoom', memory=True, children=[
            Converse('ask_follow', person_key=gid),
            navigate('living_room', 'NavigateToLivingRoom')]),
        Seq(name='OfferSeat', memory=True, children=[
            DetectFreeSeat(output_key=bbk.guest(n, 'seat')),
            PointTo(bbk.guest(n, 'seat')),
            while_looking(gid, Converse('offer_seat', person_key=gid), name='OfferSeatLooking')]),
        MarkGuestDone(n),
    ]
    return Seq(name=f'ReceiveGuest{n}', memory=True, children=children)
