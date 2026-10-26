"""Raiz del arbol.

/_/ Root
    [-] Topics2BB           (copia los topicos al blackboard en cada tick)
    [o] Priorities
        [-] Emergency
        -^- OneShot
            [-] Receptionist
        --> Idle
"""
import py_trees

from hri_orchestrator.behaviours.hri.common import idle
from hri_orchestrator.tree.emergency import create_emergency
from hri_orchestrator.tree.receptionist import create_receptionist


def create_priorities(places_file: str = '',
                      doorbell_timeout_s: float = 30.0) -> py_trees.behaviour.Behaviour:
    """Parte del arbol que no depende de ROS 2 (se puede probar sin ROS)."""
    task = py_trees.decorators.OneShot(
        name='RunOnce',
        child=create_receptionist(places_file, doorbell_timeout_s),
        policy=py_trees.common.OneShotPolicy.ON_SUCCESSFUL_COMPLETION)
    return py_trees.composites.Selector(
        name='Priorities', memory=False,
        children=[create_emergency(), task, idle()])


def create_root(places_file: str = '',
                doorbell_timeout_s: float = 30.0) -> py_trees.behaviour.Behaviour:
    from hri_orchestrator.tree.topics2bb import create_topics2bb   # requiere ROS 2
    return py_trees.composites.Parallel(
        name='Root',
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(synchronise=False),
        children=[create_topics2bb(), create_priorities(places_file, doorbell_timeout_s)])
