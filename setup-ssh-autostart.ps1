# Script para configurar SSH automático en WSL después de reinicios
# Ejecutar como Administrador en la notebook

Write-Host "Configurando SSH automático para WSL..." -ForegroundColor Green

# 1. Crear script de port forwarding que se ejecute al inicio
$startupScript = @"
# Script de port forwarding automático para WSL SSH
# Se ejecuta al inicio de Windows

# Esperar a que WSL esté listo
Start-Sleep -Seconds 5

# Obtener IP de WSL y configurar port forwarding
wsl hostname -I | ForEach-Object {
    `$wslIp = `$_.Trim()
    if (`$wslIp) {
        # Eliminar regla existente si existe
        netsh interface portproxy delete v4tov4 listenport=2222 listenaddress=0.0.0.0 2>$null
        # Crear nueva regla
        netsh interface portproxy add v4tov4 listenport=2222 listenaddress=0.0.0.0 connectport=2222 connectaddress=`$wslIp
        Write-Host "Port forwarding configurado: 0.0.0.0:2222 -> `$wslIp:2222" -ForegroundColor Green
    }
}
"@

$startupPath = "$env:ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp\wsl-ssh-portforward.ps1"
$startupScript | Out-File -FilePath $startupPath -Encoding UTF8 -Force
Write-Host "✓ Script de port forwarding creado en: $startupPath" -ForegroundColor Green

# 2. Configurar política de ejecución para el script de inicio
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
Write-Host "✓ Política de ejecución configurada" -ForegroundColor Green

# 3. Crear tarea programada como alternativa (más confiable)
$taskName = "WSL-SSH-PortForward"
$taskAction = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$startupPath`""
$taskTrigger = New-ScheduledTaskTrigger -AtLogOn
$taskPrincipal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Highest
$taskSettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# Eliminar tarea existente si existe
Unregister-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

# Crear nueva tarea
Register-ScheduledTask -TaskName $taskName -Action $taskAction -Trigger $taskTrigger -Principal $taskPrincipal -Settings $taskSettings -Description "Configura port forwarding para SSH de WSL al iniciar Windows" | Out-Null
Write-Host "✓ Tarea programada creada: $taskName" -ForegroundColor Green

# 4. Configurar SSH para iniciar automáticamente en WSL
Write-Host "`nConfigurando SSH en WSL..." -ForegroundColor Yellow
Write-Host "Ejecuta estos comandos en WSL:" -ForegroundColor Yellow
Write-Host "  echo 'if ! pgrep -x `"sshd`" > /dev/null; then sudo service ssh start; fi' >> ~/.bashrc" -ForegroundColor Cyan
Write-Host "  sudo service ssh start" -ForegroundColor Cyan

Write-Host "`n✓ Configuración completada!" -ForegroundColor Green
Write-Host "`nPróximos pasos:" -ForegroundColor Yellow
Write-Host "1. Reinicia Windows para probar" -ForegroundColor White
Write-Host "2. Después del reinicio, verifica con: netsh interface portproxy show all" -ForegroundColor White
Write-Host "3. Prueba la conexión SSH desde el PC de escritorio" -ForegroundColor White
