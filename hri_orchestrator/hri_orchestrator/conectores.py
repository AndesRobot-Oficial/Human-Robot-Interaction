import importlib
import json
import math
import os
import threading
import time

import yaml
from ament_index_python.packages import get_package_share_directory
from rclpy.action import ActionClient


def carpeta_config():
    return os.path.join(get_package_share_directory('hri_orchestrator'), 'config')


def cargar_yaml(nombre, carpeta=None):
    ruta = nombre if os.path.isabs(nombre) else os.path.join(carpeta or carpeta_config(), nombre)
    with open(ruta) as f:
        return yaml.safe_load(f) or {}


def tipo_mensaje(texto):
    paquete, clase, nombre = texto.split('/')
    return getattr(importlib.import_module(f'{paquete}.{clase}'), nombre)


def esperar_futuro(futuro, tiempo):
    listo = threading.Event()
    futuro.add_done_callback(lambda _: listo.set())
    return listo.wait(tiempo)


class Salida:

    def __init__(self, node, spec):
        self.activa = bool(spec and spec.get('nombre'))
        if self.activa:
            self.tipo = tipo_mensaje(spec['mensaje'])
            self.pub = node.create_publisher(self.tipo, spec['nombre'], 10)

    def enviar(self, valor):
        if self.activa:
            self.pub.publish(self.tipo(data=valor))


class Entrada:

    def __init__(self, node, spec):
        self.ultimo = None
        self.evento = threading.Event()
        if spec and spec.get('nombre'):
            node.create_subscription(tipo_mensaje(spec['mensaje']), spec['nombre'], self.recibir, 10)

    def recibir(self, msg):
        self.ultimo = msg
        self.evento.set()

    def limpiar(self):
        self.evento.clear()

    def esperar(self, condicion=None, tiempo=None):
        fin = None if tiempo is None else time.time() + tiempo
        while True:
            restante = None if fin is None else max(0.0, fin - time.time())
            if not self.evento.wait(restante):
                return None
            self.evento.clear()
            msg = self.ultimo
            if condicion is None or condicion(msg):
                return msg


class Hri:

    def __init__(self, node):
        self.say = Salida(node, {'nombre': '/hri/say', 'mensaje': 'std_msgs/msg/String'})
        self.hablando = Entrada(node, {'nombre': '/hri/hablando', 'mensaje': 'std_msgs/msg/Bool'})
        self.pedir_escucha = Salida(node, {'nombre': '/hri/escuchar', 'mensaje': 'std_msgs/msg/String'})
        self.texto = Entrada(node, {'nombre': '/hri/speech_text', 'mensaje': 'std_msgs/msg/String'})
        self.llm_in = Salida(node, {'nombre': '/hri/llm/entrada', 'mensaje': 'std_msgs/msg/String'})
        self.llm_out = Entrada(node, {'nombre': '/hri/llm/salida', 'mensaje': 'std_msgs/msg/String'})
        self.bert_in = Salida(node, {'nombre': '/hri/bert/entrada', 'mensaje': 'std_msgs/msg/String'})
        self.bert_out = Entrada(node, {'nombre': '/hri/bert/salida', 'mensaje': 'std_msgs/msg/String'})
        self.timbre_on = Salida(node, {'nombre': '/hri/timbre/activar', 'mensaje': 'std_msgs/msg/Bool'})
        self.timbre = Entrada(node, {'nombre': '/hri/doorbell_detected', 'mensaje': 'std_msgs/msg/Bool'})

    def decir(self, texto, tiempo=60.0):
        self.hablando.limpiar()
        self.say.enviar(texto)
        if self.hablando.esperar(lambda m: m.data, 5.0) is None:
            return False
        return self.hablando.esperar(lambda m: not m.data, tiempo) is not None

    def escuchar(self, modo='libre', tiempo=30.0):
        self.texto.limpiar()
        self.pedir_escucha.enviar(modo)
        msg = self.texto.esperar(None, tiempo)
        return msg.data if msg else ''

    def interpretar_invitado(self, texto, tiempo=60.0):
        self.llm_out.limpiar()
        self.llm_in.enviar(texto)
        msg = self.llm_out.esperar(None, tiempo)
        return json.loads(msg.data) if msg else {'nombre': None, 'bebida': None, 'entendido': False}

    def interpretar_orden(self, texto, tiempo=30.0):
        self.bert_out.limpiar()
        self.bert_in.enviar(texto)
        msg = self.bert_out.esperar(None, tiempo)
        return json.loads(msg.data) if msg else {'objeto': None, 'lugar': None, 'entendido': False}

    def esperar_timbre(self, tiempo=None):
        self.timbre.limpiar()
        self.timbre_on.enviar(True)
        return self.timbre.esperar(lambda m: m.data, tiempo) is not None


