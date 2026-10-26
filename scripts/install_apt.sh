#!/usr/bin/env bash
# Instala los paquetes de apt-packages.txt.
# Lo usan el Dockerfile y scripts/install_deps.sh. Uso: bash scripts/install_apt.sh [archivo]
set -e
FILE="${1:-$(dirname "$0")/../apt-packages.txt}"
SUDO=""
[ "$(id -u)" -ne 0 ] && SUDO="sudo"

REQUIRED=()
OPTIONAL=()
while IFS= read -r line || [ -n "$line" ]; do
    pkg="$(echo "${line%%#*}" | xargs)"
    [ -z "$pkg" ] && continue
    if [[ "$line" == *"# opcional"* ]]; then
        OPTIONAL+=("$pkg")
    else
        REQUIRED+=("$pkg")
    fi
done < "$FILE"

export DEBIAN_FRONTEND=noninteractive
$SUDO apt-get update
echo "Obligatorios: ${REQUIRED[*]}"
$SUDO apt-get install -y --no-install-recommends "${REQUIRED[@]}"

FAILED=()
for pkg in "${OPTIONAL[@]}"; do
    $SUDO apt-get install -y --no-install-recommends "$pkg" || FAILED+=("$pkg")
done
if [ ${#FAILED[@]} -gt 0 ]; then
    echo "[AVISO] No se instalaron estos paquetes opcionales: ${FAILED[*]}"
fi
