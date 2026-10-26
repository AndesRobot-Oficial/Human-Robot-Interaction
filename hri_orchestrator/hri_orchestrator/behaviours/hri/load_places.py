"""LoadPlaces: carga config/places.yaml en el blackboard (variable 'places')."""
import py_trees
import yaml

from hri_orchestrator import blackboard_keys as bbk
from hri_orchestrator.behaviours.hri.common import ReadBlackboard

S = py_trees.common.Status

# Se usa si no se da un archivo (por ejemplo, en las pruebas)
DEFAULT_PLACES = {
    'start': {'frame_id': 'map', 'x': 0.0, 'y': 0.0, 'yaw': 0.0},
    'entrance_door': {'frame_id': 'map', 'x': 4.0, 'y': 0.0, 'yaw': 0.0},
    'living_room': {'frame_id': 'map', 'x': 1.0, 'y': 2.0, 'yaw': 1.57},
}


class LoadPlaces(ReadBlackboard):

    def __init__(self, path: str = '', name='LoadPlaces'):
        super().__init__(name, write=[bbk.PLACES])
        self.path = path

    def update(self):
        if not self.path:
            self.bb.set(bbk.PLACES, dict(DEFAULT_PLACES))
            return S.SUCCESS
        try:
            with open(self.path) as f:
                places = yaml.safe_load(f)['places']
        except (OSError, KeyError, TypeError, yaml.YAMLError) as e:
            self.feedback_message = f'no se pudo leer {self.path}: {e}'
            return S.FAILURE
        self.bb.set(bbk.PLACES, places)
        return S.SUCCESS
