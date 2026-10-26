"""Condiciones: leen el blackboard y deciden SUCCESS, FAILURE o RUNNING."""
import py_trees

from hri_orchestrator import blackboard_keys as bbk
from hri_orchestrator.behaviours.hri.common import ReadBlackboard

S = py_trees.common.Status


class IsEmergency(ReadBlackboard):
    """SUCCESS si el paro de emergencia esta activo (/base/emergency_stop)."""

    def __init__(self, name='IsEmergency?'):
        super().__init__(name, read=[bbk.EMERGENCY])

    def update(self):
        return S.SUCCESS if self.read(bbk.EMERGENCY, False) else S.FAILURE


class WaitForStart(ReadBlackboard):
    """RUNNING hasta recibir /base/start_button o /base/start_sound."""

    def __init__(self, name='WaitForStart'):
        super().__init__(name, read=[bbk.START_BUTTON, bbk.START_SOUND])

    def update(self):
        if self.read(bbk.START_BUTTON, False) or self.read(bbk.START_SOUND, False):
            return S.SUCCESS
        self.feedback_message = 'esperando la senal de inicio'
        return S.RUNNING


class WaitDoorbell(ReadBlackboard):
    """RUNNING hasta que suene el timbre (/hri/doorbell_detected). Luego lo consume."""

    def __init__(self, name='WaitDoorbell'):
        super().__init__(name, write=[bbk.DOORBELL])

    def update(self):
        if self.bb.exists(bbk.DOORBELL) and self.bb.get(bbk.DOORBELL):
            self.bb.set(bbk.DOORBELL, False)   # consumir: el siguiente invitado espera otro timbre
            return S.SUCCESS
        self.feedback_message = 'esperando el timbre'
        return S.RUNNING


class IsAtStart(ReadBlackboard):
    """SUCCESS si el robot esta en la posicion inicial (/nav/pose vs places['start'])."""

    def __init__(self, name='IsAtStart?'):
        super().__init__(name, read=[bbk.ROBOT_POSE, bbk.PLACES])

    def update(self):
        # TODO: comparar robot_pose con places['start'] (distancia < tolerancia)
        return S.SUCCESS


class IsHoldingObject(ReadBlackboard):
    """SUCCESS si la garra tiene un objeto (/arm/gripper_state = holding_object)."""

    def __init__(self, name='IsHoldingObject?'):
        super().__init__(name, read=[bbk.GRIPPER_STATE])

    def update(self):
        state = self.read(bbk.GRIPPER_STATE, '')
        if isinstance(state, dict):          # valor del stub
            state = state.get('state', '')
        return S.SUCCESS if state == 'holding_object' else S.FAILURE
