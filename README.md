# Human-Robot-Interaction

Paquetes de ROS 2 del equipo de Interacción Humano-Robot (HRI) de AndesRobot para la prueba 5.1
(Receptionist) de RoboCup@Home 2027.

## Instalación

Se trabaja dentro de un contenedor de Docker que ya trae ROS 2 Humble, así que no hace falta
instalar ROS en el computador.

```bash
sudo apt install -y docker.io docker-compose-v2 docker-buildx
sudo usermod -aG docker $USER        # luego cerrar sesión y volver a entrar

git clone git@github.com:AndesRobot-Oficial/Human-Robot-Interaction.git
cd Human-Robot-Interaction
bash scripts/download_models.sh
docker compose up -d --build         # la primera vez tarda varios minutos
```

Si tu usuario no tiene el id 1000 (`id -u`), revisa `docs/docker.md` antes de construir.

## Uso

Git y `docker compose` se usan en el computador; compilar y ejecutar, dentro del contenedor.
El repositorio está montado en `~/hri_ws/src/andesrobot_hri`, así que lo que edites afuera se
ve adentro.

```bash
docker compose up -d                 # arrancar el contenedor
docker compose exec hri bash         # entrar (se pueden abrir varias terminales)

# dentro del contenedor
colcon build --symlink-install
source install/setup.bash
ros2 run hri_orchestrator task_orchestrator_node
```

Desde otra terminal del contenedor se envían la señal de inicio y el timbre:

```bash
ros2 topic pub --once /base/start_button std_msgs/msg/Bool "{data: true}"
ros2 topic pub --once /hri/doorbell_detected std_msgs/msg/Bool "{data: true}"
```

`ros2 launch hri_bringup hri_reto.launch.py` levanta todos los nodos de HRI y
`colcon test --packages-select hri_orchestrator` corre las pruebas del árbol.

## Árbol de comportamiento

`task_orchestrator_node` decide qué hace el robot en cada momento de la prueba. No mueve motores
ni procesa audio: le pide cada tarea al nodo encargado (Navegación, Visión, el gestor de
diálogo) y espera la respuesta.

Está hecho con py_trees. El árbol se recorre cada 0,5 s y cada bloque responde `SUCCESS`,
`FAILURE` o `RUNNING` (todavía trabajando). Una secuencia `[-]` ejecuta sus hijos en orden y se
detiene si uno falla, un selector `[o]` los prueba hasta que uno funcione y un paralelo `/_/`
ejecuta varios a la vez, por ejemplo mirar al invitado mientras le habla.

```
Root
 ├─ Topics2BB          copia los tópicos al blackboard
 └─ [o] Priorities
     ├─ Emergency      paro de emergencia
     ├─ Receptionist   la prueba, una sola vez
     │   ├─ Setup
     │   ├─ Guest1
     │   ├─ Guest2     incluye recibir la bolsa
     │   ├─ Introduce
     │   └─ BagToHost
     └─ Idle
```

Con cada invitado el robot espera el timbre, va a la puerta, la abre si está cerrada, lo
encuentra, le pregunta el nombre y la bebida, lo lleva a la sala y le ofrece un asiento. Si se
activa el paro de emergencia el árbol se detiene, y al soltarlo sigue donde iba.

Lo que el árbol va sabiendo (nombres, bebidas, poses) se guarda en el blackboard; los nombres de
esas variables están en `blackboard_keys.py`. Los otros equipos se simulan con stubs en
`behaviours/external/`, y cuando entreguen sus nodos se cambia cada stub por el cliente real sin
tocar el árbol.

En `hri_orchestrator/hri_orchestrator/`:

- `tree/`: la forma del árbol, un archivo por rama
- `behaviours/hri/`: comportamientos de HRI
- `behaviours/external/`: stubs de los otros equipos
- `../config/places.yaml`: lugares del mapa (`start`, `entrance_door`, `living_room`)

El detalle está en `docs/arbol_reto.md`.

## Librerías nuevas

Si usas una librería que no está declarada, tu código no le va a funcionar al resto del equipo.
Agrégala y luego ejecuta `docker compose up -d --build`:

- Python: `requirements.txt`
- Sistema (apt): `apt-packages.txt`
- Paquete de ROS 2: `apt-packages.txt` y el `package.xml` del paquete
- Modelos: `models/` y `scripts/download_models.sh` (no se suben a GitHub)

## Paquetes

| Paquete | Contenido | Responsable |
|---|---|---|
| `hri_interfaces` | Mensajes, servicios y acciones de HRI | Sebastian |
| `hri_audio` | Micrófono y parlante | Allisson y Felipe |
| `hri_speech` | STT y TTS | Allisson y Felipe |
| `hri_doorbell` | Detección del timbre | Por asignar |
| `hri_dialogue` | Gestor de diálogo | Sebastian |
| `hri_llm` | LLM | Juliana y Sara |
| `hri_orchestrator` | Árbol de comportamiento | Sebastian |
| `hri_bringup` | Archivos launch | Sebastian |

El código en Python puro de STT, TTS y LLM va en `stt_engine.py`, `tts_engine.py` y
`llm_backend.py`, que se pueden probar sin ROS.

## Ramas

`main` solo recibe código que compila, por pull request. Cada pareja trabaja en su rama:
`feature/orchestrator`, `feature/tts-stt` o `feature/llm`.

Más documentación en `docs/`: Docker, dependencias, arquitectura, árbol de la prueba e
interfaces con los otros equipos.
