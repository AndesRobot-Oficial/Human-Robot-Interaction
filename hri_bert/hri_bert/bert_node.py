import json
import queue
import threading

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from hri_bert import bert_extractor


class BertNode(Node):

    def __init__(self):
        super().__init__('bert_node')
        self.cola = queue.Queue()
        self.pub = self.create_publisher(String, '/hri/bert/salida', 10)
        self.create_subscription(String, '/hri/bert/entrada', self.on_entrada, 10)
        threading.Thread(target=self.trabajar, daemon=True).start()
        self.get_logger().info('bert_node listo: orden en /hri/bert/entrada -> objeto y lugar en /hri/bert/salida')

    def on_entrada(self, msg):
        self.cola.put(msg.data)

    def trabajar(self):
        try:
            bert_extractor.cargar()
            self.get_logger().info('modelo BERT cargado')
        except Exception as error:
            self.get_logger().error(f'no se pudo cargar BERT: {error}')
        while rclpy.ok():
            try:
                texto = self.cola.get(timeout=0.5)
            except queue.Empty:
                continue
            try:
                r = bert_extractor.interpretar(texto)
                resultado = {'objeto': r['objeto'], 'lugar': r['lugar'], 'entendido': r['entendido']}
            except Exception as error:
                self.get_logger().error(f'error de BERT: {error}')
                resultado = {'objeto': None, 'lugar': None, 'entendido': False}
            self.get_logger().info(f'"{texto}" -> {resultado}')
            self.pub.publish(String(data=json.dumps(resultado)))


def main(args=None):
    rclpy.init(args=args)
    node = BertNode()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, rclpy.executors.ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
