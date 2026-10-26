"""llm_agent_node: consulta el LLM (usa LlmBackend).

Contrato (equipo HRI):
    Ofrece       /hri/llm_chat        hri_interfaces/action/LlmChat       lo usa dialogue_manager_node
    Se suscribe  /hri/mode            std_msgs/String                     de task_orchestrator_node
                 /hri/world_context   hri_interfaces/msg/WorldContext     (modo "libre", despues)
    Llama        /hri/skill_request   hri_interfaces/srv/RequestSkill     (modo "libre", despues)

Modo "reto": solo extrae el nombre o la bebida. reply es un JSON en texto
(ver json_validator.py). Nunca pide habilidades.

Estado: PLANTILLA (sin funcionalidad).
"""
import json
import os

from ament_index_python.packages import get_package_share_directory
from hri_interfaces.action import LlmChat
import rclpy
from rclpy.action import ActionServer
from rclpy.node import Node
from std_msgs.msg import String

from hri_llm.json_validator import validate_reto_reply
from hri_llm.llm_backend import LlmBackend


class LlmAgentNode(Node):

    def __init__(self):
        super().__init__('llm_agent_node')

        # Parametros (config/llm_params.yaml)
        self.declare_parameter('model_path', 'models/llm/')
        self.declare_parameter('timeout_s', 6.0)
        self.declare_parameter(
            'reto_prompt_file',
            os.path.join(get_package_share_directory('hri_llm'), 'prompts',
                         'reto_extract.txt'))

        self.mode = 'reto'
        self.backend = LlmBackend(self.get_parameter('model_path').value)

        self.create_subscription(String, '/hri/mode', self.on_mode, 10)
        # TODO (modo "libre"): suscripcion a /hri/world_context y cliente de /hri/skill_request

        self.chat_server = ActionServer(self, LlmChat, '/hri/llm_chat', self.execute_chat)

        self.get_logger().info('llm_agent_node listo (plantilla)')

    def on_mode(self, msg: String):
        self.mode = msg.data

    def execute_chat(self, goal_handle):
        request = goal_handle.request
        result = LlmChat.Result()

        if self.mode == 'reto':
            # TODO:
            #   1. armar el prompt con reto_prompt_file, request.user_text y
            #      request.history_json (que se pregunto: nombre o bebida)
            #   2. raw = self.backend.generate(prompt, timeout_s)
            raw = self.backend.generate('', self.get_parameter('timeout_s').value)
            checked = validate_reto_reply(raw, request.user_text)
            result.reply = json.dumps(checked)
        else:
            # TODO (modo "libre"): conversacion y habilidades
            result.reply = ''

        result.skill_calls_json = []
        goal_handle.succeed()
        return result


def main(args=None):
    rclpy.init(args=args)
    node = LlmAgentNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
