import { useState, useEffect } from 'react';
import styles from './ModalCrearFactura.module.css';
import FileUploadDropzone from './FileUploadDropzone';

export default function ModalEditarFactura({ factura, onClose, onActualizar }) {
  const [formData, setFormData] = useState({
    razon_social: '',
    proveedor_nombre: '',
    nro_proforma: '',
    link_proforma: '',
    logistica: '',
    prioridad: '',
    nro_factura: '',
    link_factura: '',
    forma_pago: '',
    plazo: '',
    tipo_cambio: '',
  });

  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  // Cargar datos de la factura al montar el componente
  useEffect(() => {
    if (factura) {
      setFormData({
        razon_social: factura.razon_social || 'Grupo Gauss',
        proveedor_nombre: factura.proveedor_nombre || '',
        nro_proforma: factura.nro_proforma || '',
        link_proforma: factura.link_proforma || '',
        logistica: factura.logistica || 'GAUSS',
        prioridad: factura.prioridad || 'NORMAL',
        nro_factura: factura.nro_factura || '',
        link_factura: factura.link_factura || '',
        forma_pago: factura.forma_pago || 'CONTADO',
        plazo: factura.plazo || '',
        tipo_cambio: factura.tipo_cambio || '',
      });
    }
  }, [factura]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Limpiar error del campo cuando el usuario empieza a escribir
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: null
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    e.stopPropagation();

    setLoading(true);

    try {
      await onActualizar(factura.id, formData);
    } catch (error) {
      console.error('Error en handleSubmit:', error);
      // El error ya se maneja en el componente padre
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay-tesla">
      <div className="modal-tesla lg" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header-tesla">
          <h2 className="modal-title-tesla">Editar Factura #{factura?.id}</h2>
          <button
            className="btn-close-tesla"
            onClick={onClose}
            disabled={loading}
            type="button"
          >
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={`modal-body-tesla ${styles.formBody}`}>
            {/* Razón Social */}
            <div className={styles.formGroup}>
              <label className={styles.label}>
                Razón Social <span className={styles.required}>*</span>
              </label>
              <select
                name="razon_social"
                value={formData.razon_social}
                onChange={handleChange}
                className={styles.select}
              >
                <option value="Grupo Gauss">Grupo Gauss</option>
                <option value="Pastoriza">Pastoriza</option>
              </select>
            </div>

            {/* Proveedor */}
            <div className={styles.formGroup}>
              <label className={styles.label}>
                Proveedor <span className={styles.required}>*</span>
              </label>
              <input
                type="text"
                name="proveedor_nombre"
                value={formData.proveedor_nombre}
                onChange={handleChange}
                className={styles.input}
                placeholder="Nombre del proveedor"
              />
              {errors.proveedor_nombre && (
                <span className={styles.error}>{errors.proveedor_nombre}</span>
              )}
            </div>

            {/* Nro Proforma */}
            <div className={styles.formGroup}>
              <label className={styles.label}>
                Nro Proforma <span className={styles.required}>*</span>
              </label>
              <input
                type="text"
                name="nro_proforma"
                value={formData.nro_proforma}
                onChange={handleChange}
                className={styles.input}
                placeholder="Número de proforma"
              />
              {errors.nro_proforma && (
                <span className={styles.error}>{errors.nro_proforma}</span>
              )}
            </div>

            {/* Link Proforma */}
            <div className={styles.formGroup}>
              <label className={styles.label}>
                Link Proforma <span className={styles.required}>*</span>
              </label>
              <FileUploadDropzone
                value={formData.link_proforma}
                onChange={(url) => {
                  setFormData(prev => ({ ...prev, link_proforma: url }));
                  if (errors.link_proforma) {
                    setErrors(prev => ({ ...prev, link_proforma: null }));
                  }
                }}
                folder="Facturas"
                accept="application/pdf,image/*"
                maxSizeMB={10}
              />
              {errors.link_proforma && (
                <span className={styles.error}>{errors.link_proforma}</span>
              )}
            </div>

            {/* Logística */}
            <div className={styles.formGroup}>
              <label className={styles.label}>
                Logística <span className={styles.required}>*</span>
              </label>
              <select
                name="logistica"
                value={formData.logistica}
                onChange={handleChange}
                className={styles.select}
              >
                <option value="GAUSS">GAUSS</option>
                <option value="PROVEEDOR">PROVEEDOR</option>
                <option value="TERCERO">TERCERO</option>
              </select>
            </div>

            {/* Prioridad */}
            <div className={styles.formGroup}>
              <label className={styles.label}>
                Prioridad <span className={styles.required}>*</span>
              </label>
              <select
                name="prioridad"
                value={formData.prioridad}
                onChange={handleChange}
                className={styles.select}
              >
                <option value="NORMAL">NORMAL</option>
                <option value="URGENTE">URGENTE</option>
              </select>
            </div>

            {/* Nro Factura */}
            <div className={styles.formGroup}>
              <label className={styles.label}>
                Nro Factura <span className={styles.required}>*</span>
              </label>
              <input
                type="text"
                name="nro_factura"
                value={formData.nro_factura}
                onChange={handleChange}
                className={styles.input}
                placeholder="Número de factura"
              />
              {errors.nro_factura && (
                <span className={styles.error}>{errors.nro_factura}</span>
              )}
            </div>

            {/* Link Factura */}
            <div className={styles.formGroup}>
              <label className={styles.label}>
                Link Factura <span className={styles.required}>*</span>
              </label>
              <FileUploadDropzone
                value={formData.link_factura}
                onChange={(url) => {
                  setFormData(prev => ({ ...prev, link_factura: url }));
                  if (errors.link_factura) {
                    setErrors(prev => ({ ...prev, link_factura: null }));
                  }
                }}
                folder="Facturas"
                accept="application/pdf,image/*"
                maxSizeMB={10}
              />
              {errors.link_factura && (
                <span className={styles.error}>{errors.link_factura}</span>
              )}
            </div>

            {/* Forma de Pago */}
            <div className={styles.formGroup}>
              <label className={styles.label}>
                Forma de Pago <span className={styles.required}>*</span>
              </label>
              <select
                name="forma_pago"
                value={formData.forma_pago}
                onChange={handleChange}
                className={styles.select}
              >
                <option value="CONTADO">CONTADO</option>
                <option value="CHEQUE">CHEQUE</option>
                <option value="CTA CTE">CTA CTE</option>
              </select>
            </div>

            {/* Plazo */}
            <div className={styles.formGroup}>
              <label className={styles.label}>Plazo</label>
              <input
                type="text"
                name="plazo"
                value={formData.plazo}
                onChange={handleChange}
                className={styles.input}
                placeholder="Ej: 30 días"
              />
            </div>

            {/* Tipo de Cambio */}
            <div className={styles.formGroup}>
              <label className={styles.label}>Tipo de Cambio</label>
              <input
                type="text"
                name="tipo_cambio"
                value={formData.tipo_cambio}
                onChange={handleChange}
                className={styles.input}
                placeholder="Ej: 1480 - 3%"
              />
            </div>
          </div>

          <div className="modal-footer-tesla">
            <button
              type="button"
              className="btn-tesla secondary"
              onClick={onClose}
              disabled={loading}
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="btn-tesla primary"
              disabled={loading}
            >
              {loading ? 'Guardando...' : 'Guardar Cambios'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
