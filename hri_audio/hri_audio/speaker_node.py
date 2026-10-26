"""speaker_node: unico nodo que usa el parlante.

Contrato (equipo HRI):
    Ofrece  /hri/play_sound   hri_interfaces/srv/PlaySound
            Peticion: sound_name (archivo en sounds/) o audio_data + sample_rate (voz del tts_node)
            Respuesta: success
    Lo usan task_orchestrator_node, tts_node

Estado: PLANTILLA (sin funcionalidad).
"""
import os

from ament_index_python.packages import get_package_share_directory
from hri_interfaces.srv import PlaySound
import rclpy
from rclpy.node import Node


class SpeakerNode(Node):

    def __init__(self):
        super().__init__('speaker_node')

        # Parametros (config/audio_params.yaml)
        self.declare_parameter('device', 'default')
        self.declare_parameter(
            'sounds_dir',
            os.path.join(get_package_share_directory('hri_audio'), 'sounds'))

        self.play_srv = self.create_service(
            PlaySound, '/hri/play_sound', self.on_play_sound)

        self.get_logger().info('speaker_node listo (plantilla)')

    def on_play_sound(self, request, response):
        if request.sound_name:
            # TODO: reproducir <sounds_dir>/<sound_name>.wav
            self.get_logger().info(f'[plantilla] reproducir sonido: {request.sound_name}')
        else:
            # TODO: reproducir request.audio_data a request.sample_rate
            self.get_logger().info(
                f'[plantilla] reproducir audio: {len(request.audio_data)} bytes')
        response.success = True
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
