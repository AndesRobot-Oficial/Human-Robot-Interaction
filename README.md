# andesrobot_hri

Paquetes de ROS 2 del equipo de **Interacción Humano-Robot (HRI)** de AndesRobot para
RoboCup@Home 2027, prueba 5.1 *Human Robot Interaction Challenge* (Receptionist).

> **Estado:** plantilla. Todo compila y los nodos arrancan, pero todavía no hacen su trabajo.
> El árbol de comportamiento recorre la prueba completa con *stubs* de los otros equipos.

## Requisitos

- Ubuntu 22.04 con ROS 2 Humble (contenedor Distrobox)
- `sudo apt install ros-humble-py-trees ros-humble-py-trees-ros python3-colcon-common-extensions`

## Instalación

```bash
mkdir -p ~/hri_ws/src && cd ~/hri_ws/src
git clone https://github.com/AndesRobot-Oficial/Human-Robot-Interaction.git andesrobot_hri
bash andesrobot_hri/scripts/download_models.sh
cd ~/hri_ws
colcon build --symlink-install
source install/setup.bash
```

## Uso

| Qué | Comando |
|---|---|
| Solo el árbol (con stubs) | `ros2 run hri_orchestrator task_orchestrator_node` |
| Árbol + gestor de diálogo | `ros2 launch hri_bringup orchestrator_only.launch.py` |
| Los 8 nodos de HRI | `ros2 launch hri_bringup hri_reto.launch.py` |
| Pruebas del árbol | `colcon test --packages-select hri_orchestrator && colcon test-result --verbose` |

Para que el árbol arranque, hay que enviar la señal de inicio:

```bash
ros2 topic pub --once /base/start_button std_msgs/msg/Bool "{data: true}"
```

## Paquetes

| Paquete | Nodos | Responsables |
|---|---|---|
| `hri_interfaces` | — (mensajes, servicios y acciones) | Sebastian |
| `hri_audio` | `audio_capture_node`, `speaker_node` | Allisson y Felipe |
| `hri_speech` | `asr_node`, `tts_node` | Allisson y Felipe |
| `hri_doorbell` | `doorbell_detector_node` | Por asignar |
| `hri_dialogue` | `dialogue_manager_node` | Por asignar |
| `hri_llm` | `llm_agent_node` | Juliana y Sara |
| `hri_orchestrator` | `task_orchestrator_node` (árbol de comportamiento) | Sebastian |
| `hri_bringup` | — (archivos launch) | Sebastian |

Los códigos en Python puro (sin ROS 2) van en los "motores", que se pueden probar solos:
`hri_speech/stt_engine.py`, `hri_speech/tts_engine.py` y `hri_llm/llm_backend.py`.

## Ramas

| Rama | Uso |
|---|---|
| `main` | Solo código que compila |
| `feature/orchestrator` | Árbol de comportamiento |
| `feature/tts-stt` | Audio, STT y TTS |
| `feature/llm` | LLM |

Cada pareja trabaja en su rama y pide integrar a `main` con un *pull request*.

## Documentación

- [Arquitectura](docs/arquitectura.md)
- [Árbol de la prueba 5.1](docs/arbol_reto.md)
- [Interfaces de otros equipos](docs/contratos_externos.md)
- [Decisiones y propuestas](docs/decisiones.md)

## Instalación con Docker (recomendada)

```bash
git clone git@github.com:AndesRobot-Oficial/Human-Robot-Interaction.git
cd Human-Robot-Interaction
bash scripts/download_models.sh
docker compose up -d --build
docker compose exec hri bash
# dentro del contenedor:
colcon build --symlink-install && source install/setup.bash
```

Guía completa: [docs/docker.md](docs/docker.md)

## ¿Vas a usar una librería nueva?

| Tipo | Dónde agregarla |
|---|---|
| Python (`pip install ...`) | `requirements.txt` |
| Sistema (`sudo apt install ...`) | `apt-packages.txt` |
| Paquete de ROS 2 | `apt-packages.txt` y el `package.xml` del paquete |
| Modelo | `models/` y `scripts/download_models.sh` (no se sube a GitHub) |

Después: `docker compose up -d --build`. Detalles: [docs/dependencias.md](docs/dependencias.md)
