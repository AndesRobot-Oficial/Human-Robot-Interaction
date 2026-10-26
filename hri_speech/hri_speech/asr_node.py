"""asr_node: convierte el audio del microfono en texto (usa SttEngine).

Contrato (equipo HRI):
    Se suscribe  /hri/audio         audio_common_msgs/AudioData   de audio_capture_node
                 /hri/speaking      std_msgs/Bool                 de tts_node (*propuesta)
    Publica      /hri/speech_text   std_msgs/String               lo usa dialogue_manager_node

Reglas:
    - Si la confianza de la frase es menor que confidence_threshold, no se publica.
    - Mientras el robot habla (/hri/speaking = true), se ignora el audio.

Estado: PLANTILLA (sin funcionalidad).
"""
import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, String

from hri_speech.stt_engine import SttEngine


class AsrNode(Node):

    def __init__(self):
        super().__init__('asr_node')

        # Parametros (config/asr_params.yaml)
        self.declare_parameter('model_path', 'models/vosk/vosk-model-small-en-us-0.15')
        self.declare_parameter('sample_rate', 16000)
        self.declare_parameter('confidence_threshold', 0.6)

        self.robot_speaking = False
        self.engine = SttEngine(
            model_path=self.get_parameter('model_path').value,
            sample_rate=self.get_parameter('sample_rate').value)

        self.text_pub = self.create_publisher(String, '/hri/speech_text', 10)
        self.speaking_sub = self.create_subscription(
            Bool, '/hri/speaking', self.on_speaking, 10)
        # TODO: suscripcion a /hri/audio (audio_common_msgs/AudioData) -> self.on_audio

        self.get_logger().info('asr_node listo (plantilla)')

    def on_speaking(self, msg: Bool):
        self.robot_speaking = msg.data
        if self.robot_speaking:
            self.engine.reset()

    def on_audio(self, msg):
        if self.robot_speaking:
            return
        result = self.engine.accept_audio(bytes(msg.data))
        if result is None:
            return
        text, confidence = result
        if confidence < self.get_parameter('confidence_threshold').value:
            return
        self.text_pub.publish(String(data=text))


def main(args=None):
    rclpy.init(args=args)
    node = AsrNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
