

import queue, sys, sounddevice as sd
from vosk import Model, KaldiRecognizer
import time
import os 
import json

base_dir = os.path.dirname(os.path.abspath(__file__))
model_path =os.path.join(base_dir, "..", "models", "vosk-model-small-en-us-0.15")
model= Model(model_path) #para que funcione vosk dentro de la carpeta

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

def mostrar(resultado_json):
    texto, palabras = leer(resultado_json)
    confianza = cal_conf(palabras)

    if not texto :
        print("No se detectó ninguna frase.")
        return
    else:
        print(f"Frase: {texto}")

        print(f"Confianza: {confianza:.2f}")
        print("Palabras:")
        for p in palabras:
            print(f"  {p['word']} , conf: {p['conf']:.2f}")
    print(  )#

q = queue.Queue()
def callback(indata, frames, M_time, status):
    if status: print(status, file=sys.stderr)
    q.put(bytes(indata))

samplerate = int(sd.query_devices(None, "input")["default_samplerate"])
rec = KaldiRecognizer(model, samplerate)
rec.SetWords(True) # 

#rec.SetEndpointerDelays(5.0, 0.4, 20.0)
print("🎙️  Escuchando... (Ctrl+C para salir)\n")


limtiempo= 30


with sd.RawInputStream(samplerate=samplerate, blocksize=4000, dtype="int16", channels=1, callback=callback):#muestras de audio
    inicio_audio= time.time() #fijar tiempo de inicio
    while time.time()- inicio_audio < limtiempo:
        data = q.get()
        if rec.AcceptWaveform(data):#vosk reconoce la frase y devuelve el resultado en json
            mostrar(rec.Result()) #funcion mostrar resultado por frase
print("            tiempo terminado")

mostrar(rec.FinalResult())# funion procesar para la frase final

#print(rec.FinalResult())
