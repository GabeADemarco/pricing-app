# Configurar SSH Automático después de Reinicios

Esta guía te ayudará a configurar SSH para que funcione automáticamente después de reiniciar Windows, sin tener que hacer nada manualmente.

## 📋 Requisitos Previos

- ✅ SSH ya configurado y funcionando (puerto 2222)
- ✅ Port forwarding configurado manualmente al menos una vez
- ✅ Autenticación por clave SSH configurada (opcional pero recomendado)

## 🚀 Configuración Rápida

### Paso 1: Configurar Port Forwarding Automático (Notebook - Windows)

**En la notebook, abre PowerShell como Administrador y ejecuta:**

```powershell
# Ejecutar el script de configuración
.\setup-ssh-autostart.ps1
```

O si prefieres hacerlo manualmente:

**1. Crear script de inicio:**

Crea el archivo: `C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp\wsl-ssh-portforward.ps1`

Con este contenido:

```powershell
# Script de port forwarding automático para WSL SSH
Start-Sleep -Seconds 5

wsl hostname -I | ForEach-Object {
    $wslIp = $_.Trim()
    if ($wslIp) {
        netsh interface portproxy delete v4tov4 listenport=2222 listenaddress=0.0.0.0 2>$null
        netsh interface portproxy add v4tov4 listenport=2222 listenaddress=0.0.0.0 connectport=2222 connectaddress=$wslIp
    }
}
```

**2. Configurar política de ejecución:**

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
```

### Paso 2: Configurar SSH Automático en WSL (Notebook)

**En la notebook, abre WSL y ejecuta:**

```bash
# Ejecutar el script
bash setup-wsl-ssh-autostart.sh
```

O manualmente:

```bash
# Agregar inicio automático al .bashrc
echo "" >> ~/.bashrc
echo "# Iniciar SSH automáticamente si no está corriendo" >> ~/.bashrc
echo "if ! pgrep -x \"sshd\" > /dev/null; then" >> ~/.bashrc
echo "    sudo service ssh start > /dev/null 2>&1" >> ~/.bashrc
echo "fi" >> ~/.bashrc

# Iniciar SSH ahora
sudo service ssh start
```

### Paso 3: Verificar que Todo Funciona

**Después de reiniciar Windows:**

**1. Verificar port forwarding (en notebook - PowerShell):**

```powershell
netsh interface portproxy show all
```

Deberías ver:
```
Escuchar en ipv4:       Conectar a ipv4:
Dirección       Puerto      Dirección       Puerto
--------------- ----------  --------------- ----------
0.0.0.0         2222        172.18.18.95    2222
```

**2. Verificar SSH en WSL (en notebook - WSL):**

```bash
sudo service ssh status
sudo ss -tlnp | grep 2222
```

**3. Probar conexión desde PC de escritorio:**

```powershell
Test-NetConnection -ComputerName 192.168.0.228 -Port 2222
ssh user@192.168.0.228 -p 2222
```

## 🔧 Solución de Problemas

### El port forwarding no se configura después del reinicio

**Solución 1: Verificar que el script está en la carpeta de inicio**

```powershell
Test-Path "$env:ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp\wsl-ssh-portforward.ps1"
```

**Solución 2: Ejecutar manualmente el script**

```powershell
& "$env:ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp\wsl-ssh-portforward.ps1"
```

**Solución 3: Usar tarea programada (más confiable)**

El script `setup-ssh-autostart.ps1` crea automáticamente una tarea programada. Verifica que existe:

```powershell
Get-ScheduledTask -TaskName "WSL-SSH-PortForward"
```

### SSH no inicia automáticamente en WSL

**Verificar que está en .bashrc:**

```bash
cat ~/.bashrc | grep sshd
```

**Iniciar manualmente:**

```bash
sudo service ssh start
```

**Verificar logs:**

```bash
sudo service ssh status
sudo journalctl -u ssh -n 50
```

## 📝 Notas Importantes

1. **Port Forwarding**: Se configura automáticamente al iniciar Windows (espera ~5 segundos para que WSL esté listo)

2. **SSH en WSL**: Se inicia automáticamente cada vez que abres una terminal de WSL

3. **IP de WSL**: Puede cambiar si WSL se reinicia. El script detecta automáticamente la IP actual

4. **Firewall**: Las reglas del firewall son permanentes y no necesitan reconfiguración

## ✅ Checklist Post-Reinicio

Después de reiniciar Windows, verifica:

- [ ] Port forwarding configurado (`netsh interface portproxy show all`)
- [ ] SSH corriendo en WSL (`sudo service ssh status`)
- [ ] Puerto 2222 escuchando (`sudo ss -tlnp | grep 2222`)
- [ ] Conexión SSH funciona desde PC de escritorio (`ssh user@192.168.0.228 -p 2222`)

Si todo está ✅, ¡ya no necesitas hacer nada manualmente después de reiniciar!
