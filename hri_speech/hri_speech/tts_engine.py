from espeak_ng import espeak_AUDIO_OUTPUT
import espeak_ng
import time

"""
Simple 'hello world' example.
"""

dicc_pronun = {"cocacola": "coh cah colah",
"MILO": "may loh",
"UNAB": "uhnab",
"chile": "shih leh",
"andes": "ahn des",
"robot": "roh boht"
}

def correct_pronun(text):
    for palabra, pronun in dicc_pronun.items():
        text = text.replace(palabra, pronun)
        return text


def main():
    text_to_synth = "is this MILO robot from chile that is made in the andes by UNAB, can you please give me a cocacola?"
    text_to_synth = correct_pronun(text_to_synth)
    espeak_ng.initialize(output=espeak_AUDIO_OUTPUT.AUDIO_OUTPUT_SYNCH_PLAYBACK)
    espeak_ng.set_voice_by_properties(name="mb-us2")
    espeak_ng.synth(text_to_synth)


if __name__ == "__main__":
    main()
