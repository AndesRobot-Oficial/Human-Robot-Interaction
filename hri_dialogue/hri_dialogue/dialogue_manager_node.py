"""dialogue_manager_node: maneja cada turno de dialogo que pide el orquestador.

Contrato (equipo HRI):
    Ofrece       /hri/converse        hri_interfaces/action/Converse      lo usa task_orchestrator_node
                 /hri/remember        hri_interfaces/srv/RememberGuest    lo usa task_orchestrator_node
    Publica      /hri/say             std_msgs/String                     lo usa tts_node (unico publicador)
                 /hri/dialogue_state  hri_interfaces/msg/DialogueState    lo usa task_orchestrator_node
    Se suscribe  /hri/speech_text     std_msgs/String                     de asr_node
                 /hri/speaking        std_msgs/Bool                       de tts_node (*propuesta)
                 /hri/mode            std_msgs/String                     de task_orchestrator_node
    Llama        /hri/llm_chat        hri_interfaces/action/LlmChat       ofrece llm_agent_node

Un turno (/hri/converse con una intencion):
    1. Dice la frase de config/phrases.yaml (/hri/say) y espera a que termine (/hri/speaking).
    2. Si la intencion espera respuesta, escucha /hri/speech_text hasta listen_timeout_s.
    3. Le pide el dato al LLM (/hri/llm_chat, history_json = {"field": "name"}).
    4. Si el LLM no esta, falla o tarda mas de llm_timeout_s, usa la lista (fallback.py).
    5. Si no hubo respuesta o no se entendio, repite la pregunta max_repeats veces.

Reglas (modo "reto"): nunca hace preguntas de confirmacion ("Did you say John?").

Funciona sin los demas nodos: sin tts_node no espera a que termine la voz y sin
llm_agent_node usa la lista. Asi se puede probar solo con texto.
"""
import json
import os
import queue
import threading
from typing import Optional

from ament_index_python.packages import get_package_share_directory
from hri_interfaces.action import Converse, LlmChat
from hri_interfaces.msg import DialogueState
from hri_interfaces.srv import RememberGuest
import rclpy
from rclpy.action import ActionClient, ActionServer
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from std_msgs.msg import Bool, String

from hri_dialogue.dialogue_logic import (LLM_KEYS, build_phrase, fallback_extract,
                                         load_yaml, parse_llm_reply)
from hri_dialogue.guest_memory import GuestMemory
from hri_dialogue.intents import INTENTS, is_valid


