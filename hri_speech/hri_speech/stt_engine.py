
#from tts_engine import hablar_con_piper #sin uso actual
import queue, sys, sounddevice as sd
from vosk import Model, KaldiRecognizer
import time
import os 
import json

base_dir = os.path.dirname(os.path.abspath(__file__))
model_path =os.path.join(base_dir, "..", "models", "vosk-model-small-en-us-0.15")
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
    "bag": "bag", "pringles": "pringles", "rubik's cube": "rubik"
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



def limpiar(palabras):  # quita los [unk] de la lista de palabras
    return [p for p in palabras if p["word"] != "[unk]"]



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


        
q = queue.Queue()
def callback(indata, frames, M_time, status):
    if status: print(status, file=sys.stderr)
    q.put(bytes(indata))




samplerate = int(sd.query_devices(None, "input")["default_samplerate"])
gramatica = json.dumps(list(LUGARES) + list(OBJETOS) + RELLENO)
rec = KaldiRecognizer(model, samplerate, gramatica)
rec.SetWords(True)




#rec.SetEndpointerDelays(5.0, 0.4, 20.0)
print("🎙️  Escuchando... (Ctrl+C para salir)\n")


limtiempo= 80


with sd.RawInputStream(samplerate=samplerate, blocksize=4000, dtype="int16", channels=1, callback=callback):#muestras de audio
    inicio_audio= time.time() #fijar tiempo de inicio
    while time.time()- inicio_audio < limtiempo:
        data = q.get()
        if rec.AcceptWaveform(data):#vosk reconoce la frase y devuelve el resultado en json
            mostrar(rec.Result()) #funcion mostrar resultado por frase
print("            tiempo terminado")

mostrar(rec.FinalResult())# funcion procesar para la frase final


