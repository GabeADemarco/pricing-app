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
        
        # Incluir username del usuario actual para identificar quién subió el archivo
        username_safe = current_user.username.replace('@', '_at_').replace('.', '_')
        safe_filename = f"{timestamp}_{file_base_name}_{username_safe}{file_extension}"
        
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
                    "permissions": 1,  # Read only
                    "publicUpload": "false"  # No permitir subida pública
                }
            )

            logger.info(f"Share response status: {share_response.status_code}")
            logger.debug(f"Share response text completo: {share_response.text}")  # XML completo para debugging

            if share_response.status_code == 200:
                # Parsear respuesta XML (Nextcloud devuelve XML)
                import xml.etree.ElementTree as ET
                try:
                    root = ET.fromstring(share_response.text)
                    
                    # Buscar el token del share en diferentes ubicaciones posibles
                    # Nextcloud puede devolver el token en diferentes elementos según la versión
                    share_token = None
                    
                    # Intentar con namespace
                    url_element = root.find(".//{http://owncloud.org/ns}url")
                    if url_element is not None and url_element.text:
                        share_token = url_element.text
                    
                    # Si no se encontró con namespace, buscar sin namespace
                    if not share_token:
                        url_element = root.find(".//url")
                        if url_element is not None and url_element.text:
                            share_token = url_element.text
                    
                    # También buscar en elemento "token" directamente
                    if not share_token:
                        token_element = root.find(".//token")
                        if token_element is not None and token_element.text:
                            share_token = token_element.text
                    
                    # Buscar en el elemento data directamente
                    if not share_token:
                        data_element = root.find(".//data")
                        if data_element is not None:
                            # Buscar url dentro de data (con y sin namespace)
                            url_in_data = data_element.find("url")
                            if url_in_data is None:
                                url_in_data = data_element.find("{http://owncloud.org/ns}url")
                            if url_in_data is not None and url_in_data.text:
                                share_token = url_in_data.text
                            
                            # O buscar token dentro de data (con y sin namespace)
                            if not share_token:
                                token_in_data = data_element.find("token")
                                if token_in_data is None:
                                    token_in_data = data_element.find("{http://owncloud.org/ns}token")
                                if token_in_data is not None and token_in_data.text:
                                    share_token = token_in_data.text
                            
                            # También buscar todos los elementos hijos de data para debugging
                            if not share_token:
                                logger.debug(f"Elementos en data: {[child.tag for child in data_element]}")
                                for child in data_element:
                                    logger.debug(f"  {child.tag}: {child.text}")
                    
                    if share_token:
                        # Limpiar el token: puede venir como URL completa o solo el token
                        # Si viene como URL completa, extraer solo el token
                        share_token_clean = share_token.strip()
                        
                        # Si el token parece ser una URL completa, extraer solo la parte del token
                        if share_token_clean.startswith('http'):
                            # Intentar extraer el token de una URL completa
                            # Ejemplo: https://cloud.../s/kSTtD766cX9BSpp?dir=/&openfile=true -> kSTtD766cX9BSpp
                            import re
                            match = re.search(r'/s/([^/?]+)', share_token_clean)
                            if match:
                                share_token_clean = match.group(1)
                            else:
                                # Si no se puede extraer, usar el token tal cual (puede ser un token largo)
                                logger.warning(f"No se pudo extraer token de URL completa: {share_token_clean}")
                        
                        # Usar formato de visualización para que se muestre en iframe en lugar de descargar
                        share_link = f"{base_url}/index.php/s/{share_token_clean}?dir=/&openfile=true"
                        
                        logger.info(f"Share creado exitosamente. Token: {share_token_clean[:20]}..., Link: {share_link}")
                        return {
                            "success": True,
                            "file_url": f"{base_url}/remote.php/dav/files/{username}{remote_path}",
                            "share_url": share_link,
                            "filename": safe_filename,
                            "path": remote_path
                        }
                    else:
                        # Log completo del XML para debugging
                        logger.error("No se encontró el token de share en la respuesta XML")
                        logger.error(f"XML completo: {share_response.text}")
                        # Intentar extraer el ID del share y construir el link manualmente
                        # A veces Nextcloud devuelve solo el ID y necesitamos hacer otra llamada
                        id_element = root.find(".//id")
                        if id_element is not None and id_element.text:
                            share_id = id_element.text
                            logger.warning(f"Se encontró ID de share ({share_id}) pero no token. Intentando obtener token...")
                            # Hacer GET al share para obtener el token
                            get_share_url = f"{base_url}/ocs/v2.php/apps/files_sharing/api/v1/shares/{share_id}"
                            get_share_response = await client.get(
                                get_share_url,
                                headers={
                                    "Authorization": f"Basic {auth}",
                                    "OCS-APIRequest": "true"
                                }
                            )
                            if get_share_response.status_code == 200:
                                share_root = ET.fromstring(get_share_response.text)
                                token_from_get = share_root.find(".//token")
                                if token_from_get is not None and token_from_get.text:
                                    share_token = token_from_get.text.strip()
                                    
                                    # Limpiar el token si viene como URL completa
                                    if share_token.startswith('http'):
                                        import re
                                        match = re.search(r'/s/([^/?]+)', share_token)
                                        if match:
                                            share_token = match.group(1)
                                    
                                    share_link = f"{base_url}/index.php/s/{share_token}?dir=/&openfile=true"
                                    logger.info(f"Share creado exitosamente (vía GET): {share_link}")
                                    return {
                                        "success": True,
                                        "file_url": f"{base_url}/remote.php/dav/files/{username}{remote_path}",
                                        "share_url": share_link,
                                        "filename": safe_filename,
                                        "path": remote_path
                                    }
                        
                        raise HTTPException(
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"No se pudo extraer el token del share desde la respuesta XML. XML: {share_response.text[:500]}"
                        )
                except ET.ParseError as e:
                    logger.error(f"Error parseando XML de respuesta de share: {str(e)}")
                    logger.error(f"Contenido XML: {share_response.text}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Error parseando respuesta XML de Nextcloud: {str(e)}"
                    )
            
            # Si falla crear share, lanzar error descriptivo
            error_detail = f"No se pudo crear share público. Status: {share_response.status_code}"
            if share_response.status_code == 401:
                error_detail += " (Error de autenticación. Verificar credenciales de Nextcloud)"
            elif share_response.status_code == 403:
                error_detail += " (Sin permisos para crear shares públicos)"
            elif share_response.status_code == 404:
                error_detail += f" (Archivo no encontrado en ruta: {remote_path})"
            else:
                error_detail += f" Respuesta: {share_response.text[:200]}"
            
            logger.error(error_detail)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_detail
            )

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
