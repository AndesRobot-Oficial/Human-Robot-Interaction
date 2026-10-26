"""Estructura y Electronica. Interfaces segun la ficha de task_orchestrator_node."""
from hri_orchestrator.behaviours.external.stub import Stub


class SetLed(Stub):
    """/base/set_led_state  SetLedState.srv  pattern (idle, listening, ready_handover, alert) -> success."""
    interface = '/base/set_led_state'

    def __init__(self, pattern: str):
        super().__init__(f'SetLed {pattern}', ticks=1)
        self.pattern = pattern
