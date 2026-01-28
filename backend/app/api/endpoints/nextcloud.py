"""
Endpoints para integración con Nextcloud
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.usuario import Usuario
from app.core.config import settings
import httpx
import base64
import os
from datetime import datetime
from typing import Optional
import logging

router = APIRouter(prefix="/nextcloud", tags=["Nextcloud"])
logger = logging.getLogger(__name__)


def get_nextcloud_auth() -> tuple[str, str]:
    """Obtiene credenciales de Nextcloud"""
    if settings.NEXTCLOUD_APP_PASSWORD:
        # Usar app password si está configurado (recomendado)
        return settings.NEXTCLOUD_USER or "", settings.NEXTCLOUD_APP_PASSWORD
    else:
        # Fallback a password normal
        return settings.NEXTCLOUD_USER or "", settings.NEXTCLOUD_PASSWORD or ""


@router.post("/upload")
async def upload_file_to_nextcloud(
    file: UploadFile = File(...),
    folder: str = Form("Facturas"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Sube un archivo a Nextcloud y crea un link compartido.
    Requiere configuración de NEXTCLOUD_URL, NEXTCLOUD_USER y NEXTCLOUD_PASSWORD en .env
    """
    if not settings.NEXTCLOUD_URL:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Nextcloud no está configurado. Verificar NEXTCLOUD_URL en .env"
        )

    username, password = get_nextcloud_auth()
    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Credenciales de Nextcloud no configuradas. Verificar NEXTCLOUD_USER y NEXTCLOUD_PASSWORD en .env"
        )

    try:
        # Leer contenido del archivo
        file_content = await file.read()
        file_size = len(file_content)

        # Validar tamaño (máx 50MB)
        max_size = 50 * 1024 * 1024
        if file_size > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El archivo es muy grande. Máximo 50MB"
            )

        # Generar nombre único para el archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = os.path.splitext(file.filename)[1]
        file_base_name = os.path.splitext(file.filename)[0]
        
        # Incluir username del usuario actual y TEST al final
        # TODO: TEMPORAL - Remover "_TEST" antes de merge a producción
        # El sufijo "_TEST" es solo para desarrollo, permite identificar y borrar fácilmente archivos de prueba
        username_safe = current_user.username.replace('@', '_at_').replace('.', '_')
        safe_filename = f"{timestamp}_{file_base_name}_{username_safe}_TEST{file_extension}"
        
        # Ruta en Nextcloud
        remote_path = f"/{folder}/{safe_filename}"
        
        # URL base de Nextcloud (sin trailing slash)
        base_url = settings.NEXTCLOUD_URL.rstrip('/')
        
        # Nextcloud WebDAV usa solo la parte local del email como username en la URL
        # pero la autenticación puede usar el email completo
        dav_username = username.split('@')[0] if '@' in username else username
        
        # URL para subir archivo (WebDAV) - usar solo la parte local del username
        upload_url = f"{base_url}/remote.php/dav/files/{dav_username}{remote_path}"

        # Autenticación básica - intentar primero con email completo, luego solo username
        # Algunos Nextcloud requieren email completo, otros solo username
        auth_username = username  # Intentar con email completo primero
        auth = base64.b64encode(f"{auth_username}:{password}".encode()).decode()

        # Subir archivo usando WebDAV PUT
        async with httpx.AsyncClient(timeout=30.0) as client:
            upload_response = await client.put(
                upload_url,
                content=file_content,
                headers={
                    "Authorization": f"Basic {auth}",
                    "Content-Type": file.content_type or "application/octet-stream",
                    "Content-Length": str(file_size)
                }
            )

            if upload_response.status_code not in [200, 201, 204]:
                logger.error(f"Error subiendo archivo a Nextcloud: {upload_response.status_code} - {upload_response.text}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error al subir archivo a Nextcloud: {upload_response.status_code}"
                )

            # Crear share público para obtener link
            share_url = f"{base_url}/ocs/v2.php/apps/files_sharing/api/v1/shares"
            
            share_response = await client.post(
                share_url,
                headers={
                    "Authorization": f"Basic {auth}",
                    "OCS-APIRequest": "true",
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                data={
                    "path": remote_path,
                    "shareType": 3,  # Public link
                    "permissions": 1  # Read only
                }
            )

            if share_response.status_code == 200:
                # Parsear respuesta XML (Nextcloud devuelve XML)
                import xml.etree.ElementTree as ET
                root = ET.fromstring(share_response.text)
                
                # Buscar el elemento url
                url_element = root.find(".//{http://owncloud.org/ns}url")
                if url_element is not None:
                    share_token = url_element.text
                    share_link = f"{base_url}/s/{share_token}"
                    
                    return {
                        "success": True,
                        "file_url": f"{base_url}/remote.php/dav/files/{username}{remote_path}",
                        "share_url": share_link,
                        "filename": safe_filename,
                        "path": remote_path
                    }
            
            # Si falla crear share, devolver URL directa del archivo
            logger.warning("No se pudo crear share público, devolviendo URL directa")
            return {
                "success": True,
                "file_url": f"{base_url}/remote.php/dav/files/{dav_username}{remote_path}",
                "share_url": None,
                "filename": safe_filename,
                "path": remote_path,
                "warning": "No se pudo crear link compartido público"
            }

    except httpx.TimeoutException:
        logger.error("Timeout al subir archivo a Nextcloud")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Timeout al subir archivo a Nextcloud"
        )
    except Exception as e:
        logger.error(f"Error inesperado al subir archivo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al subir archivo: {str(e)}"
        )
