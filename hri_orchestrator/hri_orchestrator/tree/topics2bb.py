"""Topics2BB: copia los topicos al blackboard en cada tick.

Los topicos con tipos estandar (std_msgs, geometry_msgs) ya son reales.
Los de tipos de otros equipos (PersonArray, FaceArray, GripperState) son stubs
hasta que esos equipos entreguen sus paquetes de interfaces.
"""
from geometry_msgs.msg import PoseStamped
import py_trees
import py_trees_ros
from std_msgs.msg import Bool, String

from hri_orchestrator import blackboard_keys as bbk
from hri_orchestrator.behaviours.external.stub import (
    STUB_FACES, STUB_GRIPPER, STUB_PERSONS, StubTopic)

QOS = py_trees_ros.utilities.qos_profile_unlatched()
KEEP = py_trees.common.ClearingPolicy.NEVER         # estados: se conserva el ultimo valor
ONCE = py_trees.common.ClearingPolicy.ON_SUCCESS    # eventos: se escribe una sola vez


def to_bb(name, topic, msg_type, key, field='data', default=None, clearing=KEEP):
    return py_trees_ros.subscribers.ToBlackboard(
        name=name, topic_name=topic, topic_type=msg_type, qos_profile=QOS,
        blackboard_variables={key: field},
        initialise_variables={key: default} if default is not None else {},
        clearing_policy=clearing)


def create_topics2bb() -> py_trees.behaviour.Behaviour:
    children = [
        # Reales (tipos estandar)
        to_bb('Emergency2BB', '/base/emergency_stop', Bool, bbk.EMERGENCY, default=False),
        to_bb('StartButton2BB', '/base/start_button', Bool, bbk.START_BUTTON,
              default=False, clearing=ONCE),
        to_bb('StartSound2BB', '/base/start_sound', Bool, bbk.START_SOUND,
              default=False, clearing=ONCE),
        to_bb('Doorbell2BB', '/hri/doorbell_detected', Bool, bbk.DOORBELL,
              default=False, clearing=ONCE),
        to_bb('SafetyState2BB', '/nav/safety_state', String, bbk.SAFETY_STATE, default=''),
        to_bb('RobotPose2BB', '/nav/pose', PoseStamped, bbk.ROBOT_POSE, field=None),
        # TODO: DialogueState2BB (/hri/dialogue_state, hri_interfaces/msg/DialogueState)

        # Stubs (tipos de otros equipos)
        StubTopic('Persons2BB', bbk.PERSONS, STUB_PERSONS),
        StubTopic('Faces2BB', bbk.FACES, STUB_FACES),
        StubTopic('GripperState2BB', bbk.GRIPPER_STATE, STUB_GRIPPER),
    ]
    # Parallel: cada suscriptor se revisa en cada tick aunque otro no tenga datos
    return py_trees.composites.Parallel(
        name='Topics2BB',
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(synchronise=False),
        children=children)
