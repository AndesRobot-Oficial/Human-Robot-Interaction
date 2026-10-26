"""Motor de TTS en Python puro (sin ROS 2). Lo usa tts_node.

Aqui va el codigo de TTS de Allisson y Felipe (espeak-ng). Se puede probar
solo, sin ROS 2, ejecutando este archivo directamente.

Estado: PLANTILLA (sin funcionalidad).
"""
from typing import Tuple


class TtsEngine:
    """Convierte texto en ingles en audio."""

    def __init__(self, voice: str = 'mb-us1', speed: int = 160, volume: int = 100):
        self.voice = voice
        self.speed = speed
        self.volume = volume
        # TODO: verificar que espeak-ng y la voz esten disponibles
        #       (y el diccionario de pronunciacion de nombres y bebidas)

    def synthesize(self, text: str) -> Tuple[bytes, int]:
        """Devuelve (audio, sample_rate) del texto, sin reproducirlo.

        La reproduccion la hace speaker_node por /hri/play_sound.
        """
        # TODO: generar el audio con espeak-ng (por ejemplo, a un WAV en memoria)
        return b'', 16000


if __name__ == '__main__':
    # Prueba sin ROS 2: sintetizar una frase y guardarla en un WAV
    print('tts_engine: plantilla, sin prueba todavia')
