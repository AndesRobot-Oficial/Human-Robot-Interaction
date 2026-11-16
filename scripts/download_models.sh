#!/usr/bin/env bash
# Descarga los modelos en models/ (no se suben a GitHub).
# Uso: bash scripts/download_models.sh
set -e
cd "$(dirname "$0")/.."
mkdir -p models/vosk models/llm models/bert

# ---------- STT: Vosk (ingles, modelo pequeno) ----------
VOSK=vosk-model-small-en-us-0.15
if [ ! -d "models/vosk/$VOSK" ]; then
    echo "Descargando $VOSK..."
    wget -q --show-progress -O /tmp/$VOSK.zip "https://alphacephei.com/vosk/models/$VOSK.zip"
    unzip -q /tmp/$VOSK.zip -d models/vosk/
    rm /tmp/$VOSK.zip
else
    echo "Vosk ya esta descargado."
fi

# ---------- LLM (Juliana y Sara) ----------
# TODO: descargar el modelo elegido en models/llm/

# ---------- BERT (ordenes: objeto y lugar) ----------
BERT_URL=https://media.githubusercontent.com/media/JuanRivera182003/LLM-/main/bert_token_classification_model/checkpoint-339
for f in config.json model.safetensors tokenizer.json tokenizer_config.json special_tokens_map.json vocab.txt; do
    if [ ! -s "models/bert/$f" ]; then
        echo "Descargando BERT: $f"
        wget -q --show-progress -O "models/bert/$f" "$BERT_URL/$f"
    fi
done
echo "BERT listo en models/bert"

echo "Listo."
