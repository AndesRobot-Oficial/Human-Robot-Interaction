# Arquitectura de HRI

Basada en la propuesta de la líder del equipo (diagrama de nodos y contrato de integración).

## Nodos

| Nodo | Paquete | Qué hace |
|---|---|---|
| `audio_capture_node` | `hri_audio` | Único nodo que abre el micrófono |
| `speaker_node` | `hri_audio` | Único nodo que usa el parlante |
| `asr_node` | `hri_speech` | Audio → texto (Vosk) |
| `tts_node` | `hri_speech` | Texto → voz (espeak-ng) |
| `doorbell_detector_node` | `hri_doorbell` | Detecta el timbre |
| `dialogue_manager_node` | `hri_dialogue` | Maneja cada turno de diálogo que pide el orquestador |
| `llm_agent_node` | `hri_llm` | Consulta el LLM (modo "reto": extraer nombre y bebida) |
| `task_orchestrator_node` | `hri_orchestrator` | Árbol de comportamiento: decide qué hace el robot y lo pide a cada equipo |

## Conexiones dentro de HRI

```
micrófono ─► audio_capture_node ─/hri/audio─┬─► asr_node ─/hri/speech_text─► dialogue_manager_node
                                            └─► doorbell_detector_node ─/hri/doorbell_detected─► task_orchestrator_node

task_orchestrator_node ─/hri/converse, /hri/remember─► dialogue_manager_node ─/hri/llm_chat─► llm_agent_node
dialogue_manager_node ─/hri/say─► tts_node ─/hri/play_sound─► speaker_node ─► parlante
task_orchestrator_node ─/hri/play_sound─► speaker_node
tts_node ─/hri/speaking─► dialogue_manager_node, asr_node
task_orchestrator_node ─/hri/mode─► dialogue_manager_node, llm_agent_node
```

## Interfaces de HRI

| Interfaz | Tipo | Publica u ofrece | La usa |
|---|---|---|---|
| `/hri/audio` | Tópico `audio_common_msgs/AudioData` (16 kHz, mono) | `audio_capture_node` | `asr_node`, `doorbell_detector_node` |
| `/hri/doorbell_detected` | Tópico `std_msgs/Bool` (una vez por timbre) | `doorbell_detector_node` | `task_orchestrator_node` |
| `/hri/play_sound` | Servicio `PlaySound.srv` | `speaker_node` | `task_orchestrator_node`, `tts_node` |
| `/hri/speech_text` | Tópico `std_msgs/String` | `asr_node` | `dialogue_manager_node` |
| `/hri/say` | Tópico `std_msgs/String` | `dialogue_manager_node` | `tts_node` |
| `/hri/speaking` (*) | Tópico `std_msgs/Bool` | `tts_node` | `dialogue_manager_node`, `asr_node` |
| `/hri/dialogue_state` | Tópico `DialogueState.msg` | `dialogue_manager_node` | `task_orchestrator_node` |
| `/hri/remember` | Servicio `RememberGuest.srv` | `dialogue_manager_node` | `task_orchestrator_node` |
| `/hri/converse` | Acción `Converse.action` | `dialogue_manager_node` | `task_orchestrator_node` |
| `/hri/mode` | Tópico `std_msgs/String` ("reto" / "libre") | `task_orchestrator_node` | `dialogue_manager_node`, `llm_agent_node` |
| `/hri/world_context` | Tópico `WorldContext.msg` | `task_orchestrator_node` | `llm_agent_node` (modo "libre") |
| `/hri/llm_chat` | Acción `LlmChat.action` | `llm_agent_node` | `dialogue_manager_node` |
| `/hri/skill_request` | Servicio `RequestSkill.srv` | `task_orchestrator_node` | `llm_agent_node` (modo "libre") |

(*) Propuesta del equipo HRI, no está en el contrato original.

## Reglas del diálogo (modo "reto")

- Si el ASR no entiende nada en 8 s, se repite la pregunta una sola vez.
- Si el LLM no responde en 6 s, el `dialogue_manager_node` usa la lista de nombres y bebidas.
- Nunca se hacen preguntas de confirmación ("Did you say John?").
- El LLM nunca decide el flujo de la prueba: lo decide el árbol.
