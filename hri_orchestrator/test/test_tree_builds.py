"""El arbol se arma sin errores (sin ROS 2)."""
import py_trees

from hri_orchestrator.tree.receptionist import create_receptionist
from hri_orchestrator.tree.root import create_priorities


def test_receptionist_builds():
    tree = py_trees.trees.BehaviourTree(create_receptionist())
    tree.setup(timeout=5)
    names = [b.name for b in tree.root.iterate()]
    for expected in ('Setup', 'ReceiveGuest1', 'ReceiveGuest2', 'Introduce', 'BagToHost'):
        assert expected in names


def test_priorities_builds():
    tree = py_trees.trees.BehaviourTree(create_priorities())
    tree.setup(timeout=5)
    assert tree.root.name == 'Priorities'
