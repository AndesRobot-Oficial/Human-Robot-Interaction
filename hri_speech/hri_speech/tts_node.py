"""tts_node: convierte texto en voz (usa TtsEngine) y la envia al parlante.

Contrato (equipo HRI):
    Se suscribe  /hri/say          std_msgs/String               de dialogue_manager_node
    Llama        /hri/play_sound   hri_interfaces/srv/PlaySound  ofrece speaker_node
    Publica      /hri/speaking     std_msgs/Bool                 (*propuesta) true al empezar, false al terminar

Las frases se dicen en orden, una a la vez. Si speaker_node no esta corriendo,
tts_node reproduce la voz por su cuenta (para poder probarlo solo).

Prueba (dentro del contenedor):
    ros2 run hri_speech tts_node
    ros2 topic pub --once /hri/say std_msgs/msg/String "{data: 'Hello, I am MILO'}"
"""
import queue
import threading

from hri_interfaces.srv import PlaySound
import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, String

from hri_speech.tts_engine import TtsEngine


class TtsNode(Node):

    def __init__(self):
        super().__init__('tts_node')

        # Parametros (config/tts_params.yaml)
        self.declare_parameter('voice', 'mb-us2')
        self.declare_parameter('speed', 160)
        self.declare_parameter('volume', 100)
        self.declare_parameter('play_timeout_s', 30.0)

        self.engine = TtsEngine(
            voice=self.get_parameter('voice').value,
            speed=self.get_parameter('speed').value,
            volume=self.get_parameter('volume').value)

        self.say_sub = self.create_subscription(String, '/hri/say', self.on_say, 10)
        self.speaking_pub = self.create_publisher(Bool, '/hri/speaking', 10)
        self.play_client = self.create_client(PlaySound, '/hri/play_sound')

        # Las frases se dicen en un hilo aparte para no bloquear el nodo
        self.phrases = queue.Queue()
        threading.Thread(target=self.worker, daemon=True).start()

        self.get_logger().info(f'tts_node listo (voz {self.engine.voice})')

    def on_say(self, msg: String):
        if msg.data.strip():
            self.phrases.put(msg.data.strip())

    def worker(self):
        while rclpy.ok():
            text = self.phrases.get()
            self.speaking_pub.publish(Bool(data=True))
            try:
                self.get_logger().info(f'Diciendo: "{text}"')
                audio, rate = self.engine.synthesize(text)
                if not self.play_on_speaker(audio, rate):
                    self.engine.say(text)       # sin speaker_node: reproducir aqui
            except Exception as error:
                self.get_logger().error(f'No se pudo decir la frase: {error}')
            finally:
                self.speaking_pub.publish(Bool(data=False))

    def play_on_speaker(self, audio: bytes, rate: int) -> bool:
        """Envia el audio a speaker_node y espera a que termine. False si no esta."""
        if not self.play_client.wait_for_service(timeout_sec=0.5):
            self.get_logger().warn('speaker_node no disponible: reproduzco aqui', once=True)
            return False
        request = PlaySound.Request(audio_data=audio, sample_rate=rate)
        done = threading.Event()
        future = self.play_client.call_async(request)
        future.add_done_callback(lambda _: done.set())
        if not done.wait(self.get_parameter('play_timeout_s').value):
            self.get_logger().warn('speaker_node no termino a tiempo')
            return True
        return bool(future.result() and future.result().success)


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
