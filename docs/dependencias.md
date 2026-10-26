# Dónde agregar una librería

**Regla:** si una librería no está en estos archivos, **solo existe en tu computador**.
Cuando otro integrante descargue el repositorio, su código no va a funcionar.

## ¿Qué tipo de librería es?

| Tipo | Ejemplos | Dónde se agrega | Cómo |
|---|---|---|---|
| Librería de **Python** (`pip install ...`) | `vosk`, `sounddevice`, `llama-cpp-python` | `requirements.txt` (raíz) | Una línea en la sección de tu equipo: `vosk` o `vosk==0.3.45` |
| Paquete del **sistema** (`sudo apt install ...`) | `espeak-ng`, `libportaudio2`, `ffmpeg` | `apt-packages.txt` (raíz) | Una línea. Si puede no existir, agrega `# opcional` al final |
| Paquete de **ROS 2** | `ros-humble-nav2-msgs` | `apt-packages.txt` **y** `package.xml` del paquete que lo usa | `ros-humble-nav2-msgs` en apt; `<exec_depend>nav2_msgs</exec_depend>` en el `package.xml` |
| **Modelo** (archivo pesado) | Modelo de Vosk, del LLM | `models/` + su descarga en `scripts/download_models.sh` | **No se sube a GitHub** |

Si el tutorial dice `pip install X`, va en `requirements.txt`.
Si dice `sudo apt install X`, va en `apt-packages.txt`.

## Después de agregarla

| Trabajas con | Comando |
|---|---|
| Docker | `docker compose up -d --build` |
| Sin Docker | `bash scripts/install_deps.sh` |

Y súbela a GitHub junto con tu código:

```bash
git add requirements.txt apt-packages.txt <tus archivos>
git commit -m "hri_speech: STT con Vosk (agrega vosk a requirements.txt)"
git push
```

## Errores comunes

| Problema | Causa | Solución |
|---|---|---|
| `ModuleNotFoundError: No module named 'X'` | La librería no está en `requirements.txt` | Agregarla y reconstruir |
| Instalé con `pip install` dentro del contenedor y luego ya no está | Lo instalado a mano se pierde al recrear el contenedor | Agregarla a `requirements.txt` y reconstruir |
| En mi computador funciona y en el de otro no | Algo quedó instalado solo en tu computador | Revisar `requirements.txt` y `apt-packages.txt` |
| `FileNotFoundError` con un modelo | No se descargó, o la ruta es de tu computador | `bash scripts/download_models.sh`; usar `HRI_MODELS_DIR` |

## Rutas de modelos y archivos

Nunca uses rutas como `/home/usuario/...`. Dentro de Docker, `HRI_MODELS_DIR` apunta a `models/`:

```python
import os
models_dir = os.environ.get('HRI_MODELS_DIR', 'models')
vosk_path = os.path.join(models_dir, 'vosk', 'vosk-model-small-en-us-0.15')
```
