"""doorbell_detector_node: detecta el timbre en el audio del microfono.

Contrato (equipo HRI):
    Se suscribe  /hri/audio              audio_common_msgs/AudioData   de audio_capture_node
    Publica      /hri/doorbell_detected  std_msgs/Bool                 lo usa task_orchestrator_node
                 data = true una sola vez por cada timbre

Nota de la 5.1: es opcional (2 x 30 pts). Solo cuenta si el robot espera en la
posicion inicial y reacciona al instante. El sonido no se da antes de la prueba.

Estado: PLANTILLA (sin funcionalidad).
"""
import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool


class DoorbellDetectorNode(Node):

    def __init__(self):
        super().__init__('doorbell_detector_node')

        # Parametros (config/doorbell_params.yaml)
        self.declare_parameter('sample_rate', 16000)
        self.declare_parameter('min_interval_s', 3.0)

        self.doorbell_pub = self.create_publisher(Bool, '/hri/doorbell_detected', 10)
        # TODO: suscripcion a /hri/audio (audio_common_msgs/AudioData) -> self.on_audio

        self.get_logger().info('doorbell_detector_node listo (plantilla)')

    def on_audio(self, msg):
        # TODO: detectar el timbre y publicar una sola vez:
        #       self.doorbell_pub.publish(Bool(data=True))
        pass


def main(args=None):
    rclpy.init(args=args)
    node = DoorbellDetectorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
