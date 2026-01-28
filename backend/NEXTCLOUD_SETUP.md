# Configuración de Nextcloud para Upload de Archivos

Este documento explica cómo configurar Nextcloud para que el sistema pueda subir archivos automáticamente.

## Variables de Entorno

Agregá las siguientes variables a tu archivo `.env` del backend:

```env
# Nextcloud Configuration
NEXTCLOUD_URL=https://cloud.gaussonline.com.ar
NEXTCLOUD_USER=tu_usuario_nextcloud
NEXTCLOUD_PASSWORD=tu_contraseña_nextcloud

# O mejor aún, usar App Password (recomendado)
NEXTCLOUD_APP_PASSWORD=tu_app_password_generado
```

## Configuración Recomendada: App Password

Para mayor seguridad, es recomendable usar un **App Password** en lugar de tu contraseña principal:

1. Entrá a tu Nextcloud: https://cloud.gaussonline.com.ar
2. Andá a **Configuración** → **Seguridad**
3. En la sección **App Passwords**, creá uno nuevo llamado "Pricing App"
4. Copiá el password generado y usalo en `NEXTCLOUD_APP_PASSWORD`

**Ventajas:**
- No compromete tu contraseña principal
- Podés revocarlo fácilmente si es necesario
- Más seguro para uso en producción

## Estructura de Carpetas

Los archivos se subirán a la carpeta `/Facturas` en Nextcloud. Asegurate de que:

1. El usuario configurado tenga permisos de escritura en esa carpeta
2. La carpeta exista (se creará automáticamente si tiene permisos)

## Funcionamiento

Cuando un usuario arrastra un archivo en el formulario:

1. El archivo se sube a Nextcloud usando WebDAV API
2. Se crea un link compartido público (read-only)
3. El link se guarda automáticamente en el campo correspondiente
4. El usuario puede hacer clic en el link para ver el archivo

## Troubleshooting

### Error: "Nextcloud no está configurado"
- Verificá que `NEXTCLOUD_URL` esté en el `.env`
- Reiniciá el backend después de agregar las variables

### Error: "Credenciales de Nextcloud no configuradas"
- Verificá que `NEXTCLOUD_USER` y `NEXTCLOUD_PASSWORD` (o `NEXTCLOUD_APP_PASSWORD`) estén configurados
- Probá las credenciales iniciando sesión manualmente en Nextcloud

### Error al subir archivo
- Verificá que el usuario tenga permisos de escritura en `/Facturas`
- Verificá que la carpeta exista
- Revisá los logs del backend para más detalles

### No se crea link compartido
- El sistema seguirá funcionando, pero solo tendrás la URL directa del archivo
- Verificá que el usuario tenga permisos para crear shares públicos
