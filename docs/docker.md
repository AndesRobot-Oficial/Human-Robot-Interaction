# Trabajar con Docker

El contenedor trae Ubuntu 22.04, ROS 2 Humble y todas las dependencias
(`apt-packages.txt` y `requirements.txt`). El repositorio se **monta**: lo que editas en tu
computador se ve dentro del contenedor al instante.

## 1. Instalar Docker (una sola vez)

Ubuntu 24.04:

```bash
sudo apt install -y docker.io docker-compose-v2 docker-buildx
sudo usermod -aG docker $USER
```

Cierra la sesión, vuelve a entrar y prueba: `docker run hello-world`.

Si `id -u` no es `1000`, crea un archivo `.env` en la raíz del repositorio con
`HOST_UID=<tu id>` y `HOST_GID=<tu id>`.

## 2. Descargar el repositorio

```bash
git clone git@github.com:AndesRobot-Oficial/Human-Robot-Interaction.git
cd Human-Robot-Interaction
bash scripts/download_models.sh
```

## 3. Uso diario

| Qué | Comando |
|---|---|
| Construir y arrancar | `docker compose up -d --build` |
| Entrar al contenedor (una o varias terminales) | `docker compose exec hri bash` |
| Detener | `docker compose down` |

| Prompt | Dónde estás | Qué se hace ahí |
|---|---|---|
| `usuario@computador` | Tu computador | Git, `docker compose`, editar archivos |
| `hri@computador:~/hri_ws` | Dentro del contenedor | `colcon build`, `ros2 run`, `ros2 topic` |

Dentro del contenedor:

```bash
colcon build --symlink-install
source install/setup.bash
ros2 run hri_orchestrator task_orchestrator_node
```

`--build` solo tarda la primera vez o cuando cambian `apt-packages.txt`,
`requirements.txt` o el `Dockerfile`.

## 4. Probar el audio (dentro del contenedor)

```bash
pactl info | grep "Server Name"
speaker-test -t wav -c 1 -l 1
arecord -d 3 -f S16_LE -r 16000 -c 1 /tmp/prueba.wav && aplay /tmp/prueba.wav
```

Para agregar una librería, ver [dependencias.md](dependencias.md).
