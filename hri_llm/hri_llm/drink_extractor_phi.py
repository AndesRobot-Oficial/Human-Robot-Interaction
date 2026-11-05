import ollama
import json
from pydantic import BaseModel


class DrinkResult(BaseModel):
    drink: str | None
    understood: bool


def extract_drink(sentence):

    prompt = f"""
You extract the drink that a person currently wants.

Rules:
- Extract only the final drink the person wants.
- Ignore rejected drinks.
- Ignore previous preferences or abandoned choices.
- Treat indirect requests such as
  "a glass/cup/bottle of X would be nice/great/perfect"
  as requests for drink X.
- Never invent a drink.
- If no specific desired drink is given, drink must be null.
- If drink is null, understood must be false.
- If a specific drink is found, understood must be true.

Sentence:
"{sentence}"
"""

    try:

        response = ollama.chat(
            model="phi4-mini",

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            format=DrinkResult.model_json_schema(),

            options={
                "temperature": 0
            }
        )

        content = response["message"]["content"]

        result = DrinkResult.model_validate_json(content)

        drink = result.drink

        if isinstance(drink, str):

            drink = drink.strip()

            if drink.lower() == "null" or drink == "":
                drink = None

        if drink is None:
            understood = False
        else:
            understood = True

        return {
            "drink": drink,
            "understood": understood
        }

    except Exception as error:

        print("Error:", error)

        return {
            "drink": None,
            "understood": False
        }


if __name__ == "__main__":

    sentence = input("Person: ")

    result = extract_drink(sentence)

    print("\nResult:")
    print(json.dumps(result, indent=2))