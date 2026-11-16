# Human-Robot-Interaction

Paquetes de ROS 2 (Humble) del equipo de Interacción Humano-Robot (HRI) de AndesRobot para RoboCup@Home 2027.
HRI tiene tres partes: **Voz** (STT, TTS y timbre), **Intérprete** (LLM para nombre y bebida, BERT para órdenes)
y **Orquestador** (lleva el flujo del reto y es el único que da órdenes a Navegación, Visión y Garra).

| Paquete | Qué tiene |
|---|---|
| `hri_speech` | `stt_engine.py` (Vosk), `tts_engine.py` (espeak-ng), `timbre_engine.py` y sus nodos `stt_node`, `tts_node`, `timbre_node` |
| `hri_llm` | Extractores de nombre y bebida con Phi-4 Mini (Ollama) y `llm_node` |
| `hri_bert` | Extractor de objeto y lugar con el BERT de Juan Rivera y `bert_node` |
| `hri_orchestrator` | `task_orchestrator_node` (el flujo), `conectores.py` (cómo se habla con los otros equipos), `simulador_equipos` y la configuración |
| `hri_bringup` | `hri.launch.py`, arranca todo |

La arquitectura, los tópicos y lo que se le agregó a cada avance están en [`docs/arquitectura.md`](docs/arquitectura.md).

## 1. Instalar (una vez)

En el computador:

```bash
git clone git@github.com:AndesRobot-Oficial/Human-Robot-Interaction.git
cd Human-Robot-Interaction
bash scripts/download_models.sh
curl -fsSL https://ollama.com/install.sh | sh
ollama pull phi4-mini:3.8b
docker compose up -d --build
```

`download_models.sh` baja Vosk (`models/vosk/`) y BERT (`models/bert/`). Ollama corre en el computador, fuera de Docker;
el contenedor lo ve porque usa la red del computador (`network_mode: host`).

Por defecto el contenedor usa `ROS_DOMAIN_ID=12` y `ROS_LOCALHOST_ONLY=0`, como Martha. Para cambiarlo:
`ROS_DOMAIN_ID=42 docker compose up -d`.

Compilar (dentro del contenedor, `docker compose exec hri bash`):

```bash
cd ~/hri_ws && colcon build --symlink-install && source install/setup.bash
```

Si `colcon build` falla con `can't copy ... doesn't exist`, quedaron restos de una compilación vieja:
`rm -rf ~/hri_ws/build/* ~/hri_ws/install/*` y compilar de nuevo.

## 2. Probar cada avance solo (sin ROS)

Dentro del contenedor, en `~/hri_ws/src/andesrobot_hri`:

| Avance | Comando | Qué hacer |
|---|---|---|
| STT libre | `python3 -c "import sys; sys.path.insert(0,'hri_speech'); from hri_speech.stt_engine import escuchar; print(escuchar('libre'))"` | Decir "My name is John and I like coffee" |
| STT orden | lo mismo con `escuchar('orden')` | Decir "Bring me the bowl from the kitchen" |
| TTS | `python3 hri_speech/hri_speech/tts_engine.py` | Escuchar la frase de prueba |
| LLM | `python3 hri_llm/hri_llm/name_extractor.py --text "Hi, my name is John and I like coffee"` | No hay que hablar |
| BERT | `python3 hri_bert/hri_bert/bert_extractor.py "bring me the bowl from the kitchen"` | No hay que hablar |
| Timbre | `python3 hri_speech/hri_speech/timbre_engine.py` (o `... calibrar`) | Poner un sonido de timbre |

## 3. Probar todo HRI en ROS 2, sin los otros equipos

```bash
ros2 launch hri_bringup hri.launch.py simular:=true
```

`simular:=true` arranca `simulador_equipos`, que responde como Navegación (acción `/nav/navigate_to_pose`),
Visión y Garra. En otra terminal:

```bash
ros2 topic pub --once /orquestador/iniciar std_msgs/msg/Bool "{data: true}"
```

Después: poner el timbre, decir el nombre y la bebida, y cuando pregunte qué traer, decir por ejemplo
"Bring me the bowl from the kitchen". El robot hace el flujo con los dos invitados, los presenta y recibe la bolsa.
`ros2 topic echo /orquestador/estado` muestra en qué paso va.

Argumentos del launch: `simular` (false), `iniciar` (false: arranca solo, sin el `pub`),
`esperar_timbre` (true: false salta el timbre).

Para probar un nodo suelto se puede publicar a mano, por ejemplo
`ros2 topic pub --once /hri/say std_msgs/msg/String "{data: 'Hello'}"`.

## 4. Con los otros equipos

```bash
ros2 launch hri_bringup hri.launch.py
```

Todos los contenedores deben tener el mismo `ROS_DOMAIN_ID` y `ROS_LOCALHOST_ONLY`.
Lo que HRI espera de cada equipo está en `hri_orchestrator/config/topicos.yaml`. Si un equipo usa otro nombre
de tópico, se cambia ahí sin tocar código (ver `docs/arquitectura.md`).

## 5. Configuración (sin tocar código)

| Archivo | Para qué |
|---|---|
| `hri_orchestrator/config/frases.yaml` | Todo lo que dice el robot. `{nombre}`, `{objeto}`, etc. se reemplazan solos |
| `hri_orchestrator/config/nombres.yaml` | `lugares_reto`: lugares del flujo → waypoint (`puerta: indoor`). `lugares`: lo que dice la persona → waypoint (`fridge: refrigerator`). `objetos`: lo que dice la persona → clase de Visión (`red bull: redbull_can`) |
| `hri_orchestrator/config/topicos.yaml` | Tópicos y acciones de Navegación, Visión y Garra |
| `hri_orchestrator/config/casa_lugares.yaml` | Copia de los waypoints de Navegación (repo `Navegation`, `maps/casa_lugares.yaml`) |
| `hri_speech/config/voz.yaml` | Límite y pausa del STT, voz del TTS (`mb-us1` Martha, `en-us` Milo), valores del timbre |

## 6. Pendiente con otros equipos

- `puerta → indoor`: Navegación no tiene un waypoint "puerta".
- Visión: los tópicos de personas (`/vision/registrar_persona`, `/vision/persona_registrada`, `/vision/persona_al_frente`,
  `/vision/personas_sofa`) y `/vision/buscar_objeto` son propuesta de HRI. Los de objetos (`/detected_object`, `/object_position`) son los de su repo.
- Garra: todos sus tópicos son propuesta de HRI.
- Objetos: Visión no tiene `cup`.
