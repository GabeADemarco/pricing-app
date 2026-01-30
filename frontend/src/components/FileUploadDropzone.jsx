import { useState, useRef } from 'react';
import styles from './FileUploadDropzone.module.css';

export default function FileUploadDropzone({ 
  value, 
  onChange, 
  onUploadComplete,
  folder = 'Facturas',
  accept = 'application/pdf,image/*',
  maxSizeMB = 10
}) {
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const handleDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      await handleFileUpload(files[0]);
    }
  };

  const handleFileSelect = async (e) => {
    const files = Array.from(e.target.files);
    if (files.length > 0) {
      await handleFileUpload(files[0]);
    }
  };

  const handleFileUpload = async (file) => {
    // Validar tipo de archivo
    if (!file.type.match(/^(application\/pdf|image\/(jpeg|jpg|png|gif))$/i)) {
      setError('Solo se permiten archivos PDF o imágenes');
      return;
    }

    // Validar tamaño
    const maxSizeBytes = maxSizeMB * 1024 * 1024;
    if (file.size > maxSizeBytes) {
      setError(`El archivo es muy grande. Máximo ${maxSizeMB}MB`);
      return;
    }

    setError(null);
    setUploading(true);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const token = localStorage.getItem('token');
      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8002/api';
      // Construir URL: remover /api si existe al final, luego agregar /api/upload/factura
      const baseUrl = API_URL.replace(/\/api$/, '');
      const uploadUrl = `${baseUrl}/api/upload/factura`;

      const response = await fetch(uploadUrl, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`
        },
        body: formData
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error al subir el archivo');
      }

      const data = await response.json();
      
      // Construir URL completa para el archivo
      // file_url viene como /api/files/facturas/{filename}, necesitamos la URL completa
      const baseApiUrl = API_URL.replace(/\/api$/, '');
      const fullFileUrl = data.file_url.startsWith('http') 
        ? data.file_url 
        : `${baseApiUrl}${data.file_url}`;
      
      if (onChange) {
        onChange(fullFileUrl);
      }

      if (onUploadComplete) {
        onUploadComplete(data);
      }

    } catch (err) {
      console.error('Error uploading file:', err);
      setError(err.message || 'Error al subir el archivo');
    } finally {
      setUploading(false);
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className={styles.container}>
      <div
        className={`${styles.dropzone} ${isDragging ? styles.dragging : ''} ${uploading ? styles.uploading : ''}`}
        onDragEnter={handleDragEnter}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept={accept}
          onChange={handleFileSelect}
          className={styles.fileInput}
          disabled={uploading}
        />

        {uploading ? (
          <div className={styles.uploadingContent}>
            <div className={styles.spinner}></div>
            <span>Subiendo archivo...</span>
          </div>
        ) : (
          <div className={styles.dropzoneContent}>
            {value ? (
              <>
                <span className={styles.checkIcon}>✓</span>
                <span className={styles.fileLink} onClick={(e) => e.stopPropagation()}>
                  <a href={value} target="_blank" rel="noopener noreferrer">
                    Archivo subido - Ver
                  </a>
                </span>
                <span className={styles.changeFile}>Hacé clic o arrastrá otro archivo para cambiar</span>
              </>
            ) : (
              <>
                <span className={styles.icon}>📎</span>
                <span className={styles.text}>
                  Arrastrá un archivo aquí o hacé clic para seleccionar
                </span>
                <span className={styles.hint}>
                  PDF o imagen (máx. {maxSizeMB}MB)
                </span>
              </>
            )}
          </div>
        )}
      </div>

      {error && (
        <div className={styles.error}>
          {error}
        </div>
      )}

      {value && (
        <input
          type="url"
          value={value}
          onChange={(e) => onChange?.(e.target.value)}
          className={styles.urlInput}
          placeholder="O ingresá la URL manualmente"
        />
      )}
    </div>
  );
}
