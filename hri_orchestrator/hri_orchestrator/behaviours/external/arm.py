"""Brazo y Garra. Interfaces segun la ficha de task_orchestrator_node."""
from hri_orchestrator.behaviours.external.stub import Stub


class OpenDoor(Stub):
    """/arm/open_door  OpenDoor.action  handle_pose, direction (pull | push) -> success."""
    interface = '/arm/open_door'

    def __init__(self, direction: str = 'pull'):
        super().__init__(f'OpenDoor {direction}', ticks=4)
        self.direction = direction


class MoveArmToPose(Stub):
    """/arm/move_to_pose  MoveArmToPose.action  pose_name (home, look_door, look_front,
    carry, ready_handover) o look_target -> success."""
    interface = '/arm/move_to_pose'

    def __init__(self, pose_name: str):
        super().__init__(f'MoveArmToPose {pose_name}', ticks=2)
        self.pose_name = pose_name


class PickObject(Stub):
    """/arm/pick_object  PickObject.action  target_pose, mode (grasp | handover) -> success.

    En la 5.1 se usa mode = handover: el invitado entrega la bolsa, el brazo no se estira.
    """
    interface = '/arm/pick_object'

    def __init__(self, mode: str = 'handover'):
        super().__init__(f'PickObject {mode}', ticks=3)
        self.mode = mode


class PointTo(Stub):
    """/arm/point_to  PointTo.action  PointStamped target -> success."""
    interface = '/arm/point_to'

    def __init__(self, target_key: str):
        super().__init__(f'PointTo {target_key}', ticks=2)
        self.target_key = target_key


class PlaceObject(Stub):
    """/arm/place_object  PlaceObject.action  (no confirmado en la ficha) -> success."""
    interface = '/arm/place_object'

    def __init__(self, target: str = 'floor'):
        super().__init__(f'PlaceObject {target}', ticks=3)
        self.target = target
