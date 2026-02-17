# Configurar Nextcloud

Para desarrollo, agregá estas líneas a tu archivo `.env` del backend:

```env
# Nextcloud Configuration
NEXTCLOUD_URL=https://cloud.gaussonline.com.ar
NEXTCLOUD_USER=tu_usuario_nextcloud
NEXTCLOUD_PASSWORD=tu_contraseña_nextcloud
# O mejor usar App Password (recomendado):
# NEXTCLOUD_APP_PASSWORD=tu_app_password_generado
```

**⚠️ IMPORTANTE:** 
- **NUNCA** commitees credenciales reales al repositorio
- Usa variables de entorno o un archivo `.env` local (que está en `.gitignore`)
- Para producción, usa App Password en lugar de contraseña de usuario

**Formato de nombres de archivo:**
Los archivos se subirán con el formato:
```
YYYYMMDD_HHMMSS_nombre_original_username.ext
```

Ejemplo:
- Archivo original: `factura.pdf`
- Usuario: `compras`
- Resultado: `20250128_143022_factura_compras.pdf`

Esto permite:
- Identificar quién subió el archivo
- Evitar conflictos de nombres
- Timestamp para ordenamiento cronológico
