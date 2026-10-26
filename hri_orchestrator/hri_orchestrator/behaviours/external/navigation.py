"""Navegacion (equipo de Navegacion). Interfaces segun la ficha de task_orchestrator_node."""
from hri_orchestrator import blackboard_keys as bbk
from hri_orchestrator.behaviours.external.stub import STUB_POSE, Stub


class SetInitialPose(Stub):
    """/nav/set_initial_pose  SetInitialPose.srv  (PoseWithCovarianceStamped, frame map) -> success."""
    interface = '/nav/set_initial_pose'

    def __init__(self, place: str = 'start'):
        super().__init__(f'SetInitialPose {place}', ticks=1)
        self.place = place


class NavigateToPose(Stub):
    """/nav/navigate_to_pose  NavigateToPose.action (Nav2)  PoseStamped -> success.

    target: nombre de un lugar de places.yaml (ej. 'entrance_door') o una variable
    del blackboard con una pose (ej. 'seat_pose').
    TODO: puede hacerse real desde ya con nav2_msgs/action/NavigateToPose.
    """
    interface = '/nav/navigate_to_pose'

    def __init__(self, target: str):
        super().__init__(f'NavigateToPose {target}', ticks=3)
        self.target = target


class LookAhead(Stub):
    """/nav/look_ahead  std_srvs/SetBool  (true = mirar hacia donde navega).

    TODO: puede hacerse real desde ya (std_srvs es estandar).
    """
    interface = '/nav/look_ahead'

    def __init__(self, enable: bool):
        super().__init__(f'LookAhead {"on" if enable else "off"}', ticks=1)
        self.enable = enable


class LookAt(Stub):
    """/nav/look  LookAt.action  person_id (o target), continuous -> on_target.

    Se usa dentro de un Parallel: queda en RUNNING mientras el robot habla.
    """
    interface = '/nav/look'

    def __init__(self, person_key: str):
        super().__init__(f'LookAt {person_key}', continuous=True)
        self.person_key = person_key


class FollowPerson(Stub):
    """/nav/follow_person  FollowPerson.action  person_id -> distance_to_person, success.

    Se usa dentro de un Parallel: termina cuando el anfitrion dice donde dejar la bolsa.
    """
    interface = '/nav/follow_person'

    def __init__(self, person_key: str):
        super().__init__(f'FollowPerson {person_key}', continuous=True)
        self.person_key = person_key


class DoorIsOpen(Stub):
    """/nav/detect_door  DetectDoor.srv  -> is_open, door_pose, hinge_side.

    SUCCESS si la puerta esta abierta; FAILURE si esta cerrada.
    """
    interface = '/nav/detect_door'

    def __init__(self, is_open: bool = True):
        super().__init__('DoorIsOpen?', ticks=1, outputs={bbk.DOOR_POSE: STUB_POSE},
                         succeed=is_open)
