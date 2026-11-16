import threading
import time

import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, String

from hri_speech import stt_engine


class SttNode(Node):

    def __init__(self):
        super().__init__('stt_node')
        self.declare_parameter('limite_s', 15.0)
        self.declare_parameter('pausa_s', 1.5)
        self.hablando = False
        self.ocupado = threading.Lock()
        self.pub = self.create_publisher(String, '/hri/speech_text', 10)
        self.create_subscription(String, '/hri/escuchar', self.on_escuchar, 10)
        self.create_subscription(Bool, '/hri/hablando', self.on_hablando, 10)
        self.get_logger().info('stt_node listo: publica en /hri/speech_text cuando recibe /hri/escuchar')

    def on_hablando(self, msg):
        self.hablando = msg.data

    def on_escuchar(self, msg):
        modo = msg.data.strip() or 'orden'
        if not self.ocupado.acquire(blocking=False):
            self.get_logger().warn('ya estoy escuchando, se ignora el pedido')
            return
        threading.Thread(target=self.escuchar, args=(modo,), daemon=True).start()

    def escuchar(self, modo):
        try:
            while self.hablando:
                time.sleep(0.1)
            self.get_logger().info(f'escuchando (modo {modo})...')
            resultado = stt_engine.escuchar(
                modo,
                limite=self.get_parameter('limite_s').value,
                pausa=self.get_parameter('pausa_s').value,
            )
            texto = resultado['texto'] if resultado else ''
            self.get_logger().info(f'escuche: "{texto}"')
            self.pub.publish(String(data=texto))
        except Exception as error:
            self.get_logger().error(f'error del STT: {error}')
            self.pub.publish(String(data=''))
        finally:
            self.ocupado.release()


def main(args=None):
    rclpy.init(args=args)
    node = SttNode()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, rclpy.executors.ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
