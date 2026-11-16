import queue

import rclpy
import sounddevice as sd
from rclpy.node import Node
from std_msgs.msg import Bool

from hri_speech import timbre_engine


class TimbreNode(Node):

    def __init__(self):
        super().__init__('timbre_node')
        for clave, valor in timbre_engine.CONFIG.items():
            self.declare_parameter(clave, valor)
        self.declare_parameter('dispositivo', '')
        self.stream = None
        self.detector = None
        self.cola = queue.Queue()
        self.pub = self.create_publisher(Bool, '/hri/doorbell_detected', 10)
        self.create_subscription(Bool, '/hri/timbre/activar', self.on_activar, 10)
        self.create_timer(0.05, self.procesar)
        self.get_logger().info('timbre_node listo: /hri/timbre/activar true para empezar a escuchar')

    def on_activar(self, msg):
        if msg.data:
            self.abrir()
        else:
            self.cerrar()

    def abrir(self):
        if self.stream is not None:
            return
        config = {clave: self.get_parameter(clave).value for clave in timbre_engine.CONFIG}
        dispositivo = self.get_parameter('dispositivo').value or None
        samplerate = int(sd.query_devices(dispositivo, 'input')['default_samplerate'])
        self.detector = timbre_engine.DetectorTimbre(samplerate, **config)
        self.cola = queue.Queue()
        self.stream = sd.RawInputStream(samplerate=samplerate, blocksize=config['bloque'], dtype='int16',
                                        channels=1, device=dispositivo, callback=self.guardar)
        self.stream.start()
        self.get_logger().info('escuchando el timbre...')

    def cerrar(self):
        if self.stream is None:
            return
        self.stream.stop()
        self.stream.close()
        self.stream = None
        self.get_logger().info('microfono liberado')

    def guardar(self, indata, frames, M_time, status):
        self.cola.put(bytes(indata))

    def procesar(self):
        if self.stream is None:
            return
        while not self.cola.empty():
            if self.detector.procesar(self.cola.get()):
                self.get_logger().info('TIMBRE detectado')
                self.pub.publish(Bool(data=True))
                self.cerrar()
                return


def main(args=None):
    rclpy.init(args=args)
    node = TimbreNode()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, rclpy.executors.ExternalShutdownException):
        pass
    finally:
        node.cerrar()
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
