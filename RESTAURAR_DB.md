# Comando para Restaurar Base de Datos

## Comando PowerShell (ejecutar en la raíz del proyecto):

```powershell
cd D:\Gabriel\PFA\Gauss\pricing-app\pricing-app
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d pricing_db_dev -f "DB\pricing_full.sql"
```

## Explicación:

- `-U postgres`: Usuario de PostgreSQL
- `-d pricing_db_dev`: Base de datos destino
- `-f "DB\pricing_full.sql"`: Archivo SQL a ejecutar

## Cuando ejecutes el comando:

1. Te pedirá la contraseña de PostgreSQL (tu DNI: `35359014`)
2. Verás el progreso en la consola
3. Puede tardar varios minutos (el archivo es de 1.1 GB)
4. Al finalizar, deberías ver mensajes de éxito

## Si hay errores:

- Verifica que PostgreSQL esté corriendo
- Verifica que la base de datos `pricing_db_dev` exista
- Verifica que el archivo `DB\pricing_full.sql` exista
