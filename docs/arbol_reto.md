# Árbol de comportamiento de la prueba 5.1

Hecho con `py_trees` y `py_trees_ros`. Código en `hri_orchestrator/hri_orchestrator/tree/`.

## Notación (la misma que imprime `py_trees` en la terminal)

| Símbolo | Significado |
|---|---|
| `[-]` / `{-}` | Sequence (sin memoria / con memoria) |
| `[o]` / `{o}` | Selector (sin memoria / con memoria) |
| `/_/` | Parallel |
| `-^-` | Decorador (OneShot, Timeout, Retry) |
| `-->` | Comportamiento |
| `(stub)` | Simula un nodo de otro equipo |

## Raíz

```
/_/ Root
    /_/ Topics2BB          copia los tópicos al blackboard en cada tick
    [o] Priorities         (abajo)
```

## Árbol completo (sin Topics2BB)

```
[o] Priorities
    [-] Emergency
        --> IsEmergency?
        --> SetLed alert (stub)
        --> Hold
    -^- RunOnce
        {-} Receptionist
            {-} Setup
                --> LoadPlaces
                --> PublishMode "reto"
                --> SetLed idle (stub)
                --> WaitForStart
                --> SetInitialPose start (stub)
            {o} Guest1
                --> IsGuest1Done?
                {-} ReceiveGuest1
                    {-} WaitAtStart
                        [o] GoToStart
                            --> IsAtStart?
                            {-} NavigateToStart
                                --> LookAhead on (stub)
                                --> NavigateToPose start (stub)
                                --> LookAhead off (stub)
                        {o} Doorbell (opcional)
                            -^- TimeoutDoorbell
                                --> WaitDoorbell
                            --> SinTimbre
                    {-} GoToDoor
                        --> LookAhead on (stub)
                        --> NavigateToPose entrance_door (stub)
                        --> LookAhead off (stub)
                    {o} OpenDoorIfClosed
                        --> DoorIsOpen? (stub)
                        {-} OpenDoor
                            --> DetectHandle (stub)
                            --> OpenDoor pull (stub)
                    -^- RetryFindGuest
                        --> FindGuest1AtDoor
                    /_/ TalkToGuest
                        --> LookAt guest1_id (stub)
                        {-} Dialogue
                            --> Converse "greet"
                            --> Converse "ask_name"
                            --> Converse "ask_drink"
                            --> DescribePerson guest1_id (stub)
                    --> RememberGuest1
                    {-} GuideToLivingRoom
                        --> Converse "ask_follow"
                        {-} NavigateToLivingRoom
                            --> LookAhead on (stub)
                            --> NavigateToPose living_room (stub)
                            --> LookAhead off (stub)
                    {-} OfferSeat
                        --> DetectFreeSeat (stub)
                        --> PointTo guest1_seat (stub)
                        /_/ OfferSeatLooking
                            --> LookAt guest1_id (stub)
                            --> Converse "offer_seat"
                    --> MarkGuest1Done
            {o} Guest2
                --> IsGuest2Done?
                {-} ReceiveGuest2
                    {-} WaitAtStart
                        [o] GoToStart
                            --> IsAtStart?
                            {-} NavigateToStart
                                --> LookAhead on (stub)
                                --> NavigateToPose start (stub)
                                --> LookAhead off (stub)
                        {o} Doorbell (opcional)
                            -^- TimeoutDoorbell
                                --> WaitDoorbell
                            --> SinTimbre
                    {-} GoToDoor
                        --> LookAhead on (stub)
                        --> NavigateToPose entrance_door (stub)
                        --> LookAhead off (stub)
                    {o} OpenDoorIfClosed
                        --> DoorIsOpen? (stub)
                        {-} OpenDoor
                            --> DetectHandle (stub)
                            --> OpenDoor pull (stub)
                    -^- RetryFindGuest
                        --> FindGuest2AtDoor
                    /_/ TalkToGuest
                        --> LookAt guest2_id (stub)
                        {-} Dialogue
                            --> Converse "greet"
                            --> Converse "ask_name"
                            --> Converse "ask_drink"
                            --> Converse "describe_guest"
                    --> RememberGuest2
                    {-} ReceiveBag
                        --> Converse "ask_bag"
                        --> SetLed ready_handover (stub)
                        --> MoveArmToPose ready_handover (stub)
                        --> PickObject handover (stub)
                        --> IsHoldingObject?
                        --> MoveArmToPose carry (stub)
                        --> SetLed idle (stub)
                    {-} GuideToLivingRoom
                        --> Converse "ask_follow"
                        {-} NavigateToLivingRoom
                            --> LookAhead on (stub)
                            --> NavigateToPose living_room (stub)
                            --> LookAhead off (stub)
                    {-} OfferSeat
                        --> DetectFreeSeat (stub)
                        --> PointTo guest2_seat (stub)
                        /_/ OfferSeatLooking
                            --> LookAt guest2_id (stub)
                            --> Converse "offer_seat"
                    --> MarkGuest2Done
            {-} Introduce
                --> LocateGuests
                /_/ IntroduceToGuest1
                    --> LookAt guest1_id (stub)
                    --> Converse "introduce"
                /_/ IntroduceToGuest2
                    --> LookAt guest2_id (stub)
                    --> Converse "introduce"
            {-} BagToHost
                --> FindHost
                /_/ AskHostLooking
                    --> LookAt host_id (stub)
                    --> Converse "ask_host"
                --> WaitHostInFront
                /_/ FollowHost
                    --> FollowPerson host_id (stub)
                    --> Converse "wait_drop"
                --> PlaceObject floor (stub)
                --> MoveArmToPose home (stub)
            --> SetLed idle (stub)
    --> Idle

```

## Archivos

| Archivo | Contenido |
|---|---|
| `tree/root.py` | Root, Priorities y OneShot |
| `tree/topics2bb.py` | Suscriptores al blackboard |
| `tree/emergency.py` | Paro de emergencia |
| `tree/receptionist.py` | Setup y orden de los subárboles |
| `tree/receive_guest.py` | ReceiveGuest(n) |
| `tree/introduce.py` | Introduce |
| `tree/bag_to_host.py` | BagToHost |
| `blackboard_keys.py` | Nombres de las variables del blackboard |
