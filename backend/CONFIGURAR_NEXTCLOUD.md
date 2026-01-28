# Configurar Nextcloud - Credenciales Temporales

Para desarrollo, agregá estas líneas a tu archivo `.env` del backend:

```env
# Nextcloud Configuration (Temporal para desarrollo)
NEXTCLOUD_URL=https://cloud.gaussonline.com.ar
NEXTCLOUD_USER=gdemarco@gaussonline.com.ar
NEXTCLOUD_PASSWORD=Gabegato2323
```

**Nota:** Cuando Chicho cree el App Password, actualizá el `.env` para usar:
```env
NEXTCLOUD_APP_PASSWORD=el_app_password_que_te_dé_chicho
```

Y comentá o eliminá la línea `NEXTCLOUD_PASSWORD`.

**Formato de nombres de archivo:**
Los archivos se subirán con el formato:
```
YYYYMMDD_HHMMSS_nombre_original_username_TEST.ext
```

Ejemplo:
- Archivo original: `factura.pdf`
- Usuario: `compras`
- Resultado: `20250128_143022_factura_compras_TEST.pdf`

Esto permite:
- Identificar quién subió el archivo
- Identificar fácilmente archivos de prueba (terminan en `_TEST`)
- Evitar conflictos de nombres
