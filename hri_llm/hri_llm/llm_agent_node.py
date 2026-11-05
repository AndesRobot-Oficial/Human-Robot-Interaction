"""
llm_agent_node: nodo principal del LLM para HRI.

Modo reto:
- Recibe texto proveniente del STT.
- Determina si se espera un nombre o una bebida.
- Usa Phi-4 Mini mediante los extractores desarrollados.
- Devuelve un JSON estructurado.

El nodo NO controla el flujo de la prueba.
Eso lo realiza el árbol de comportamiento / dialogue manager.
"""

import json
import multiprocessing as mp

from hri_interfaces.action import LlmChat

import rclpy
from rclpy.action import ActionServer
from rclpy.node import Node
from std_msgs.msg import String

from hri_llm.json_validator import validate_reto_reply
from hri_llm.name_extractor import extract_name
from hri_llm.drink_extractor_phi import extract_drink


MODEL = "phi4-mini:latest"


class LlmAgentNode(Node):

    def __init__(self):
        super().__init__("llm_agent_node")

        # Parametros
        self.declare_parameter("timeout_s", 20.0)
        self.declare_parameter("model_name", MODEL)

        self.mode = "reto"

        # Recibe el modo actual del sistema
        self.create_subscription(
            String,
            "/hri/mode",
            self.on_mode,
            10
        )

        # Action Server usado por dialogue_manager
        self.chat_server = ActionServer(
            self,
            LlmChat,
            "/hri/llm_chat",
            self.execute_chat
        )

        self.get_logger().info(
            "llm_agent_node listo - Phi-4 Mini"
        )


    def on_mode(self, msg: String):
        self.mode = msg.data


    def get_expected_data(self, history_json: str):
        """
        Determina si se espera un nombre o una bebida.

        Por ahora se deja flexible hasta conocer el formato
        definitivo de history_json enviado por dialogue_manager.
        """

        if not history_json:
            return None

        # Intentar leer como JSON
        try:
            history = json.loads(history_json)

            for key in [
                "expected_data",
                "expected_field",
                "field",
                "type"
            ]:
                value = history.get(key)

                if isinstance(value, str):
                    value = value.lower().strip()

                    if value in ["name", "nombre"]:
                        return "name"

                    if value in [
                        "drink",
                        "beverage",
                        "bebida"
                    ]:
                        return "drink"

        except Exception:
            pass

        # Respaldo temporal:
        # buscar directamente palabras dentro del texto
        text = history_json.lower()

        if "name" in text or "nombre" in text:
            return "name"

        if (
            "drink" in text
            or "beverage" in text
            or "bebida" in text
        ):
            return "drink"

        return None


    def execute_chat(self, goal_handle):

        request = goal_handle.request
        result = LlmChat.Result()

        # ==========================================
        # MODO RETO
        # ==========================================

        if self.mode == "reto":

            user_text = request.user_text

            expected_data = self.get_expected_data(
                request.history_json
            )

            self.get_logger().info(
                f"Texto recibido: {user_text}"
            )

            self.get_logger().info(
                f"Dato esperado: {expected_data}"
            )


            # ======================================
            # EXTRAER NOMBRE
            # ======================================

            if expected_data == "name":

                model_name = self.get_parameter(
                    "model_name"
                ).value

                extracted = extract_name(
                    user_text,
                    model=model_name
                )

                reply_data = {
                    "nombre": extracted.get("name"),
                    "bebida": None,
                    "entendido": extracted.get(
                        "understood",
                        False
                    )
                }


            # ======================================
            # EXTRAER BEBIDA
            # ======================================

            elif expected_data == "drink":

                extracted = extract_drink(
                    user_text
                )

                reply_data = {
                    "nombre": None,
                    "bebida": extracted.get("drink"),
                    "entendido": extracted.get(
                        "understood",
                        False
                    )
                }


            # ======================================
            # NO SE IDENTIFICO EL DATO ESPERADO
            # ======================================

            else:

                reply_data = {
                    "nombre": None,
                    "bebida": None,
                    "entendido": False
                }


            # Convertir resultado a JSON
            raw = json.dumps(reply_data)

            # Validacion final
            checked = validate_reto_reply(
                raw,
                user_text
            )

            result.reply = json.dumps(checked)


        # ==========================================
        # MODO LIBRE - FUTURO
        # ==========================================

        else:

            result.reply = json.dumps({
                "nombre": None,
                "bebida": None,
                "entendido": False
            })


        result.skill_calls_json = []

        goal_handle.succeed()

        return result


def main(args=None):

    mp.freeze_support()

    rclpy.init(args=args)

    node = LlmAgentNode()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
