# models/

Aqui van los modelos. **No se suben a GitHub** (pesan cientos de MB).
Para descargarlos: `bash scripts/download_models.sh`

| Carpeta | Contenido | Lo usa |
|---|---|---|
| `vosk/` | Modelo de STT (`vosk-model-small-en-us-0.15`) | `stt_engine.py` / `stt_node` |
| `bert/` | BERT de ordenes (`checkpoint-339` del repo de Juan Rivera) | `bert_extractor.py` / `bert_node` |
| `llm/` | Sin uso: el LLM (Phi-4 Mini) corre en Ollama, en el computador | — |
