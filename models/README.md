# models/

Aqui van los modelos. **No se suben a GitHub** (pesan cientos de MB).
Para descargarlos: `bash scripts/download_models.sh`

| Carpeta | Contenido | Lo usa |
|---|---|---|
| `vosk/` | Modelo de STT (`vosk-model-small-en-us-0.15`) | `asr_node` |
| `llm/` | Modelo del LLM | `llm_agent_node` |
| `bert_t5/` | Checkpoints de BERT y T5 (modo "libre", mas adelante) | `llm_agent_node` |
