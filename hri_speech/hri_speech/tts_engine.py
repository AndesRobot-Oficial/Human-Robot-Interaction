from espeak_ng import espeak_AUDIO_OUTPUT
import espeak_ng
#import time

"""
Simple 'hello world' example.
"""

dicc_pronun = {"cocacola": "coh cah colah",
"MILO": "may loh",
"UNAB": "uhnab",
"chile": "shih leh",
"andes": "ahn des",
"robot": "roh boht",
"MARTA": "marh tah",
"pepsi": "pet ci",
"fanta": "fan tah"
}

def correct_pronun(text):
    for palabra, pronun in dicc_pronun.items():
        text = text.replace(palabra, pronun)
    return text


def main():
    text_to_synth = "fanta"
    print("texto en lenguaje original: ", text_to_synth)
    text_to_synth = correct_pronun(text_to_synth)
    print("texto con cambio de pronunciacion: ", text_to_synth)

    espeak_ng.initialize(output=espeak_AUDIO_OUTPUT.AUDIO_OUTPUT_SYNCH_PLAYBACK)
    espeak_ng.set_voice_by_properties(name="2")
    espeak_ng.synth(text_to_synth)


if __name__ == "__main__":
    main()
