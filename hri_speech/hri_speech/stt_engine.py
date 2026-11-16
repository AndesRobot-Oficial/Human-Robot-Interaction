
#from tts_engine import hablar_con_piper #sin uso actual
import queue, sys, sounddevice as sd
from vosk import Model, KaldiRecognizer
import time
import os 
import json

base_dir = os.path.dirname(os.path.realpath(__file__))


def ruta_modelo(nombre="vosk-model-small-en-us-0.15"):
    opciones = [
        os.path.join(os.environ.get("HRI_MODELS_DIR", ""), "vosk", nombre),
        os.path.join(base_dir, "..", "..", "models", "vosk", nombre),
        os.path.join(base_dir, "..", "models", nombre),
    ]
    for ruta in opciones:
        if os.path.isdir(ruta):
            return ruta
    return opciones[-1]


model_path = ruta_modelo()
model= Model(model_path) #para que funcione vosk dentro de la carpeta




LUGARES = {
    "base": "base",
    "bed": "bed",
    "bedroom": "bedroom",
    "cabinet": "cabinet",
    "counter": "counter",
    "dishwasher": "dishwasher",
    "indoor": "indoor",
    "kitchen": "kitchen",
    "laundry": "laundry",
    "outdoor": "outdoor",
    "refrigerator": "refrigerator",
    "shelf": "shelf",
    "sink": "sink",
    "sofa": "sofa",
    "table": "table",
    "bedside table": "bedside_table",
    "coat rack": "coat_rack",
    "coffee table": "coffee_table",
    "cooking table": "cooking_table",
    "dining table": "dining_table",
    "dinner table": "dinner_table",
    "kitchen trash bin": "kitchen_trash_bin",
    "laundry table": "laundry_table",
    "laundry trash bin": "laundry_trash_bin",
    "living room": "living_room",
    "washing machine": "washing_machine",
    "tv stand": "tv_stand",
}


OBJETOS = {
    "cup": "cup", "bowl": "bowl", "red bull": "redbull", "card": "card",
    "fork":"fork", "spoon":"spoon", "bottle":"bottle",
    "bag": "bag", "pringles": "pringles", "rubik cube": "rubik", "rubik": "rubik"
}
RELLENO = [

    "go", "bring", "take", "put", "pick", "up", "place", "get", "give",
    "grab", "find", "carry", "move",
    "me", "it", "you", "i",
    "the", "a", "an",
    "in", "on", "to", "from", "at", "into", "can",
    "yes", "no",

    # ruido o palabras desconocidas
    "[unk]"
]


UMBRAL=0.6
def limpiar(palabras):  # quita los [unk] de la lista de palabras
    return [p for p in palabras if p["word"] != "[unk]"]




def buscar(palabras, diccionario):  # busca lugar u objeto y su confianza
    lista = [p["word"] for p in palabras]
    for frase in sorted(diccionario, key=len, reverse=True):
        partes = frase.split()
        n = len(partes)
        for i in range(len(lista) - n + 1):
            if lista[i:i + n] == partes:
                conf = min(p["conf"] for p in palabras[i:i + n])
                return diccionario[frase], conf
    return None, 0.0




def leer(resultado_json): # funcion para leer el resultado de la frase
    r = json.loads(resultado_json)#archivo json con el resultado de la frase
    texto = r.get("text", "")# obtener el texto de la frase var texto
    palabras = r.get("result", [])
    
    return texto, palabras 



def cal_conf(palabras):# funcion para calcular la confianza prom de la frase
    if palabras:
        confianza = sum(p["conf"] for p in palabras) / len(palabras)
    else:
        confianza = 0.0
    return confianza



def imprimir_frase(palabras):  # frase y confianza promedio
    texto_limpio = " ".join(p["word"] for p in palabras)
    print(f"Frase: {texto_limpio}")
    print(f"Confianza: {cal_conf(palabras):.2f}")
    print("Palabras:")
    for p in palabras:
        print(f"  {p['word']} , conf: {p['conf']:.2f}")




