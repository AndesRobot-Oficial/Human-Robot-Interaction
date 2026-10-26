# Decisiones y propuestas

## Decisiones del equipo HRI

| Decisión | Detalle |
|---|---|
| Todo en Python | El árbol usa `py_trees` y `py_trees_ros` (no BehaviorTree.CPP) |
| Repositorio nuevo | Independiente del prototipo de profe Pablo (solo se tomaron ideas) |
| Modo "reto" primero | El modo "libre" (conversación y habilidades) queda para después |
| LLM también en modo "reto" | Solo extrae nombre y bebida; `reply` es un JSON en texto |
| LLM primero, BERT + T5 de respaldo | Solo en modo "libre", más adelante |
| Motores en Python puro | STT, TTS y LLM se pueden probar sin ROS 2 |
| Modelos fuera de Git | Se descargan con `scripts/download_models.sh` |

## Propuestas para informar a la líder

| Propuesta | Por qué |
|---|---|
| `/hri/speaking` (`std_msgs/Bool`, publica `tts_node`) | Saber cuándo terminó de hablar el robot: empezar a contar los 8 s y que el ASR no se escuche a sí mismo |
| Intención `wait_drop` en `/hri/converse` | Escuchar "drop it here" mientras sigue al anfitrión |
| Usar el LLM en modo "reto" | El contrato dice que en "reto" no se usa |
| Usar solo `/hri/doorbell_detected` | `/base/doorbell_detected` está duplicado (regla de un solo responsable) |
| Usar solo `/hri/play_sound` | `/base/play_sound` está marcado como movido |
| Confirmar `/arm/place_object` | No aparece en la ficha y se necesita para dejar la bolsa |

## Preguntas para otros equipos

| Equipo | Pregunta |
|---|---|
| Visión | ¿Cómo sabe `/vision/identify_person` el nombre de cada invitado? ¿El `person_id` se mantiene si la persona se mueve o cambia de asiento? |
| Visión | `detect_free_seat` entrega la posición del asiento: ¿el robot debe calcular un punto frente a él? |
| Navegación y Brazo | Las poses de Visión vienen en el marco de la cámara: ¿sus nodos las transforman con TF2? |
