"""Nombres de todas las variables del blackboard del arbol.

Usar siempre estas constantes (nunca escribir el nombre a mano) para que un
error de escritura falle al importar y no en medio de la prueba.
"""

# ---------- Copiadas de topicos (tree/topics2bb.py) ----------
EMERGENCY = 'emergency'            # bool    /base/emergency_stop
START_BUTTON = 'start_button'      # bool    /base/start_button
START_SOUND = 'start_sound'        # bool    /base/start_sound
DOORBELL = 'doorbell'              # bool    /hri/doorbell_detected
SAFETY_STATE = 'safety_state'      # str     /nav/safety_state
ROBOT_POSE = 'robot_pose'          # pose    /nav/pose
DIALOGUE_STATE = 'dialogue_state'  # msg     /hri/dialogue_state
PERSONS = 'persons'                # list    /vision/persons
FACES = 'faces'                    # list    /vision/faces
GRIPPER_STATE = 'gripper_state'    # str     /arm/gripper_state

# ---------- Escritas por el arbol ----------
PLACES = 'places'                  # dict    config/places.yaml
DOOR_POSE = 'door_pose'            # pose    /nav/detect_door
HANDLE_POSE = 'handle_pose'        # pose    /vision/detect_handle
SEAT_POSE = 'seat_pose'            # pose    /vision/detect_free_seat
HOST_ID = 'host_id'                # int
HOST_POSE = 'host_pose'            # pose

# ---------- Por invitado (n = 1 o 2) ----------
GUEST_FIELDS = ('id', 'pose', 'name', 'drink', 'attr', 'seat', 'done')


def guest(n: int, field: str) -> str:
    """Nombre de la variable de un invitado. Ej.: guest(1, 'name') -> 'guest1_name'."""
    if field not in GUEST_FIELDS:
        raise ValueError(f'Campo de invitado desconocido: {field}')
    return f'guest{n}_{field}'