def revisar(nombre, valor, conf):  # avisa si la confianza es muy baja
    if valor and conf < UMBRAL:
        print(f"{nombre} : {valor} ({conf:.2f}) No seguro")


def mostrar(resultado_json):
    texto, palabras = leer(resultado_json)

    if not texto:  # sin sonido
        print("No se escuchó nada.")
        return

    palabras = limpiar(palabras)
    if not palabras:  # solo [unk]
        print("No entendido\n")
        return

    imprimir_frase(palabras)

    lugar, conf_l = buscar(palabras, LUGARES)
    objeto, conf_o = buscar(palabras, OBJETOS)
    revisar("Lugar", lugar, conf_l)
    revisar("Objeto", objeto, conf_o)

    print(f"Lugar: {lugar} ({conf_l:.2f}) | Objeto: {objeto} ({conf_o:.2f})\n")


def crear_reconocedor(modo, samplerate):
    if modo == "libre":
        rec = KaldiRecognizer(model, samplerate)
    else:
        gramatica = json.dumps(list(LUGARES) + list(OBJETOS) + RELLENO)
        rec = KaldiRecognizer(model, samplerate, gramatica)
    rec.SetWords(True)
    return rec


def resumir(palabras):
    if not palabras:
        return None
    lugar, conf_l = buscar(palabras, LUGARES)
    objeto, conf_o = buscar(palabras, OBJETOS)
    return {
        "texto": " ".join(p["word"] for p in palabras),
        "confianza": round(cal_conf(palabras), 2),
        "lugar": lugar,
        "objeto": objeto,
    }


def analizar(resultado_json):
    texto, palabras = leer(resultado_json)
    return resumir(limpiar(palabras))


def escuchar(modo="orden", limite=15.0, dispositivo=None, pausa=1.5):
    samplerate = int(sd.query_devices(dispositivo, "input")["default_samplerate"])
    rec = crear_reconocedor(modo, samplerate)
    cola = queue.Queue()
    palabras = []
    ultima_voz = None

    def guardar(indata, frames, M_time, status):
        cola.put(bytes(indata))

    with sd.RawInputStream(samplerate=samplerate, blocksize=4000, dtype="int16", channels=1,
                           device=dispositivo, callback=guardar):
        inicio = time.time()
        while time.time() - inicio < limite:
            try:
                data = cola.get(timeout=0.2)
            except queue.Empty:
                data = None
            if data is not None:
                if rec.AcceptWaveform(data):
                    nuevas = limpiar(leer(rec.Result())[1])
                    if nuevas and cal_conf(nuevas) >= UMBRAL:
                        palabras += nuevas
                        ultima_voz = time.time()
                elif json.loads(rec.PartialResult()).get("partial"):
                    ultima_voz = time.time()
            if palabras and ultima_voz and time.time() - ultima_voz > pausa:
                break
    final = limpiar(leer(rec.FinalResult())[1])
    if final and cal_conf(final) >= UMBRAL:
        palabras += final
    return resumir(palabras)


q = queue.Queue()
def callback(indata, frames, M_time, status):
    if status: print(status, file=sys.stderr)
    q.put(bytes(indata))


limtiempo= 80


def main():
    modo = sys.argv[1] if len(sys.argv) > 1 else "orden"
    samplerate = int(sd.query_devices(None, "input")["default_samplerate"])
    rec = crear_reconocedor(modo, samplerate)

    #rec.SetEndpointerDelays(5.0, 0.4, 20.0)
    print("🎙️  Escuchando... (Ctrl+C para salir)\n")

    with sd.RawInputStream(samplerate=samplerate, blocksize=4000, dtype="int16", channels=1, callback=callback):#muestras de audio
        inicio_audio= time.time() #fijar tiempo de inicio
        while time.time()- inicio_audio < limtiempo:
            data = q.get()
            if rec.AcceptWaveform(data):#vosk reconoce la frase y devuelve el resultado en json
                mostrar(rec.Result()) #funcion mostrar resultado por frase
    print("            tiempo terminado")

    mostrar(rec.FinalResult())# funcion procesar para la frase final


if __name__ == "__main__":
    main()
