"""Motor del LLM en Python puro (sin ROS 2). Lo usa llm_agent_node.

Aqui va el codigo del LLM de Juliana y Sara: cargar el modelo local
(menos de 4B parametros, solo CPU) y consultarlo. Se puede probar solo,
sin ROS 2, ejecutando este archivo directamente.

Estado: PLANTILLA (sin funcionalidad).
"""


class LlmBackend:

    def __init__(self, model_path: str):
        self.model_path = model_path
        # TODO: cargar el modelo (por ejemplo con llama.cpp u Ollama)

    def generate(self, prompt: str, timeout_s: float) -> str:
        """Devuelve el texto generado por el LLM.

        Si no responde dentro de timeout_s, debe lanzar TimeoutError.
        """
        # TODO: consultar el modelo
        return ''


if __name__ == '__main__':
    # Prueba sin ROS 2: enviar un prompt y mostrar la respuesta
    print('llm_backend: plantilla, sin prueba todavia')
