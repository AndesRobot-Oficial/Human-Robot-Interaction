"""speaker_node: unico nodo que usa el parlante.

Contrato (equipo HRI):
    Ofrece  /hri/play_sound   hri_interfaces/srv/PlaySound
            Peticion: sound_name (archivo en sounds/) o audio_data + sample_rate (voz del tts_node)
            Respuesta: success, cuando el audio TERMINO de sonar
    Lo usan task_orchestrator_node, tts_node

Prueba (dentro del contenedor):
    ros2 run hri_audio speaker_node
    ros2 service call /hri/play_sound hri_interfaces/srv/PlaySound "{sound_name: speaker_test}"
"""
import os
import threading
import wave

from ament_index_python.packages import get_package_share_directory
from hri_interfaces.srv import PlaySound
import numpy as np
import rclpy
from rclpy.node import Node
import sounddevice as sd


class SpeakerNode(Node):

    def __init__(self):
        super().__init__('speaker_node')

        # Parametros (config/audio_params.yaml)
        self.declare_parameter('device', 'default')
        self.declare_parameter(
            'sounds_dir',
            os.path.join(get_package_share_directory('hri_audio'), 'sounds'))

        device = self.get_parameter('device').value
        self.device = None if device in ('', 'default') else device
        self.lock = threading.Lock()        # un audio a la vez

        self.play_srv = self.create_service(
            PlaySound, '/hri/play_sound', self.on_play_sound)

        self.get_logger().info('speaker_node listo')

    def play(self, audio: bytes, sample_rate: int, channels: int = 1) -> None:
        """Reproduce audio PCM int16 y espera a que termine."""
        samples = np.frombuffer(audio, dtype=np.int16)
        if channels > 1:
            samples = samples.reshape(-1, channels)
        with self.lock:
            sd.play(samples, sample_rate, device=self.device)
            sd.wait()

    def on_play_sound(self, request, response):
        try:
            if request.sound_name:
                name = request.sound_name
                if not name.endswith('.wav'):
                    name += '.wav'
                path = os.path.join(self.get_parameter('sounds_dir').value, name)
                with wave.open(path, 'rb') as w:
                    audio = w.readframes(w.getnframes())
                    rate, channels = w.getframerate(), w.getnchannels()
                self.get_logger().info(f'Sonido: {name}')
                self.play(audio, rate, channels)
            else:
                self.play(bytes(request.audio_data), request.sample_rate or 16000)
            response.success = True
        except Exception as error:      # archivo que no existe, parlante ocupado...
            self.get_logger().error(f'No se pudo reproducir: {error}')
            response.success = False
        return response


def main(args=None):
    rclpy.init(args=args)
    node = SpeakerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
