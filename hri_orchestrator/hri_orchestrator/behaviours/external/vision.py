"""Vision (equipo de Vision Computacional). Interfaces segun la ficha de task_orchestrator_node."""
from hri_orchestrator import blackboard_keys as bbk
from hri_orchestrator.behaviours.external.stub import STUB_POSE, Stub


class DetectHandle(Stub):
    """/vision/detect_handle  DetectHandle.srv  door_pose -> found, handle_pose, handle_type."""
    interface = '/vision/detect_handle'

    def __init__(self):
        super().__init__('DetectHandle', ticks=1, outputs={bbk.HANDLE_POSE: STUB_POSE})


class DescribePerson(Stub):
    """/vision/describe_person  DescribePerson.srv  person_id -> attribute (ej. "camisa roja")."""
    interface = '/vision/describe_person'

    def __init__(self, person_key: str, output_key: str):
        super().__init__(f'DescribePerson {person_key}', ticks=2,
                         outputs={output_key: 'a red shirt'})
        self.person_key = person_key


class DetectFreeSeat(Stub):
    """/vision/detect_free_seat  DetectFreeSeat.srv  -> seat_pose, found."""
    interface = '/vision/detect_free_seat'

    def __init__(self, output_key: str = bbk.SEAT_POSE):
        super().__init__('DetectFreeSeat', ticks=2, outputs={output_key: STUB_POSE})
