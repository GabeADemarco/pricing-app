#!/bin/bash
# Script para configurar SSH automático en WSL
# Ejecutar en WSL de la notebook

echo "Configurando SSH automático en WSL..."

# 1. Agregar inicio automático de SSH al .bashrc
if ! grep -q "sshd" ~/.bashrc; then
    echo "" >> ~/.bashrc
    echo "# Iniciar SSH automáticamente si no está corriendo" >> ~/.bashrc
    echo "if ! pgrep -x \"sshd\" > /dev/null; then" >> ~/.bashrc
    echo "    sudo service ssh start > /dev/null 2>&1" >> ~/.bashrc
    echo "fi" >> ~/.bashrc
    echo "✓ Configuración agregada a ~/.bashrc"
else
    echo "✓ SSH ya está configurado en ~/.bashrc"
fi

# 2. Iniciar SSH ahora
sudo service ssh start
echo "✓ SSH iniciado"

# 3. Verificar que está corriendo
if pgrep -x "sshd" > /dev/null; then
    echo "✓ SSH está corriendo"
    sudo ss -tlnp | grep 2222 || echo "⚠ SSH no está escuchando en puerto 2222. Verifica la configuración en /etc/ssh/sshd_config"
else
    echo "⚠ SSH no está corriendo. Verifica los logs con: sudo service ssh status"
fi

echo ""
echo "Configuración completada!"
echo "SSH se iniciará automáticamente cada vez que abras WSL."
