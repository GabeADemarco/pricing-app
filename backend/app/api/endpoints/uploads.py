"""
Endpoints para subir archivos localmente al servidor
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.usuario import Usuario
from app.core.config import settings
import os
from datetime import datetime
from pathlib import Path
import logging
import shutil

router = APIRouter(prefix="/upload", tags=["Uploads"])
logger = logging.getLogger(__name__)

# Directorio base para uploads
UPLOADS_DIR = Path(__file__).parent.parent.parent.parent / "uploads"
FACTURAS_DIR = UPLOADS_DIR / "facturas"

# Asegurar que el directorio existe
FACTURAS_DIR.mkdir(parents=True, exist_ok=True)


def generate_filename(original_filename: str, username: str) -> str:
    """
    Genera un nombre de archivo único con formato:
    YYYYMMDD_HHMMSS_original_filename_username.ext
    """
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    
    # Obtener extensión
    ext = Path(original_filename).suffix
    
    # Limpiar nombre original (remover caracteres especiales)
    clean_name = Path(original_filename).stem
    clean_name = "".join(c for c in clean_name if c.isalnum() or c in (' ', '-', '_')).strip()
    clean_name = clean_name.replace(' ', '_')
    
    # Construir nombre final
    filename = f"{timestamp}_{clean_name}_{username}{ext}"
    
    return filename


@router.post("/factura")
async def upload_factura_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Sube un archivo de factura/proforma al servidor local.
    Retorna la URL pública para acceder al archivo.
    """
    try:
        # Validar tipo de archivo
        allowed_extensions = {'.pdf', '.jpg', '.jpeg', '.png', '.gif', '.webp'}
        file_ext = Path(file.filename).suffix.lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de archivo no permitido. Extensiones permitidas: {', '.join(allowed_extensions)}"
            )
        
        # Validar tamaño (máximo 10MB)
        file_content = await file.read()
        file_size_mb = len(file_content) / (1024 * 1024)
        
        if file_size_mb > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El archivo es demasiado grande. Tamaño máximo: 10MB. Tamaño actual: {file_size_mb:.2f}MB"
            )
        
        # Generar nombre único
        filename = generate_filename(file.filename, current_user.username)
        file_path = FACTURAS_DIR / filename
        
        # Guardar archivo
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
        
        # Generar URL pública (relativa, el frontend construirá la URL completa)
        file_url = f"/api/files/facturas/{filename}"
        
        logger.info(f"Archivo subido: {filename} por usuario {current_user.username} ({file_size_mb:.2f}MB)")
        
        return {
            "filename": filename,
            "file_url": file_url,
            "size_mb": round(file_size_mb, 2),
            "uploaded_by": current_user.username,
            "uploaded_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al subir archivo: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al subir archivo: {str(e)}"
        )


# Nota: Los archivos se sirven directamente mediante StaticFiles montado en main.py
# en /api/files/facturas/{filename}. Este endpoint no es necesario si usamos StaticFiles,
# pero lo dejamos como alternativa si necesitamos autenticación en el futuro.
# Por ahora, StaticFiles permite acceso directo sin autenticación (los archivos están en el servidor).
