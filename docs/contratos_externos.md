# Interfaces de otros equipos

Según la ficha de `task_orchestrator_node` del documento de la líder. HRI es **cliente**:
los tipos y campos los define cada equipo. Mientras no estén listos, el árbol usa
*stubs* (`hri_orchestrator/behaviours/external/`) con los mismos puertos.

## Estructura y Electrónica (`/base/`)

| Interfaz | Tipo | Campos | Stub |
|---|---|---|---|
| `/base/start_button` | Tópico `std_msgs/Bool` | true al presionar el botón | Real (Topics2BB) |
| `/base/start_sound` | Tópico `std_msgs/Bool` | true al recibir la señal de inicio | Real (Topics2BB) |
| `/base/emergency_stop` | Tópico `std_msgs/Bool` | true = robot detenido | Real (Topics2BB) |
| `/base/set_led_state` | Servicio `SetLedState.srv` | pattern (idle, listening, ready_handover, alert) → success | `SetLed` |

## Navegación (`/nav/`)

| Interfaz | Tipo | Campos | Stub |
|---|---|---|---|
| `/nav/pose` | Tópico `geometry_msgs/PoseStamped` | frame map | Real (Topics2BB) |
| `/nav/safety_state` | Tópico `std_msgs/String` | "PARADO: sin lidar", "frenando"… | Real (Topics2BB) |
| `/nav/set_initial_pose` | Servicio `SetInitialPose.srv` | PoseWithCovarianceStamped → success, message | `SetInitialPose` |
| `/nav/navigate_to_pose` | Acción `NavigateToPose.action` (Nav2) | PoseStamped → distance_remaining → success | `NavigateToPose` |
| `/nav/follow_person` | Acción `FollowPerson.action` | person_id → distance_to_person → success | `FollowPerson` |
| `/nav/look` | Acción `LookAt.action` | person_id (-1 = target), target, continuous → on_target → success | `LookAt` |
| `/nav/look_ahead` | Servicio `std_srvs/SetBool` | true = mirar hacia donde navega | `LookAhead` |
| `/nav/detect_door` | Servicio `DetectDoor.srv` | → is_open, door_pose, hinge_side | `DoorIsOpen` |

## Visión Computacional (`/vision/`)

| Interfaz | Tipo | Campos | Stub |
|---|---|---|---|
| `/vision/persons` | Tópico `PersonArray.msg` | persons[]: id, pose, posture, confidence | `StubTopic` |
| `/vision/faces` | Tópico `FaceArray.msg` | faces[]: person_id, name, confidence | `StubTopic` |
| `/vision/identify_person` | Servicio `IdentifyPerson.srv` | person_id → name, confidence | (no usado aún) |
| `/vision/describe_person` | Servicio `DescribePerson.srv` | person_id → attribute | `DescribePerson` |
| `/vision/detect_free_seat` | Servicio `DetectFreeSeat.srv` | → seat_pose, found | `DetectFreeSeat` |
| `/vision/detect_handle` | Servicio `DetectHandle.srv` | door_pose → found, handle_pose, handle_type | `DetectHandle` |
| `/vision/detect_bag` | Servicio `DetectBag.srv` | → bag_pose, found | (no usado aún) |

## Brazo y Garra (`/arm/`)

| Interfaz | Tipo | Campos | Stub |
|---|---|---|---|
| `/arm/gripper_state` | Tópico `GripperState.msg` | state (open, closed, holding_object), object_detected | `StubTopic` |
| `/arm/pick_object` | Acción `PickObject.action` | target_pose, mode (grasp \| handover) → success | `PickObject` |
| `/arm/move_to_pose` | Acción `MoveArmToPose.action` | pose_name o look_target → success | `MoveArmToPose` |
| `/arm/point_to` | Acción `PointTo.action` | PointStamped target → success | `PointTo` |
| `/arm/open_door` | Acción `OpenDoor.action` | handle_pose, direction (pull \| push) → success | `OpenDoor` |
| `/arm/gesture` | Acción `Gesture.action` | gesture (wave, point, nod), target → success | (no usado aún) |
| `/arm/place_object` | Acción `PlaceObject.action` | **No confirmado en la ficha** | `PlaceObject` |
