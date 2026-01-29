import { useState, useEffect } from 'react';
import styles from './ModalVisualizarDocumento.module.css';

export default function ModalVisualizarDocumento({ url, titulo, onClose }) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Convertir URL de descarga a URL de visualización para Nextcloud
  // Nextcloud requiere ?dir=/&openfile=true para mostrar en iframe en lugar de descargar
  const getViewUrl = () => {
    if (!url) return null;
    
    // Si es un share URL de Nextcloud (/s/ o /index.php/s/), asegurar formato de visualización
    if (url.includes('/s/')) {
      // Si ya tiene los parámetros de visualización, usarlo tal cual
      if (url.includes('openfile=true')) {
        return url;
      }
      
      // Si es formato corto /s/{token}, convertir a formato completo con parámetros
      // Ejemplo: cloud.gaussonline.com.ar/s/zAdmQn4LxCrk5xz
      // -> cloud.gaussonline.com.ar/index.php/s/zAdmQn4LxCrk5xz?dir=/&openfile=true
      try {
        const urlObj = new URL(url);
        const pathParts = urlObj.pathname.split('/s/');
        
        if (pathParts.length === 2) {
          const shareToken = pathParts[1].split('?')[0]; // Remover query params existentes si hay
          // Construir URL de visualización
          const basePath = urlObj.pathname.includes('/index.php') ? '/index.php' : '';
          return `${urlObj.protocol}//${urlObj.host}${basePath}/s/${shareToken}?dir=/&openfile=true`;
        }
      } catch (e) {
        // Si falla el parsing, intentar transformación simple
        if (url.includes('/s/') && !url.includes('openfile=true')) {
          // Agregar parámetros si no los tiene
          const separator = url.includes('?') ? '&' : '?';
          return `${url}${separator}dir=/&openfile=true`;
        }
      }
    }
    
    // Para otros tipos de URLs, devolver tal cual
    return url;
  };

  const viewUrl = getViewUrl();

  useEffect(() => {
    setLoading(true);
    setError(null);
  }, [url]);

  const handleIframeLoad = () => {
    setLoading(false);
  };

  const handleIframeError = () => {
    setLoading(false);
    setError('No se pudo cargar el documento. Puede requerir autenticación.');
  };

  return (
    <div className="modal-overlay-tesla" onClick={onClose}>
      <div className="modal-tesla xl" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header-tesla">
          <h2 className="modal-title-tesla">{titulo || 'Visualizar Documento'}</h2>
          <button
            className="btn-close-tesla"
            onClick={onClose}
            type="button"
          >
            ✕
          </button>
        </div>
        <div className={styles.modalBody}>
          {loading && (
            <div className={styles.loading}>
              <div className={styles.spinner}></div>
              <span>Cargando documento...</span>
            </div>
          )}
          {error && (
            <div className={styles.error}>
              <p>{error}</p>
              <a
                href={viewUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="btn-tesla primary"
              >
                Abrir en nueva pestaña
              </a>
            </div>
          )}
          {viewUrl && (
            <iframe
              src={viewUrl}
              className={styles.iframe}
              title={titulo || 'Documento'}
              onLoad={handleIframeLoad}
              onError={handleIframeError}
              style={{ display: error ? 'none' : 'block' }}
            />
          )}
        </div>
        <div className="modal-footer-tesla">
          <button
            className="btn-tesla secondary"
            onClick={() => window.open(viewUrl, '_blank')}
          >
            Abrir en nueva pestaña
          </button>
          <button
            className="btn-tesla primary"
            onClick={onClose}
          >
            Cerrar
          </button>
        </div>
      </div>
    </div>
  );
}
