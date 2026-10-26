"""tts_node: convierte texto en voz (usa TtsEngine) y la envia al parlante.

Contrato (equipo HRI):
    Se suscribe  /hri/say          std_msgs/String               de dialogue_manager_node
    Llama        /hri/play_sound   hri_interfaces/srv/PlaySound  ofrece speaker_node
    Publica      /hri/speaking     std_msgs/Bool                 (*propuesta) true al empezar, false al terminar

Estado: PLANTILLA (sin funcionalidad).
"""
from hri_interfaces.srv import PlaySound
import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, String

from hri_speech.tts_engine import TtsEngine


class TtsNode(Node):

    def __init__(self):
        super().__init__('tts_node')

        # Parametros (config/tts_params.yaml)
        self.declare_parameter('voice', 'mb-us1')
        self.declare_parameter('speed', 160)
        self.declare_parameter('volume', 100)

        self.engine = TtsEngine(
            voice=self.get_parameter('voice').value,
            speed=self.get_parameter('speed').value,
            volume=self.get_parameter('volume').value)

        self.say_sub = self.create_subscription(String, '/hri/say', self.on_say, 10)
        self.speaking_pub = self.create_publisher(Bool, '/hri/speaking', 10)
        self.play_client = self.create_client(PlaySound, '/hri/play_sound')

        self.get_logger().info('tts_node listo (plantilla)')

    def on_say(self, msg: String):
        self.get_logger().info(f'[plantilla] decir: "{msg.data}"')
        # TODO:
        #   1. publicar /hri/speaking = true
        #   2. audio, rate = self.engine.synthesize(msg.data)
        #   3. llamar a /hri/play_sound con audio_data y sample_rate
        #   4. cuando termine, publicar /hri/speaking = false


def main(args=None):
    rclpy.init(args=args)
    node = TtsNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
