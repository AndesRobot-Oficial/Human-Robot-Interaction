import queue
import sys
import time

import numpy as np
import sounddevice as sd

CONFIG = {
    "f_min": 400.0,
    "f_max": 3000.0,
    "ratio_min": 0.6,
    "db_sobre_ruido": 10.0,
    "estabilidad_bins": 1,
    "duracion_min": 0.3,
    "bloque": 2048,
}


class DetectorTimbre:

    def __init__(self, samplerate, **config):
        self.cfg = dict(CONFIG, **config)
        self.sr = samplerate
        n = self.cfg["bloque"]
        self.ventana = np.hanning(n)
        self.freqs = np.fft.rfftfreq(n, 1.0 / samplerate)
        self.banda = (self.freqs >= self.cfg["f_min"]) & (self.freqs <= self.cfg["f_max"])
        self.tolerancia_hz = (self.cfg["estabilidad_bins"] + 0.5) * samplerate / n
        self.cuadros_min = max(2, int(np.ceil(self.cfg["duracion_min"] * samplerate / n)))
        self.ruido_db = None
        self.seguidos = 0
        self.f_inicio = None
        self.resto = np.zeros(0, dtype=np.float32)

    def medir(self, x):
        espectro = np.abs(np.fft.rfft(x * self.ventana)) ** 2
        banda = espectro[self.banda]
        total = banda.sum() + 1e-12
        i = int(np.argmax(banda))
        pico = banda[max(i - 2, 0):i + 3].sum()
        nivel_db = 10.0 * np.log10(total / len(x) + 1e-12)
        return {
            "nivel_db": round(float(nivel_db), 1),
            "frecuencia": round(float(self.freqs[self.banda][i]), 1),
            "ratio": round(float(pico / total), 2),
        }

    def actualizar_ruido(self, nivel_db):
        if self.ruido_db is None:
            self.ruido_db = nivel_db
        elif nivel_db < self.ruido_db:
            self.ruido_db = 0.7 * self.ruido_db + 0.3 * nivel_db
        else:
            self.ruido_db = 0.995 * self.ruido_db + 0.005 * nivel_db

    def es_tono(self, m):
        fuerte = m["nivel_db"] - self.ruido_db >= self.cfg["db_sobre_ruido"]
        limpio = m["ratio"] >= self.cfg["ratio_min"]
        estable = self.f_inicio is not None and abs(m["frecuencia"] - self.f_inicio) <= self.tolerancia_hz
        return fuerte and limpio, estable

    def procesar(self, datos):
        x = np.frombuffer(datos, dtype=np.int16).astype(np.float32) / 32768.0
        self.resto = np.concatenate([self.resto, x])
        n = self.cfg["bloque"]
        detectado = False
        while len(self.resto) >= n:
            cuadro, self.resto = self.resto[:n], self.resto[n:]
            m = self.medir(cuadro)
            tono, estable = self.es_tono(m) if self.ruido_db is not None else (False, False)
            if tono:
                if self.seguidos == 0 or not estable:
                    self.seguidos = 1
                    self.f_inicio = m["frecuencia"]
                else:
                    self.seguidos += 1
                if self.seguidos >= self.cuadros_min:
                    detectado = True
            else:
                self.seguidos = 0
                self.f_inicio = None
                self.actualizar_ruido(m["nivel_db"])
            self.ultima = m
        return detectado


def esperar_timbre(limite=None, dispositivo=None, **config):
    samplerate = int(sd.query_devices(dispositivo, "input")["default_samplerate"])
    detector = DetectorTimbre(samplerate, **config)
    cola = queue.Queue()

    def guardar(indata, frames, M_time, status):
        cola.put(bytes(indata))

    with sd.RawInputStream(samplerate=samplerate, blocksize=detector.cfg["bloque"], dtype="int16",
                           channels=1, device=dispositivo, callback=guardar):
        inicio = time.time()
        while limite is None or time.time() - inicio < limite:
            try:
                datos = cola.get(timeout=0.2)
            except queue.Empty:
                continue
            if detector.procesar(datos):
                return True
    return False


def calibrar(segundos=20.0, dispositivo=None):
    samplerate = int(sd.query_devices(dispositivo, "input")["default_samplerate"])
    detector = DetectorTimbre(samplerate)
    cola = queue.Queue()

    def guardar(indata, frames, M_time, status):
        cola.put(bytes(indata))

    with sd.RawInputStream(samplerate=samplerate, blocksize=detector.cfg["bloque"], dtype="int16",
                           channels=1, device=dispositivo, callback=guardar):
        inicio = time.time()
        while time.time() - inicio < segundos:
            try:
                datos = cola.get(timeout=0.2)
            except queue.Empty:
                continue
            detectado = detector.procesar(datos)
            m = getattr(detector, "ultima", None)
            if m and detector.ruido_db is not None:
                print(f"nivel {m['nivel_db']:6.1f} dB | ruido {detector.ruido_db:6.1f} dB | "
                      f"frecuencia {m['frecuencia']:7.1f} Hz | ratio {m['ratio']:.2f} | "
                      f"seguidos {detector.seguidos}" + ("  <-- TIMBRE" if detectado else ""))


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "calibrar":
        calibrar()
        return
    print("Esperando el timbre... (Ctrl+C para salir)")
    while True:
        if esperar_timbre():
            print("TIMBRE detectado")
            time.sleep(2.0)


if __name__ == "__main__":
    main()