class Navegacion:

    def __init__(self, node, cfg, carpeta=None):
        self.node = node
        self.spec = cfg['ir_a']
        self.frame = cfg.get('frame', 'map')
        self.tiempo = float(cfg.get('tiempo_max_s', 120.0))
        datos = cargar_yaml(cfg.get('waypoints', 'casa_lugares.yaml'), carpeta)
        datos = datos.get('ubicaciones', datos)
        self.waypoints = {k: v for k, v in datos.items() if isinstance(v, dict) and 'x' in v}
        if self.spec['tipo'] == 'accion':
            self.tipo = tipo_mensaje(self.spec['mensaje'])
            self.cliente = ActionClient(node, self.tipo, self.spec['nombre'])
        else:
            self.salida = Salida(node, self.spec)
            self.llego = Entrada(node, cfg.get('llego'))

    def ir_a(self, lugar):
        if lugar not in self.waypoints:
            self.node.get_logger().error(f'el waypoint "{lugar}" no existe')
            return False
        if self.spec['tipo'] != 'accion':
            self.llego.limpiar()
            self.salida.enviar(lugar)
            return self.llego.esperar(lambda m: m.data == lugar, self.tiempo) is not None
        if not self.cliente.wait_for_server(timeout_sec=5.0):
            self.node.get_logger().error(f'Navegacion no responde en {self.spec["nombre"]}')
            return False
        d = self.waypoints[lugar]
        meta = self.tipo.Goal()
        meta.pose.header.frame_id = self.frame
        meta.pose.header.stamp = self.node.get_clock().now().to_msg()
        meta.pose.pose.position.x = float(d['x'])
        meta.pose.pose.position.y = float(d['y'])
        meta.pose.pose.orientation.z = math.sin(float(d.get('yaw', 0.0)) / 2.0)
        meta.pose.pose.orientation.w = math.cos(float(d.get('yaw', 0.0)) / 2.0)
        envio = self.cliente.send_goal_async(meta)
        if not esperar_futuro(envio, 10.0) or not envio.result().accepted:
            self.node.get_logger().error(f'Navegacion rechazo la meta {lugar}')
            return False
        resultado = envio.result().get_result_async()
        if not esperar_futuro(resultado, self.tiempo):
            envio.result().cancel_goal_async()
            self.node.get_logger().warn(f'{lugar}: se acabo el tiempo')
            return False
        return resultado.result().status == 4


class Vision:

    def __init__(self, node, cfg):
        self.registrar = Salida(node, cfg.get('registrar_persona'))
        self.registrada = Entrada(node, cfg.get('persona_registrada'))
        self.buscar = Salida(node, cfg.get('buscar_objeto'))
        self.objeto = Entrada(node, cfg.get('objeto_detectado'))
        self.posicion = Entrada(node, cfg.get('posicion_objeto'))
        self.al_frente = Entrada(node, cfg.get('persona_al_frente'))
        self.sofa = Entrada(node, cfg.get('personas_sofa'))

    def registrar_persona(self, persona, tiempo=30.0):
        self.registrada.limpiar()
        self.registrar.enviar(persona)
        return self.registrada.esperar(lambda m: m.data == persona, tiempo) is not None

    def buscar_objeto(self, clase, tiempo=30.0):
        self.objeto.limpiar()
        self.buscar.enviar(clase)
        return self.objeto.esperar(lambda m: m.data == clase, tiempo) is not None

    def posicion_objeto(self):
        return self.posicion.ultimo

    def esperar_persona_al_frente(self, persona, tiempo=30.0):
        self.al_frente.limpiar()
        return self.al_frente.esperar(lambda m: m.data == persona, tiempo) is not None

    def personas_en_sofa(self, tiempo=30.0):
        self.sofa.limpiar()
        msg = self.sofa.esperar(None, tiempo)
        return json.loads(msg.data) if msg else {}


class Garra:

    def __init__(self, node, cfg):
        self.pedir_agarre = Salida(node, cfg.get('agarrar'))
        self.tiene = Entrada(node, cfg.get('tiene_objeto'))
        self.pedir_entrega = Salida(node, cfg.get('entregar'))
        self.entregado = Entrada(node, cfg.get('entregado'))
        self.pedir_proceder = Salida(node, cfg.get('proceder'))

    def agarrar(self, objeto, tiempo=60.0):
        self.tiene.limpiar()
        self.pedir_agarre.enviar(objeto)
        return self.tiene.esperar(lambda m: m.data, tiempo) is not None

    def entregar(self, tiempo=30.0):
        self.entregado.limpiar()
        self.pedir_entrega.enviar(True)
        return self.entregado.esperar(lambda m: m.data, tiempo) is not None

    def proceder(self, tiempo=60.0):
        self.tiene.limpiar()
        self.pedir_proceder.enviar(True)
        return self.tiene.esperar(lambda m: m.data, tiempo) is not None


class Conectores:

    def __init__(self, node, archivo='topicos.yaml', carpeta=None):
        cfg = cargar_yaml(archivo, carpeta)
        self.hri = Hri(node)
        self.nav = Navegacion(node, cfg['navegacion'], carpeta)
        self.vision = Vision(node, cfg.get('vision', {}))
        self.garra = Garra(node, cfg.get('garra', {}))
        self.estado = Salida(node, cfg.get('orquestador', {}).get('estado'))
