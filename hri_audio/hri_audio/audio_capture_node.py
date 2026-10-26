"""audio_capture_node: unico nodo que abre el microfono.

Contrato (equipo HRI):
    Publica  /hri/audio   audio_common_msgs/AudioData   uint8[] data, 16 kHz, mono
    Lo usan  asr_node, doorbell_detector_node

Estado: PLANTILLA (sin funcionalidad).
"""
import rclpy
from rclpy.node import Node


class AudioCaptureNode(Node):

    def __init__(self):
        super().__init__('audio_capture_node')

        # Parametros (config/audio_params.yaml)
        self.declare_parameter('device', 'default')
        self.declare_parameter('sample_rate', 16000)
        self.declare_parameter('channels', 1)
        self.declare_parameter('chunk_size', 4000)

        # TODO: publicador de /hri/audio con audio_common_msgs/AudioData
        #   (verificar que el paquete audio_common_msgs este instalado en Humble)
        # self.audio_pub = self.create_publisher(AudioData, '/hri/audio', 10)

        # TODO: abrir el microfono (sounddevice) y publicar cada bloque de audio

        self.get_logger().info('audio_capture_node listo (plantilla)')


def main(args=None):
    rclpy.init(args=args)
    node = AudioCaptureNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
