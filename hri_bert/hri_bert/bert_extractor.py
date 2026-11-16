import os
import sys

import torch
from transformers import BertForTokenClassification, BertTokenizerFast

BERT_PATH = os.path.join(os.environ.get("HRI_MODELS_DIR", "models"), "bert")
ESPECIALES = ("[CLS]", "[SEP]", "[PAD]")

bert_tokenizer = None
bert_model = None
id2label = None


def cargar(path=BERT_PATH):
    global bert_tokenizer, bert_model, id2label
    if bert_model is None:
        bert_tokenizer = BertTokenizerFast.from_pretrained(path)
        bert_model = BertForTokenClassification.from_pretrained(path)
        bert_model.eval()
        id2label = bert_model.config.id2label


def run_inference(command):
    cargar()
    words = command.strip().split()
    if not words:
        return [], []

    inputs = bert_tokenizer(words, is_split_into_words=True, return_tensors="pt")
    with torch.no_grad():
        outputs = bert_model(**inputs)

    preds = outputs.logits.argmax(dim=-1).squeeze().tolist()
    tokens = bert_tokenizer.convert_ids_to_tokens(inputs["input_ids"].squeeze())

    labels = [id2label.get(p, "O") for p in preds]
    return tokens, labels


def combine_subwords(tokens, labels):
    new_tokens = []
    new_labels = []
    skip = False

    for i in range(len(tokens)):
        if skip:
            skip = False
            continue

        token = tokens[i]
        label = labels[i]

        if token.startswith("##") and new_tokens:
            new_tokens[-1] = new_tokens[-1] + token[2:]
        elif i + 1 < len(tokens) and tokens[i + 1].startswith("##"):
            new_tokens.append(token + tokens[i + 1][2:])
            new_labels.append(label)
            skip = True
        else:
            new_tokens.append(token)
            new_labels.append(label)

    return new_tokens, new_labels


def extract_slots(tokens, labels):
    slots = []
    current = {}
    prev = "O"

    for tok, lab in zip(tokens, labels):
        if lab.startswith("B-VERB"):
            if current:
                slots.append(current)
            current = {"intent": tok}
        elif lab.startswith("B-OBJ"):
            if prev.startswith("B-OBJ") and "object" in current:
                current["object"] += " " + tok
            else:
                current["object"] = tok
        elif lab.startswith("B-LOC"):
            current["location"] = tok
        elif lab.startswith("I-LOC") and "location" in current:
            current["location"] += " " + tok
        elif lab.startswith("B-ATTR"):
            current["attribute"] = tok
        elif lab.startswith("B-FILTER"):
            current["filter"] = tok
        elif lab.startswith("B-PERSON"):
            current["person"] = tok
        elif lab.startswith("B-CONTENT"):
            current["content"] = tok
        prev = lab

    if current:
        slots.append(current)
    return slots


def clean_slots(slots):
    for s in slots:
        attr = s.get("attribute", "")
        if attr.startswith("##"):
            s["attribute"] = attr.replace("##", "")
        if "filter" in s and "intent" not in s:
            s["intent"] = "locate"
    return slots


def interpretar(command):
    tokens, labels = run_inference(command)
    pares = [(t, l) for t, l in zip(tokens, labels) if t not in ESPECIALES]
    tokens, labels = combine_subwords([t for t, _ in pares], [l for _, l in pares])
    slots = clean_slots(extract_slots(tokens, labels))
    objeto = next((s["object"] for s in slots if "object" in s), None)
    lugar = next((s["location"] for s in slots if "location" in s), None)
    return {"objeto": objeto, "lugar": lugar, "slots": slots, "entendido": objeto is not None}


if __name__ == "__main__":
    for frase in sys.argv[1:] or ["bring me the fork from the kitchen"]:
        print(frase, "->", interpretar(frase))
