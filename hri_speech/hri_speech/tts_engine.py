"""Motor de TTS (espeak-ng + voz mbrola) en Python puro, sin ROS 2.
Lo usan tts_node y scripts/prueba_voz.py.

Codigo de TTS de Allisson y Felipe, puesto en la clase TtsEngine:
    TtsEngine(voice, speed, volume)
    synthesize(texto) -> (audio, sample_rate)   audio PCM int16 mono, sin reproducir
    say(texto)        -> sintetiza y reproduce (para pruebas)

Prueba sola (dentro del contenedor):
    python3 hri_speech/hri_speech/tts_engine.py
"""
import os
import re
import subprocess
import tempfile
import wave
from typing import Tuple

dicc_pronun = {
    "cocacola": "coh cah colah",
    "coca-cola": "coh cah colah",
    "MILO": "may loh",
    "UNAB": "uhnab",
    "chile": "shih leh",
    "andes": "ahn des",
    "robot": "roh boht",
    "MARTA": "marh tah",
    "pepsi": "pet ci",
    "fanta": "fan tah",
}


def correct_pronun(text):
    for palabra, pronun in dicc_pronun.items():
        # palabra completa, sin importar mayusculas ("Robot" y "robot", pero no "robots")
        text = re.sub(rf'\b{re.escape(palabra)}\b', pronun, text, flags=re.IGNORECASE)
    return text


class TtsEngine:
    """Convierte texto en ingles en audio."""

    def __init__(self, voice: str = 'mb-us2', speed: int = 160, volume: int = 100):
        self.voice = voice
        self.speed = speed
        self.volume = volume

    def synthesize(self, text: str) -> Tuple[bytes, int]:
        """Devuelve (audio, sample_rate) del texto, sin reproducirlo."""
        text = correct_pronun(text)
        fd, wav_path = tempfile.mkstemp(suffix='.wav')
        os.close(fd)
        try:
            cmd = ['espeak-ng', '-v', self.voice, '-s', str(self.speed),
                   '-a', str(self.volume), '-w', wav_path, text]
            if subprocess.run(cmd, capture_output=True).returncode != 0 \
                    or os.path.getsize(wav_path) == 0:
                # si la voz mbrola no esta instalada, usar la de espeak-ng
                cmd[2] = 'en-us'
                subprocess.run(cmd, capture_output=True, check=True)
            with wave.open(wav_path, 'rb') as w:
                return w.readframes(w.getnframes()), w.getframerate()
        finally:
            os.remove(wav_path)

    def say(self, text: str) -> None:
        """Sintetiza y reproduce en el parlante (espera a que termine)."""
        import numpy as np
        import sounddevice as sd

        audio, rate = self.synthesize(text)
        sd.play(np.frombuffer(audio, dtype=np.int16), rate)
        sd.wait()


if __name__ == "__main__":
    # Prueba sin ROS 2: decir una frase
    text_to_synth = ("MARTA and MILO are two robots that can bring drinks such as Pepsi, "
                     "Coca-Cola, or Fanta. They belong to Andes Robot; furthermore, MILO is "
                     "from Chile, and MARTA is from Colombia.")
    print("texto en lenguaje original: ", text_to_synth)
    print("texto con cambio de pronunciacion: ", correct_pronun(text_to_synth))
    TtsEngine().say(text_to_synth)
