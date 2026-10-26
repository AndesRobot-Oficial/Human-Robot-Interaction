"""PublishMode: publica /hri/mode ("reto" o "libre").

Contrato: /hri/mode  std_msgs/String  lo usan dialogue_manager_node y llm_agent_node.
"""
import py_trees

S = py_trees.common.Status


class PublishMode(py_trees.behaviour.Behaviour):

    def __init__(self, mode: str = 'reto', name='PublishMode'):
        super().__init__(name=f'{name} "{mode}"')
        self.mode = mode
        self.publisher = None

    def setup(self, **kwargs):
        node = kwargs.get('node')
        if node is None:            # sin ROS (pruebas): no publica
            return
        import py_trees_ros
        from std_msgs.msg import String
        self.String = String
        self.publisher = node.create_publisher(
            String, '/hri/mode', py_trees_ros.utilities.qos_profile_latched())

    def update(self):
        if self.publisher is not None:
            self.publisher.publish(self.String(data=self.mode))
        return S.SUCCESS
