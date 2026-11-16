import queue
import threading

import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, String

from hri_speech import tts_engine


class TtsNode(Node):

    def __init__(self):
        super().__init__('tts_node')
        self.declare_parameter('voz', 'mb-us1')
        self.cola = queue.Queue()
        self.iniciado = False
        self.pub_hablando = self.create_publisher(Bool, '/hri/hablando', 10)
        self.create_subscription(String, '/hri/say', self.on_say, 10)
        threading.Thread(target=self.trabajar, daemon=True).start()
        self.get_logger().info('tts_node listo: dice lo que llega por /hri/say')

    def on_say(self, msg):
        if msg.data.strip():
            self.cola.put(msg.data)

    def decir(self, texto):
        voz = self.get_parameter('voz').value
        if hasattr(tts_engine, 'hablar'):
            tts_engine.hablar(texto, voz)
            return
        if not self.iniciado:
            tts_engine.espeak_ng.initialize(
                output=tts_engine.espeak_AUDIO_OUTPUT.AUDIO_OUTPUT_SYNCH_PLAYBACK)
            self.iniciado = True
        tts_engine.espeak_ng.set_voice_by_properties(name=voz)
        tts_engine.espeak_ng.synth(tts_engine.correct_pronun(texto))

    def trabajar(self):
        while rclpy.ok():
            try:
                texto = self.cola.get(timeout=0.5)
            except queue.Empty:
                continue
            self.pub_hablando.publish(Bool(data=True))
            self.get_logger().info(f'digo: "{texto}"')
            try:
                self.decir(texto)
            except Exception as error:
                self.get_logger().error(f'error del TTS: {error}')
            if self.cola.empty():
                self.pub_hablando.publish(Bool(data=False))


def main(args=None):
    rclpy.init(args=args)
    node = TtsNode()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, rclpy.executors.ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
