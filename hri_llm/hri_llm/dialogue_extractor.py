import multiprocessing as mp
import ollama
import time

from hri_llm.name_extractor import extract_name
from hri_llm.drink_extractor_phi import extract_drink


MODEL = "phi4-mini:3.8b"


def warm_up_model():
    """
    Carga Phi-4 Mini antes de iniciar la interacción
    para evitar una latencia alta en la primera consulta.
    """

    print("Loading Phi-4 Mini...")

    try:
        ollama.chat(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": "Reply only with OK."
                }
            ],
            options={
                "temperature": 0
            }
        )

        print("Phi-4 Mini ready.\n")

    except Exception as error:
        print("Warm-up error:", error)
        print("The system will continue.\n")


def process_answer(text, expected_data):
    """
    Procesa la respuesta según el dato esperado
    y devuelve una estructura común.

    expected_data:
        "name"
        "drink"
    """

    expected_data = expected_data.strip().lower()


    # =========================
    # NAME
    # =========================

    if expected_data == "name":

        result = extract_name(
            text,
            model=MODEL
        )

        return {
            "type": "name",
            "value": result.get("name"),
            "understood": result.get("understood", False),
            "source": result.get("source", "unknown"),
            "reason": result.get("reason", "unknown"),
            "elapsed_seconds": result.get("elapsed_seconds"),
            "in_list": result.get("in_list")
        }


    # =========================
    # DRINK
    # =========================

    elif expected_data == "drink":

        start_time = time.time()

        result = extract_drink(text)

        elapsed = time.time() - start_time

        return {
            "type": "drink",
            "value": result.get("drink"),
            "understood": result.get("understood", False),
            "source": "llm",
            "reason": (
                "ok"
                if result.get("understood", False)
                else "not_understood"
            ),
            "elapsed_seconds": round(elapsed, 3),
            "in_list": None
        }


    # =========================
    # UNKNOWN TYPE
    # =========================

    else:

        return {
            "type": expected_data,
            "value": None,
            "understood": False,
            "source": "system",
            "reason": "unknown_expected_data",
            "elapsed_seconds": 0,
            "in_list": None
        }


def main():

    warm_up_model()

    print("Dialogue extractor test")
    print("-----------------------")

    expected_data = input(
        "What data are we expecting? (name/drink): "
    )

    text = input("Person: ")

    result = process_answer(
        text,
        expected_data
    )

    print("\nResult:")
    print(result)


if __name__ == "__main__":
    mp.freeze_support()
    main()