import json
import queue
import threading

import ollama
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from hri_llm.drink_extractor_phi import extract_drink
from hri_llm.json_validator import validate_reto_reply
from hri_llm.name_extractor import MODEL, extract_name


class LlmNode(Node):

    def __init__(self):
        super().__init__('llm_node')
        self.declare_parameter('modelo', MODEL)
        self.declare_parameter('calentar', True)
        self.cola = queue.Queue()
        self.pub = self.create_publisher(String, '/hri/llm/salida', 10)
        self.create_subscription(String, '/hri/llm/entrada', self.on_entrada, 10)
        threading.Thread(target=self.trabajar, daemon=True).start()
        self.get_logger().info('llm_node listo: texto en /hri/llm/entrada -> nombre y bebida en /hri/llm/salida')

    def on_entrada(self, msg):
        self.cola.put(msg.data)

    def calentar(self):
        modelo = self.get_parameter('modelo').value
        self.get_logger().info(f'cargando {modelo} en Ollama...')
        try:
            ollama.Client(timeout=120).chat(
                model=modelo,
                messages=[{'role': 'user', 'content': 'Reply only with OK.'}],
                options={'temperature': 0},
            )
            self.get_logger().info('modelo listo')
        except Exception as error:
            self.get_logger().warn(f'no se pudo cargar el modelo: {error}')

    def interpretar(self, texto):
        nombre = extract_name(texto, model=self.get_parameter('modelo').value)
        self.get_logger().info(f"nombre: {nombre['name']} ({nombre['source']}, {nombre['reason']}, {nombre['elapsed_seconds']} s)")
        bebida = extract_drink(texto)
        respuesta = json.dumps({
            'nombre': nombre['name'],
            'bebida': bebida['drink'],
            'entendido': nombre['understood'] or bebida['understood'],
        })
        return validate_reto_reply(respuesta, texto)

    def trabajar(self):
        if self.get_parameter('calentar').value:
            self.calentar()
        while rclpy.ok():
            try:
                texto = self.cola.get(timeout=0.5)
            except queue.Empty:
                continue
            try:
                resultado = self.interpretar(texto)
            except Exception as error:
                self.get_logger().error(f'error del LLM: {error}')
                resultado = {'nombre': None, 'bebida': None, 'entendido': False}
            self.get_logger().info(f'"{texto}" -> {resultado}')
            self.pub.publish(String(data=json.dumps(resultado)))


def main(args=None):
    rclpy.init(args=args)
    node = LlmNode()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, rclpy.executors.ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
