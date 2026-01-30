import { useState } from 'react';
import styles from './ModalCrearFactura.module.css';
import FileUploadDropzone from './FileUploadDropzone';

export default function ModalCrearFactura({ onClose, onCrear }) {
  const [formData, setFormData] = useState({
    razon_social: 'Grupo Gauss',
    proveedor_nombre: '',
    nro_proforma: '',
    link_proforma: '',
    logistica: 'GAUSS',
    prioridad: 'NORMAL',
    nro_factura: '',
    link_factura: '',
    forma_pago: 'CONTADO',
    plazo: '',
    tipo_cambio: '',
    observaciones: '',
    iniciado: true
  });

  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

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

  const validateForm = () => {
    // Solo validar campos obligatorios si se va a iniciar el proceso
    if (!formData.iniciado) {
      // Si es borrador, no validar nada
      setErrors({});
      return true;
    }

    const newErrors = {};

    // Campos obligatorios para iniciar proceso
    if (!formData.razon_social?.trim()) {
      newErrors.razon_social = 'La razón social es requerida';
    }

    if (!formData.proveedor_nombre?.trim()) {
      newErrors.proveedor_nombre = 'El proveedor es requerido';
    }

    // Validar que haya al menos un documento completo (proforma o factura)
    const tieneProforma = formData.nro_proforma?.trim() && formData.link_proforma?.trim();
    const tieneFactura = formData.nro_factura?.trim() && formData.link_factura?.trim();
    
    if (!tieneProforma && !tieneFactura) {
      newErrors.nro_proforma = 'Debe cargar al menos un documento (proforma o factura)';
      newErrors.nro_factura = 'Debe cargar al menos un documento (proforma o factura)';
    } else {
      // Si tiene proforma, validar que tenga número y link
      if (formData.nro_proforma?.trim() && !formData.link_proforma?.trim()) {
        newErrors.link_proforma = 'El link de proforma es requerido si se especifica el número';
      }
      if (formData.link_proforma?.trim() && !formData.nro_proforma?.trim()) {
        newErrors.nro_proforma = 'El número de proforma es requerido si se especifica el link';
      }
      
      // Si tiene factura, validar que tenga número y link
      if (formData.nro_factura?.trim() && !formData.link_factura?.trim()) {
        newErrors.link_factura = 'El link de factura es requerido si se especifica el número';
      }
      if (formData.link_factura?.trim() && !formData.nro_factura?.trim()) {
        newErrors.nro_factura = 'El número de factura es requerido si se especifica el link';
      }
    }

    if (!formData.logistica) {
      newErrors.logistica = 'La logística es requerida';
    }

    if (!formData.prioridad) {
      newErrors.prioridad = 'La prioridad es requerida';
    }

    if (!formData.forma_pago) {
      newErrors.forma_pago = 'La forma de pago es requerida';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    e.stopPropagation();

    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      // Preparar datos para enviar (excluir observaciones que se manejan por separado)
      const { observaciones, ...datosFactura } = formData;
      
      await onCrear(datosFactura, observaciones);
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
          <h2 className="modal-title-tesla">Nueva Factura de Compra</h2>
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
                Nro Proforma <span className={styles.required} title="Requerido si se carga proforma">*</span>
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
              <small className={styles.helpText}>
                Debe cargar al menos un documento completo (Proforma o Factura)
              </small>
            </div>

            {/* Link Proforma */}
            <div className={styles.formGroup}>
              <label className={styles.label}>
                Link Proforma <span className={styles.required} title="Requerido si se carga proforma">*</span>
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
              <label className={styles.label}>Nro Factura</label>
              <input
                type="text"
                name="nro_factura"
                value={formData.nro_factura}
                onChange={handleChange}
                className={styles.input}
                placeholder="Número de factura"
              />
            </div>

            {/* Link Factura */}
            <div className={styles.formGroup}>
              <label className={styles.label}>Link Factura</label>
              <FileUploadDropzone
                value={formData.link_factura}
                onChange={(url) => {
                  setFormData(prev => ({ ...prev, link_factura: url }));
                }}
                folder="Facturas"
                accept="application/pdf,image/*"
                maxSizeMB={10}
              />
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
              <label className={styles.label}>
                Tipo de Cambio <span className={styles.required}>*</span>
              </label>
              <input
                type="text"
                name="tipo_cambio"
                value={formData.tipo_cambio}
                onChange={handleChange}
                className={styles.input}
                placeholder="Ej: 1480 - 3%"
              />
              {errors.tipo_cambio && (
                <span className={styles.error}>{errors.tipo_cambio}</span>
              )}
            </div>

            {/* Observaciones */}
            <div className={styles.formGroup}>
              <label className={styles.label}>Observaciones</label>
              <textarea
                name="observaciones"
                value={formData.observaciones}
                onChange={handleChange}
                className={styles.textarea}
                rows="3"
                placeholder="Observaciones iniciales..."
              />
            </div>
          </div>

          <div className="modal-footer-tesla">
            <div className={styles.footerLeft}>
              <label className={styles.checkboxLabel}>
                <input
                  type="checkbox"
                  name="iniciado"
                  checked={formData.iniciado}
                  onChange={(e) =>
                    setFormData(prev => ({
                      ...prev,
                      iniciado: e.target.checked,
                    }))
                  }
                  className={styles.checkbox}
                />
                <span>Iniciar proceso de carga de facturas ahora</span>
              </label>
            </div>
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
              {loading ? 'Guardando...' : 'Crear Factura'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
