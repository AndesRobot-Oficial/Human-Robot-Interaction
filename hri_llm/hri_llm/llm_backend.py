"""Motor del LLM en Python puro (sin ROS 2). Lo usa llm_agent_node.

Aqui va el codigo del LLM de Juliana y Sara: cargar el modelo local
(menos de 4B parametros, solo CPU) y consultarlo. Se puede probar solo,
sin ROS 2, ejecutando este archivo directamente.

Estado: PLANTILLA (sin funcionalidad).
"""
from hri_llm.dialogue_extractor import process_answer

class LlmBackend:

    def __init__(self, model_path: str):
        self.model_path = model_path
        # TODO: cargar el modelo (por ejemplo con llama.cpp u Ollama)
	

    def extract_reto(self, user_text: str, field: str) -> dict:
        """Extrae el dato solicitado y lo adapta al formato del reto."""
        result = process_answer(user_text, field)
        value = result["value"] if result["understood"] else None

        return {
        "nombre": value if field == "name" else None,
        "bebida": value if field == "drink" else None,
        "entendido": value is not None,
        }

    def generate(self, prompt: str, timeout_s: float) -> str:
        """Devuelve el texto generado por el LLM.

        Si no responde dentro de timeout_s, debe lanzar TimeoutError.
        """
        # TODO: consultar el modelo
        return ''


if __name__ == '__main__':
    # Prueba sin ROS 2: enviar un prompt y mostrar la respuesta
    print('llm_backend: plantilla, sin prueba todavia')
