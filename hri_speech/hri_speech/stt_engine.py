"""Motor de STT en Python puro (sin ROS 2). Lo usa asr_node.

Aqui va el codigo de STT de Allisson y Felipe (Vosk). Se puede probar solo,
sin ROS 2, ejecutando este archivo directamente.

Estado: PLANTILLA (sin funcionalidad).
"""
from typing import List, Optional, Tuple


class SttEngine:
    """Convierte bloques de audio (16 kHz, mono, 16 bits) en texto."""

    def __init__(self, model_path: str, sample_rate: int = 16000,
                 vocabulary: Optional[List[str]] = None):
        self.model_path = model_path
        self.sample_rate = sample_rate
        self.vocabulary = vocabulary or []   # nombres y bebidas para favorecerlos
        # TODO: cargar el modelo de Vosk y crear el KaldiRecognizer
        #       (con la gramatica de self.vocabulary si se usa)

    def accept_audio(self, data: bytes) -> Optional[Tuple[str, float]]:
        """Recibe un bloque de audio.

        Devuelve (texto, confianza) cuando se completa una frase, o None
        mientras la persona sigue hablando.
        """
        # TODO: pasar el audio a Vosk y, al terminar la frase,
        #       calcular la confianza promedio de las palabras
        return None

    def reset(self) -> None:
        """Descarta lo escuchado (por ejemplo, mientras habla el robot)."""
        # TODO: reiniciar el reconocedor
        pass


if __name__ == '__main__':
    # Prueba sin ROS 2: leer el microfono y mostrar el texto reconocido
    print('stt_engine: plantilla, sin prueba todavia')
