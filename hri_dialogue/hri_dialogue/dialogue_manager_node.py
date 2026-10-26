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

Reglas (modo "reto"):
    - Si no hay respuesta en listen_timeout_s (8 s), repite la pregunta una sola vez.
    - Si el LLM no responde en llm_timeout_s (6 s), usa fallback.py.
    - Nunca hace preguntas de confirmacion ("Did you say John?").

Estado: PLANTILLA. Responde valores fijos para poder probar el arbol.
"""
from hri_interfaces.action import Converse, LlmChat
from hri_interfaces.msg import DialogueState
from hri_interfaces.srv import RememberGuest
import rclpy
from rclpy.action import ActionClient, ActionServer
from rclpy.node import Node
from std_msgs.msg import Bool, String

from hri_dialogue.guest_memory import GuestMemory
from hri_dialogue.intents import INTENTS, is_valid

# Respuestas fijas de la plantilla (se quitan al implementar el nodo)
PLACEHOLDER_ANSWERS = {'name': 'John', 'drink': 'coffee', 'drop': 'drop it here'}


class DialogueManagerNode(Node):

    def __init__(self):
        super().__init__('dialogue_manager_node')

        # Parametros (config/dialogue_params.yaml)
        self.declare_parameter('listen_timeout_s', 8.0)
        self.declare_parameter('max_repeats', 1)
        self.declare_parameter('llm_timeout_s', 6.0)
        self.declare_parameter('phrases_file', '')
        self.declare_parameter('vocabulary_file', '')

        self.mode = 'reto'
        self.robot_speaking = False
        self.memory = GuestMemory()

        # Publicadores
        self.say_pub = self.create_publisher(String, '/hri/say', 10)
        self.state_pub = self.create_publisher(DialogueState, '/hri/dialogue_state', 10)

        # Suscripciones
        self.create_subscription(String, '/hri/speech_text', self.on_speech_text, 10)
        self.create_subscription(Bool, '/hri/speaking', self.on_speaking, 10)
        self.create_subscription(String, '/hri/mode', self.on_mode, 10)

        # Servidores
        self.converse_server = ActionServer(
            self, Converse, '/hri/converse', self.execute_converse)
        self.remember_srv = self.create_service(
            RememberGuest, '/hri/remember', self.on_remember)

        # Cliente del LLM
        self.llm_client = ActionClient(self, LlmChat, '/hri/llm_chat')

        self.get_logger().info('dialogue_manager_node listo (plantilla)')

    # ---------- Suscripciones ----------
    def on_speech_text(self, msg: String):
        # TODO: guardar el texto si se esta esperando una respuesta
        pass

    def on_speaking(self, msg: Bool):
        self.robot_speaking = msg.data

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

        self.publish_state(intent, person_id)

        # TODO (implementacion real):
        #   1. armar la frase con config/phrases.yaml y la memoria de invitados
        #   2. publicarla en /hri/say y esperar /hri/speaking = false
        #   3. si la intencion espera respuesta: escuchar /hri/speech_text
        #      hasta listen_timeout_s; repetir max_repeats veces
        #   4. pedir al LLM (/hri/llm_chat) que extraiga el dato; si falla, fallback.py
        self.get_logger().info(f'[plantilla] converse: {intent} (persona {person_id})')

        field = INTENTS[intent]['field']
        result.answer = PLACEHOLDER_ANSWERS.get(field, '') if field else ''
        result.understood = True
        goal_handle.succeed()
        return result

    def publish_state(self, state: str, person_id: int):
        msg = DialogueState()
        msg.state = state
        msg.current_guest = str(person_id)
        self.state_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = DialogueManagerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
