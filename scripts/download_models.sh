#!/usr/bin/env bash
# Descarga los modelos en models/ (no se suben a GitHub).
# Uso: bash scripts/download_models.sh
set -e
cd "$(dirname "$0")/.."
mkdir -p models/vosk models/llm models/bert_t5

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

# ---------- BERT + T5 (modo "libre", mas adelante) ----------
# TODO: copiar los checkpoints en models/bert_t5/

echo "Listo."