class DialogueManagerNode(Node):

    def __init__(self):
        super().__init__('dialogue_manager_node')

        # Parametros (config/dialogue_params.yaml)
        self.declare_parameter('listen_timeout_s', 8.0)
        self.declare_parameter('max_repeats', 1)
        self.declare_parameter('llm_timeout_s', 20.0)
        self.declare_parameter('speak_start_timeout_s', 1.5)
        self.declare_parameter('speak_max_s', 30.0)
        self.declare_parameter('phrases_file', '')
        self.declare_parameter('vocabulary_file', '')

        config_dir = os.path.join(get_package_share_directory('hri_dialogue'), 'config')
        self.phrases = load_yaml(
            self.get_parameter('phrases_file').value
            or os.path.join(config_dir, 'phrases.yaml'))
        self.vocabulary = load_yaml(
            self.get_parameter('vocabulary_file').value
            or os.path.join(config_dir, 'vocabulary.yaml'))

        self.mode = 'reto'
        self.memory = GuestMemory()
        self.turn_lock = threading.Lock()          # un turno a la vez
        self.speech_queue = queue.Queue()
        self.listening = False
        self.speaking_started = threading.Event()
        self.speaking_done = threading.Event()
        self.warned_no_tts = False

        cb = ReentrantCallbackGroup()               # los callbacks corren en paralelo

        # Publicadores
        self.say_pub = self.create_publisher(String, '/hri/say', 10)
        self.state_pub = self.create_publisher(DialogueState, '/hri/dialogue_state', 10)

        # Suscripciones
        self.create_subscription(String, '/hri/speech_text', self.on_speech_text, 10,
                                 callback_group=cb)
        self.create_subscription(Bool, '/hri/speaking', self.on_speaking, 10,
                                 callback_group=cb)
        self.create_subscription(String, '/hri/mode', self.on_mode, 10, callback_group=cb)

        # Servidores
        self.converse_server = ActionServer(
            self, Converse, '/hri/converse', self.execute_converse, callback_group=cb)
        self.remember_srv = self.create_service(
            RememberGuest, '/hri/remember', self.on_remember, callback_group=cb)

        # Cliente del LLM
        self.llm_client = ActionClient(self, LlmChat, '/hri/llm_chat', callback_group=cb)

        self.get_logger().info('dialogue_manager_node listo')

    # ---------- Suscripciones ----------
    def on_speech_text(self, msg: String):
        text = msg.data.strip()
        if self.listening and text:
            self.speech_queue.put(text)

    def on_speaking(self, msg: Bool):
        if msg.data:
            self.speaking_started.set()
        else:
            self.speaking_done.set()

    def on_mode(self, msg: String):
        self.mode = msg.data

    # ---------- /hri/remember ----------
    def on_remember(self, request, response):
        self.memory.remember(request.person_id, request.name,
                             request.drink, request.attribute)
        self.get_logger().info(
            f'Recordado {request.person_id}: {request.name}, {request.drink}, '
            f'{request.attribute}')
        response.success = True
        return response

    # ---------- Hablar, escuchar y preguntar al LLM ----------
    def say(self, text: str) -> None:
        """Publica la frase en /hri/say y espera a que tts_node termine de decirla."""
        if not text:
            return
        self.speaking_started.clear()
        self.speaking_done.clear()
        self.say_pub.publish(String(data=text))
        self.get_logger().info(f'ROBOT: "{text}"')
        if not self.speaking_started.wait(self.get_parameter('speak_start_timeout_s').value):
            if not self.warned_no_tts:
                self.get_logger().warn('tts_node no responde en /hri/speaking: no espero la voz')
                self.warned_no_tts = True
            return
        self.speaking_done.wait(self.get_parameter('speak_max_s').value)

    def listen(self, timeout_s: float) -> Optional[str]:
        """Primera frase que llegue por /hri/speech_text, o None si pasa timeout_s."""
        while not self.speech_queue.empty():         # descartar lo que llego antes
            self.speech_queue.get_nowait()
        self.listening = True
        try:
            return self.speech_queue.get(timeout=timeout_s)
        except queue.Empty:
            return None
        finally:
            self.listening = False

    def ask_llm(self, text: str, field: str, person_id: int) -> Optional[str]:
        """Pide el dato a llm_agent_node. None si no esta, falla o se pasa del tiempo."""
        if field not in LLM_KEYS:
            return None
        if not self.llm_client.server_is_ready():
            self.get_logger().warn('llm_agent_node no disponible')
            return None

        goal = LlmChat.Goal(user_text=text, person_id=person_id,
                            history_json=json.dumps({'field': field}))
        done = threading.Event()
        box = {}

        def on_result(future):
            box['result'] = future.result().result
            done.set()

        def on_goal(future):
            handle = future.result()
            box['handle'] = handle
            if not handle.accepted:
                done.set()
                return
            handle.get_result_async().add_done_callback(on_result)

        self.llm_client.send_goal_async(goal).add_done_callback(on_goal)
        timeout_s = self.get_parameter('llm_timeout_s').value
        if not done.wait(timeout_s):
            self.get_logger().warn(f'el LLM tardo mas de {timeout_s:.0f} s')
            if 'handle' in box:
                box['handle'].cancel_goal_async()
            return None
        result = box.get('result')
        if result is None:
            return None
        self.get_logger().info(f'LLM: {result.reply}')
        return parse_llm_reply(result.reply, field)

    # ---------- /hri/converse ----------
    def execute_converse(self, goal_handle):
        intent = goal_handle.request.intent
        person_id = goal_handle.request.person_id
        result = Converse.Result()

        if not is_valid(intent):
            self.get_logger().warn(f'Intencion desconocida: {intent}')
            goal_handle.abort()
            result.understood = False
            return result

        with self.turn_lock:
            self.get_logger().info(f'--- {intent} (persona {person_id}) ---')
            self.publish_state(intent, person_id)
            self.feedback(goal_handle, 'speaking')
            self.say(build_phrase(self.phrases, intent, self.memory, person_id))

            field = INTENTS[intent]['field']
            if not INTENTS[intent]['listens']:
                result.answer = ''
                result.understood = True
                goal_handle.succeed()
                return result

            answer = None
            for attempt in range(self.get_parameter('max_repeats').value + 1):
                if attempt > 0:
                    self.feedback(goal_handle, 'speaking')
                    self.say(build_phrase(self.phrases, 'repeat', self.memory, person_id))

                self.feedback(goal_handle, 'listening')
                text = self.listen(self.get_parameter('listen_timeout_s').value)
                if text is None:
                    self.get_logger().info('Sin respuesta')
                    continue
                self.get_logger().info(f'PERSONA: "{text}"')

                self.feedback(goal_handle, 'thinking')
                answer = self.ask_llm(text, field, person_id)
                source = 'LLM'
                if answer is None:
                    answer = fallback_extract(text, field, self.vocabulary)
                    source = 'lista'
                if answer is not None:
                    self.get_logger().info(f'{field} = {answer} (por {source})')
                    break
                self.get_logger().info(f'No se entendio el dato ({field})')

            result.answer = answer or ''
            result.understood = answer is not None
            goal_handle.succeed()
            return result

    def feedback(self, goal_handle, state: str) -> None:
        goal_handle.publish_feedback(Converse.Feedback(state=state))

    def publish_state(self, state: str, person_id: int):
        msg = DialogueState()
        msg.state = state
        msg.current_guest = str(person_id)
        self.state_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = DialogueManagerNode()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
