# Imagen de desarrollo del equipo HRI: Ubuntu 22.04 + ROS 2 Humble + dependencias.
# Construir:  docker compose build      (ver docs/docker.md)
FROM ros:humble-ros-base

ARG USERNAME=hri
ARG USER_UID=1000
ARG USER_GID=1000
ENV DEBIAN_FRONTEND=noninteractive
SHELL ["/bin/bash", "-c"]

# 1. Paquetes del sistema  ->  apt-packages.txt
COPY apt-packages.txt scripts/install_apt.sh /tmp/deps/
RUN bash /tmp/deps/install_apt.sh /tmp/deps/apt-packages.txt \
    && rm -rf /var/lib/apt/lists/*

# 2. Librerias de Python  ->  requirements.txt
COPY requirements.txt /tmp/deps/
RUN python3 -m pip install --no-cache-dir -r /tmp/deps/requirements.txt

# 3. Audio: ALSA -> PulseAudio/PipeWire del computador
COPY docker/asound.conf /etc/asound.conf

# 4. Usuario con el mismo UID/GID que el del computador
#    (asi build/ e install/ y los archivos editados no quedan como root)
RUN apt-get update && apt-get install -y --no-install-recommends sudo \
    && rm -rf /var/lib/apt/lists/* \
    && (getent group ${USER_GID} || groupadd --gid ${USER_GID} ${USERNAME}) \
    && useradd --uid ${USER_UID} --gid ${USER_GID} --groups audio -m -s /bin/bash ${USERNAME} \
    && echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/${USERNAME}

USER ${USERNAME}
ENV HRI_WS=/home/${USERNAME}/hri_ws
ENV HRI_MODELS_DIR=/home/${USERNAME}/hri_ws/src/andesrobot_hri/models

# 5. Workspace y entorno de ROS 2 al abrir la terminal
RUN mkdir -p ${HRI_WS}/src ${HRI_WS}/build ${HRI_WS}/install ${HRI_WS}/log \
    && echo 'source /opt/ros/humble/setup.bash' >> ~/.bashrc \
    && echo '[ -f ~/hri_ws/install/setup.bash ] && source ~/hri_ws/install/setup.bash' >> ~/.bashrc \
    && echo 'cd ~/hri_ws' >> ~/.bashrc

WORKDIR /home/${USERNAME}/hri_ws
CMD ["sleep", "infinity"]
