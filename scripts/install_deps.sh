#!/usr/bin/env bash
# Instala las dependencias SIN Docker (Ubuntu 22.04 + ROS 2 Humble ya instalado).
# Con Docker no hace falta: el Dockerfile hace lo mismo.
# Uso (desde la raiz del repositorio):  bash scripts/install_deps.sh
set -e
REPO="$(cd "$(dirname "$0")/.." && pwd)"

if [ ! -f /opt/ros/humble/setup.bash ]; then
    echo "No se encontro ROS 2 Humble. Usa Docker (ver docs/docker.md)."
    exit 1
fi

echo "== 1/3 Paquetes del sistema (apt-packages.txt) =="
bash "$REPO/scripts/install_apt.sh" "$REPO/apt-packages.txt"

echo "== 2/3 Librerias de Python (requirements.txt) =="
python3 -m pip install --user -r "$REPO/requirements.txt"

echo "== 3/3 Modelos =="
bash "$REPO/scripts/download_models.sh"

echo "Listo. Ahora compila:  cd ~/hri_ws && colcon build --symlink-install"
