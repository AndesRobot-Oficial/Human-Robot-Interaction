"""Comportamientos genericos."""
import py_trees


def hold(name: str = 'Hold') -> py_trees.behaviour.Behaviour:
    """Se queda en RUNNING para siempre (por ejemplo, durante el paro de emergencia)."""
    return py_trees.behaviours.Running(name=name)


def idle(name: str = 'Idle') -> py_trees.behaviour.Behaviour:
    """Se queda en RUNNING cuando no hay nada que hacer."""
    return py_trees.behaviours.Running(name=name)


class ReadBlackboard(py_trees.behaviour.Behaviour):
    """Base para comportamientos que leen y escriben el blackboard."""

    def __init__(self, name: str, read=(), write=()):
        super().__init__(name=name)
        self.bb = self.attach_blackboard_client(name=name)
        for key in read:
            self.bb.register_key(key=key, access=py_trees.common.Access.READ)
        for key in write:
            self.bb.register_key(key=key, access=py_trees.common.Access.WRITE)

    def read(self, key, default=None):
        """Lee una variable; devuelve default si todavia no existe."""
        return self.bb.get(key) if self.bb.exists(key) else default
