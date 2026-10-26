"""Recorre la prueba 5.1 completa con stubs (sin ROS 2)."""
import py_trees

from hri_orchestrator import blackboard_keys as bbk
from hri_orchestrator.behaviours.external.stub import STUB_GRIPPER, STUB_PERSONS
from hri_orchestrator.tree.root import create_priorities

MAX_TICKS = 300


def make_tree():
    py_trees.blackboard.Blackboard.clear()
    bb = py_trees.blackboard.Client(name='test')
    for key in (bbk.EMERGENCY, bbk.START_BUTTON, bbk.START_SOUND, bbk.DOORBELL,
                bbk.PERSONS, bbk.GRIPPER_STATE):
        bb.register_key(key=key, access=py_trees.common.Access.WRITE)
    bb.set(bbk.EMERGENCY, False)
    bb.set(bbk.START_BUTTON, True)
    bb.set(bbk.START_SOUND, False)
    bb.set(bbk.DOORBELL, False)
    bb.set(bbk.PERSONS, STUB_PERSONS)
    bb.set(bbk.GRIPPER_STATE, STUB_GRIPPER)
    tree = py_trees.trees.BehaviourTree(create_priorities(doorbell_timeout_s=0.0))
    tree.setup(timeout=5)
    return tree, bb


def run_until_done(tree, on_tick=None):
    task = tree.root.children[1]        # OneShot(Receptionist)
    for i in range(MAX_TICKS):
        if on_tick:
            on_tick(i)
        tree.tick()
        if task.status == py_trees.common.Status.SUCCESS:
            return i
    return None


def test_reto_completo():
    tree, _ = make_tree()
    assert run_until_done(tree) is not None
    store = py_trees.blackboard.Blackboard.storage
    assert store['/' + bbk.guest(1, 'name')] == 'John'
    assert store['/' + bbk.guest(2, 'drink')] == 'coffee'
    assert store['/' + bbk.guest(1, 'done')] is True
    assert store['/' + bbk.guest(2, 'done')] is True


def test_emergencia_no_repite_invitado_1():
    tree, bb = make_tree()
    guest1 = next(b for b in tree.root.iterate() if b.name == 'ReceiveGuest1')
    stopped_at = []
    guest1_repeated = []

    def on_tick(i):
        store = py_trees.blackboard.Blackboard.storage
        # Activar el paro cuando el invitado 1 ya termino, y soltarlo 5 ticks despues
        if store.get('/' + bbk.guest(1, 'done')) and not stopped_at:
            bb.set(bbk.EMERGENCY, True)
            stopped_at.append(i)
        elif stopped_at and i == stopped_at[0] + 5:
            bb.set(bbk.EMERGENCY, False)
        elif stopped_at and guest1.status == py_trees.common.Status.RUNNING:
            guest1_repeated.append(i)

    assert run_until_done(tree, on_tick) is not None
    assert stopped_at, 'no se activo el paro de emergencia'
    assert not guest1_repeated, 'el invitado 1 se repitio despues del paro'
