import json
import threading
import time

import rclpy
from geometry_msgs.msg import Point
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionServer
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from std_msgs.msg import Bool, String

from hri_orchestrator.conectores import cargar_yaml


class SimuladorEquipos(Node):

    def __init__(self):
        super().__init__('simulador_equipos')
        self.declare_parameter('carpeta_config', '')
        self.declare_parameter('demora_s', 2.0)
        cfg = cargar_yaml('topicos.yaml', self.get_parameter('carpeta_config').value or None)
        v, g = cfg['vision'], cfg['garra']
        self.personas = []
        ActionServer(self, NavigateToPose, cfg['navegacion']['ir_a']['nombre'], self.navegar)
        self.p_registrada = self.create_publisher(String, v['persona_registrada']['nombre'], 10)
        self.p_objeto = self.create_publisher(String, v['objeto_detectado']['nombre'], 10)
        self.p_posicion = self.create_publisher(Point, v['posicion_objeto']['nombre'], 10)
        self.p_frente = self.create_publisher(String, v['persona_al_frente']['nombre'], 10)
        self.p_sofa = self.create_publisher(String, v['personas_sofa']['nombre'], 10)
        self.p_tiene = self.create_publisher(Bool, g['tiene_objeto']['nombre'], 10)
        self.p_entregado = self.create_publisher(Bool, g['entregado']['nombre'], 10)
        self.create_subscription(String, v['registrar_persona']['nombre'], self.registrar, 10)
        self.create_subscription(String, v['buscar_objeto']['nombre'], self.buscar, 10)
        self.create_subscription(String, g['agarrar']['nombre'], self.agarrar, 10)
        self.create_subscription(Bool, g['entregar']['nombre'], self.entregar, 10)
        self.create_subscription(Bool, g['proceder']['nombre'], self.proceder, 10)
        self.create_timer(1.0, self.publicar_personas)
        self.get_logger().info('simulador de Navegacion, Vision y Garra listo')

    def luego(self, funcion):
        threading.Timer(self.get_parameter('demora_s').value, funcion).start()

    def navegar(self, meta):
        p = meta.request.pose.pose.position
        self.get_logger().info(f'[Navegacion] voy a x={p.x:.2f} y={p.y:.2f}')
        time.sleep(self.get_parameter('demora_s').value)
        meta.succeed()
        self.get_logger().info('[Navegacion] llegue')
        return NavigateToPose.Result()

    def registrar(self, msg):
        self.get_logger().info(f'[Vision] registrando la cara de {msg.data}')
        if msg.data not in self.personas:
            self.personas.append(msg.data)
        self.luego(lambda: self.p_registrada.publish(String(data=msg.data)))

    def buscar(self, msg):
        self.get_logger().info(f'[Vision] buscando {msg.data}')

        def encontrar():
            self.p_posicion.publish(Point(x=0.4, y=0.0, z=0.8))
            self.p_objeto.publish(String(data=msg.data))
            self.get_logger().info(f'[Vision] detecte {msg.data}')
        self.luego(encontrar)

    def agarrar(self, msg):
        self.get_logger().info(f'[Garra] agarrando {msg.data}')
        self.luego(lambda: self.p_tiene.publish(Bool(data=True)))

    def entregar(self, msg):
        self.get_logger().info('[Garra] entregando, 3 s para que la persona lo tome')
        threading.Timer(3.0, lambda: self.p_entregado.publish(Bool(data=True))).start()

    def proceder(self, msg):
        self.get_logger().info('[Garra] agarrando la bolsa')
        self.luego(lambda: self.p_tiene.publish(Bool(data=True)))

    def publicar_personas(self):
        if not self.personas:
            return
        self.p_frente.publish(String(data=self.personas[-1]))
        lados = ['izquierda', 'derecha']
        self.p_sofa.publish(String(data=json.dumps(
            {p: lados[i % 2] for i, p in enumerate(self.personas)})))


def main(args=None):
    rclpy.init(args=args)
    node = SimuladorEquipos()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except (KeyboardInterrupt, rclpy.executors.ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
