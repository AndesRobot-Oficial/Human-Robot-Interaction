# Arquitectura de HRI

## Nodos y tópicos internos

Todos con `std_msgs`. Los datos van en JSON dentro de un `String`.

| Nodo | Escucha | Publica |
|---|---|---|
| `timbre_node` | `/hri/timbre/activar` (Bool) | `/hri/doorbell_detected` (Bool) |
| `stt_node` | `/hri/escuchar` (String: `libre` u `orden`), `/hri/hablando` (Bool) | `/hri/speech_text` (String) |
| `tts_node` | `/hri/say` (String) | `/hri/hablando` (Bool) |
| `llm_node` | `/hri/llm/entrada` (String) | `/hri/llm/salida` (JSON `{nombre, bebida, entendido}`) |
| `bert_node` | `/hri/bert/entrada` (String) | `/hri/bert/salida` (JSON `{objeto, lugar, entendido}`) |
| `task_orchestrator_node` | `/orquestador/iniciar` (Bool) y los de arriba | `/orquestador/estado` (String) y los de arriba |

- El micrófono lo abre el `timbre_node` solo mientras espera el timbre, y el `stt_node` solo mientras escucha una frase.
- El `stt_node` no escucha mientras el robot habla (`/hri/hablando`).

## Con los otros equipos: conectores

El orquestador no usa tópicos directamente: llama funciones de `hri_orchestrator/conectores.py`
(`nav.ir_a`, `vision.buscar_objeto`, `garra.agarrar`, ...). Cada conector lee `config/topicos.yaml`:

```yaml
navegacion:
  ir_a:
    tipo: accion          # accion o topico
    nombre: /nav/navigate_to_pose
    mensaje: nav2_msgs/action/NavigateToPose
```

- Si cambia el **nombre**, se cambia en el yaml.
- Si cambia la **forma** (por ejemplo, de tópico a servicio), se cambia solo la clase de ese equipo en `conectores.py`.
- Un `nombre` vacío desactiva esa parte.

| Equipo | Lo que HRI envía | Lo que HRI espera |
|---|---|---|
| Navegación | Acción `/nav/navigate_to_pose` con la pose del waypoint (de `casa_lugares.yaml`) | El resultado de la acción (llegó o no) |
| Visión | `/vision/registrar_persona` (ID), `/vision/buscar_objeto` (clase) | `/vision/persona_registrada` (ID), `/detected_object` (clase), `/object_position` (Point), `/vision/persona_al_frente` (ID), `/vision/personas_sofa` (JSON `{ID: lado}`) |
| Garra | `/garra/agarrar` (clase), `/garra/entregar` (Bool), `/garra/proceder` (Bool, bolsa) | `/garra/tiene_objeto` (Bool), `/garra/entregado` (Bool) |
| Todos | `/orquestador/estado` (String: en qué paso va, "orden terminada ...") | — |

**Nombre y cara:** el orquestador da el ID (`invitado_1`, `invitado_2`). Visión guarda la cara con ese ID y HRI guarda
el nombre y la bebida con el mismo ID.

## Flujo (`task_orchestrator_node.secuencia`)

Para cada invitado (`invitado_1`, luego `invitado_2`):

1. Esperar el timbre (`timbre_node`).
2. Ir a la puerta (`puerta → indoor`).
3. Registrar: Visión registra la cara con el ID mientras HRI saluda, pregunta, escucha (modo libre) y el LLM saca nombre y bebida. Si falta algo, pregunta de nuevo (hasta 3 veces).
4. "Please follow me to the sofa" → ir al sofá.
5. Pedir la orden (modo orden) → BERT da objeto y lugar → `nombres.yaml` los traduce a clase de Visión y waypoint.
6. Ir al lugar → Visión detecta el objeto → Garra lo agarra.
7. Volver a la sala → Visión confirma la persona al frente → "here is your ..." → Garra entrega (3 s) → `orden terminada`.

Al final: presentar a los dos invitados (nombre y bebida del otro), recibir la bolsa (Visión la detecta, aviso de seguridad, `garra/proceder`) y `reto terminado`.
Si un equipo no responde a tiempo, el orquestador lo avisa en el log y sigue.

## Lo que se agregó a cada avance

| Avance | Autores | Qué se agregó |
|---|---|---|
| STT (`stt_engine.py`) | Allisson y Felipe | Modo `libre` (sin gramática) para nombre y bebida, además del modo `orden` con su lista. `escuchar(modo)` devuelve `{texto, confianza, lugar, objeto}` y junta la frase hasta 1.5 s de silencio. Descarta pedazos con confianza menor a su `UMBRAL`. Busca el modelo en `models/vosk/`. `rubik's cube` → `rubik cube` (Vosk no conoce `rubik's`). Lo que corría al abrir el archivo quedó en `main()` |
| TTS (`tts_engine.py`) | Allisson, Felipe y watitaa | `correct_pronun` corrige por palabra completa y sin importar mayúsculas (antes no corregía "Pepsi" y cambiaba "fantastic"); se agregó "coca-cola" al diccionario. Nueva `hablar(texto, voz)` (voz `mb-us1` Martha, `en-us` Milo), que usa `tts_node`. Dependencias: `espeak-ng-python` y `libespeak-ng-dev` |
| LLM (`name_extractor.py`, `drink_extractor_phi.py`) | Sara y Juliana | Un solo modelo `phi4-mini:3.8b` y `OLLAMA_HOST` (los cambios del PR #2 de Juliana). En bebidas: tiempo límite de 20 s, descartar bebidas que la persona no dijo y la regla "I like X". El calentamiento del modelo (idea del PR #2) está en `llm_node` |
| BERT (`bert_extractor.py`) | Juan Rivera | `run_inference`, `combine_subwords`, `extract_slots` y `clean_slots` salen de su notebook `Ruta.ipynb`. Se agregó `interpretar()`, que quita `[CLS]`/`[SEP]`, y `extract_slots` junta dos palabras de objeto seguidas ("orange juice"). El modelo es su `checkpoint-339`. T5 no se usa |
| Timbre (`timbre_engine.py`) | Nuevo | Detecta un tono estable (misma frecuencia ≥ 0.3 s, ≥ 10 dB sobre el ruido). `calibrar` muestra lo que mide para ajustar `voz.yaml` |

## Lo que se quitó (sigue en el historial de git)

`hri_dialogue` (gestor de diálogo), `hri_audio`, `hri_doorbell`, `hri_interfaces`, el árbol de `hri_orchestrator` (`py_trees`),
`llm_agent_node` y `llm_backend`, y los launch viejos de `hri_bringup`.

## Pendientes

- STT: el modelo pequeño de Vosk confunde nombres ("John" → "joan"). Opciones: modelo más grande o lista de nombres del reto.
- Visión y Garra: confirmar nombres y tipos de sus tópicos y actualizar `topicos.yaml`.
- Navegación: confirmar el waypoint de la puerta.
