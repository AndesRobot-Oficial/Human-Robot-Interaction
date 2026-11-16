import threading

import rclpy
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from std_msgs.msg import Bool

from hri_orchestrator.conectores import Conectores, cargar_yaml


class TaskOrchestratorNode(Node):

    def __init__(self):
        super().__init__('task_orchestrator_node')
        self.declare_parameter('carpeta_config', '')
        self.declare_parameter('esperar_timbre', True)
        self.declare_parameter('intentos', 3)
        self.declare_parameter('auto_iniciar', False)
        carpeta = self.get_parameter('carpeta_config').value or None
        self.frases = cargar_yaml('frases.yaml', carpeta)
        self.nombres = cargar_yaml('nombres.yaml', carpeta)
        self.c = Conectores(self, carpeta=carpeta)
        self.invitados = {}
        self.corriendo = threading.Lock()
        self.create_subscription(Bool, '/orquestador/iniciar', self.on_iniciar, 10)
        self.get_logger().info('task_orchestrator_node listo: /orquestador/iniciar true para empezar el reto')
        if self.get_parameter('auto_iniciar').value:
            self.iniciar()

    def on_iniciar(self, msg):
        if msg.data:
            self.iniciar()

    def iniciar(self):
        if not self.corriendo.acquire(blocking=False):
            self.get_logger().warn('el reto ya esta corriendo')
            return
        threading.Thread(target=self.correr, daemon=True).start()

    def correr(self):
        try:
            self.secuencia()
        except Exception as error:
            self.get_logger().error(f'el reto se detuvo: {error}')
        finally:
            self.corriendo.release()

    def estado(self, texto):
        self.get_logger().info(f'[estado] {texto}')
        self.c.estado.enviar(texto)

    def decir(self, clave, **datos):
        texto = self.frases[clave].format(**datos)
        self.get_logger().info(f'[robot] {texto}')
        self.c.hri.decir(texto)

    def ir(self, lugar):
        waypoint = self.nombres['lugares_reto'].get(lugar, lugar)
        self.estado(f'yendo a {lugar} ({waypoint})')
        llego = self.c.nav.ir_a(waypoint)
        self.estado(f'llego a {lugar}' if llego else f'no llego a {lugar}')
        return llego

    def registrar_invitado(self, invitado):
        vision = {}
        hilo = threading.Thread(
            target=lambda: vision.update(ok=self.c.vision.registrar_persona(invitado)), daemon=True)
        hilo.start()
        self.decir('saludo')
        datos = {'nombre': None, 'bebida': None}
        for intento in range(self.get_parameter('intentos').value):
            self.decir('preguntar' if intento == 0 else 'repetir')
            texto = self.c.hri.escuchar('libre')
            self.get_logger().info(f'[invitado] "{texto}"')
            if not texto:
                continue
            r = self.c.hri.interpretar_invitado(texto)
            datos['nombre'] = r.get('nombre') or datos['nombre']
            datos['bebida'] = r.get('bebida') or datos['bebida']
            if datos['nombre'] and datos['bebida']:
                break
        self.invitados[invitado] = datos
        hilo.join(35.0)
        if not vision.get('ok'):
            self.get_logger().warn(f'Vision no confirmo el registro de {invitado}')
        self.estado(f'{invitado} listo: {datos}')
        self.decir('registrado', nombre=datos['nombre'] or 'friend')

    def recibir_invitado(self, invitado):
        if self.get_parameter('esperar_timbre').value:
            self.estado('esperando el timbre')
            self.c.hri.esperar_timbre()
            self.estado('timbre detectado')
        self.ir('puerta')
        self.registrar_invitado(invitado)
        self.decir('vamos_sofa')
        self.ir('sofa')

    def entender_orden(self, nombre):
        for intento in range(self.get_parameter('intentos').value):
            self.decir('pedir_orden' if intento == 0 else 'repetir_orden', nombre=nombre)
            texto = self.c.hri.escuchar('orden')
            self.get_logger().info(f'[invitado] "{texto}"')
            if not texto:
                continue
            r = self.c.hri.interpretar_orden(texto)
            objeto, lugar = r.get('objeto'), r.get('lugar')
            if not objeto or not lugar:
                continue
            clase = self.nombres['objetos'].get(objeto.lower())
            waypoint = self.nombres['lugares'].get(lugar.lower(), lugar.lower().replace(' ', '_'))
            if clase is None:
                self.decir('objeto_desconocido', objeto=objeto)
                continue
            if waypoint not in self.c.nav.waypoints:
                self.decir('lugar_desconocido', lugar=lugar)
                continue
            return {'objeto': objeto, 'clase': clase, 'lugar': lugar, 'waypoint': waypoint}
        return None

    def traer_objeto(self, invitado):
        nombre = self.invitados.get(invitado, {}).get('nombre') or 'friend'
        orden = self.entender_orden(nombre)
        if orden is None:
            self.estado(f'no se entendio la orden de {invitado}')
            return False
        self.estado(f'orden de {invitado}: {orden}')
        self.decir('voy_por', objeto=orden['objeto'], lugar=orden['lugar'])
        self.ir(orden['waypoint'])
        if not self.c.vision.buscar_objeto(orden['clase']):
            self.get_logger().warn(f'Vision no confirmo {orden["clase"]}')
        self.estado(f'agarrando {orden["clase"]}')
        if not self.c.garra.agarrar(orden['clase']):
            self.get_logger().warn('Garra no confirmo que tiene el objeto')
        self.ir('sala')
        if not self.c.vision.esperar_persona_al_frente(invitado):
            self.get_logger().warn(f'Vision no confirmo que {invitado} esta al frente')
        self.decir('aqui_esta', nombre=nombre, objeto=orden['objeto'])
        entregado = self.c.garra.entregar()
        self.estado(f'orden terminada para {invitado}' if entregado else f'entrega sin confirmar para {invitado}')
        return entregado

    def presentar(self):
        ids = list(self.invitados)
        if len(ids) < 2:
            return
        lados = self.c.vision.personas_en_sofa()
        for actual, otro in ((ids[0], ids[1]), (ids[1], ids[0])):
            self.estado(f'presentando {otro} a {actual} ({lados.get(actual, "lado desconocido")})')
            self.decir('presentar',
                       nombre_a=self.invitados[actual]['nombre'] or 'friend',
                       nombre_b=self.invitados[otro]['nombre'] or 'our guest',
                       bebida_b=self.invitados[otro]['bebida'] or 'unknown')

    def recibir_bolsa(self):
        self.decir('pedir_bolsa')
        if not self.c.vision.buscar_objeto('bag'):
            self.get_logger().warn('Vision no confirmo la bolsa')
        self.decir('bolsa_seguridad')
        if not self.c.garra.proceder():
            self.get_logger().warn('Garra no confirmo que tiene la bolsa')
        self.estado('bolsa recibida')

    def secuencia(self):
        self.estado('inicio del reto')
        for invitado in ('invitado_1', 'invitado_2'):
            self.recibir_invitado(invitado)
            self.traer_objeto(invitado)
        self.presentar()
        self.recibir_bolsa()
        self.decir('terminado')
        self.estado('reto terminado')


def main(args=None):
    rclpy.init(args=args)
    node = TaskOrchestratorNode()
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
