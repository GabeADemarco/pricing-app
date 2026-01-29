import { useState, useEffect, useMemo } from 'react';
import { useDebounce } from '../hooks/useDebounce';
import { useQueryFilters } from '../hooks/useQueryFilters';
import { usePermisos } from '../contexts/PermisosContext';
import styles from './FacturasCompras.module.css';
import axios from 'axios';
import ModalCrearFactura from '../components/ModalCrearFactura';
import ModalEditarFactura from '../components/ModalEditarFactura';
import ModalVisualizarDocumento from '../components/ModalVisualizarDocumento';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8002';

export default function FacturasCompras() {
  const { tienePermiso } = usePermisos();
  const [facturas, setFacturas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [totalFacturas, setTotalFacturas] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  const [mostrarModalCrear, setMostrarModalCrear] = useState(false);
  const [mostrarModalDetalle, setMostrarModalDetalle] = useState(false);
  const [mostrarModalEditar, setMostrarModalEditar] = useState(false);
  const [facturaSeleccionada, setFacturaSeleccionada] = useState(null);
  const [facturaAEditar, setFacturaAEditar] = useState(null);

  // Usar query params para filtros
  const { getFilter, updateFilters, searchParams } = useQueryFilters({
    search: '',
    page: 1,
    page_size: 50,
    razon_social: '',
    listo_para_pagar: '',
    oc_cargada: '',
    fc_cargada: '',
    retirado: '',
    controlado: '',
    pagado: '',
    creadas_por_mi: ''
  }, {
    page: 'number',
    page_size: 'number'
  });

  const searchInput = getFilter('search');
  const page = getFilter('page');
  const pageSize = getFilter('page_size');
  const filtroRazonSocial = getFilter('razon_social');
  const filtroListoPagar = getFilter('listo_para_pagar');
  const filtroOcCargada = getFilter('oc_cargada');
  const filtroFcCargada = getFilter('fc_cargada');
  const filtroRetirado = getFilter('retirado');
  const filtroControlado = getFilter('controlado');
  const filtroPagado = getFilter('pagado');
  const filtroCreadasPorMi = getFilter('creadas_por_mi');

  const debouncedSearch = useDebounce(searchInput, 500);

  // Verificar permisos
  const puedeVer = tienePermiso('facturas_compras.ver');
  const puedeCrear = tienePermiso('facturas_compras.crear');
  const puedeEditarCompras = tienePermiso('facturas_compras.editar_campos_compras');
  const puedeMarcarListoPagar = tienePermiso('facturas_compras.marcar_listo_pagar');
  const puedeCargarOc = tienePermiso('facturas_compras.cargar_oc');
  const puedeCargarFc = tienePermiso('facturas_compras.cargar_fc');
  const puedeMarcarRetirado = tienePermiso('facturas_compras.marcar_retirado');
  const puedeMarcarControlado = tienePermiso('facturas_compras.marcar_controlado');
  const puedeMarcarPagado = tienePermiso('facturas_compras.marcar_pagado');
  const puedeAgregarObservacion = tienePermiso('facturas_compras.agregar_observacion');

  // Cargar facturas cuando cambian los filtros
  useEffect(() => {
    if (puedeVer) {
      cargarFacturas();
    }
  }, [page, pageSize, debouncedSearch, filtroRazonSocial, filtroListoPagar, filtroOcCargada, filtroFcCargada, filtroRetirado, filtroControlado, filtroPagado, puedeVer]);

  const cargarFacturas = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: pageSize.toString()
      });

      if (debouncedSearch) params.append('search', debouncedSearch);
      if (filtroRazonSocial) params.append('razon_social', filtroRazonSocial);
      if (filtroListoPagar !== '') params.append('listo_para_pagar', filtroListoPagar);
      if (filtroOcCargada !== '') params.append('oc_cargada', filtroOcCargada);
      if (filtroFcCargada !== '') params.append('fc_cargada', filtroFcCargada);
      if (filtroRetirado !== '') params.append('retirado', filtroRetirado);
      if (filtroControlado !== '') params.append('controlado', filtroControlado);
      if (filtroPagado !== '') params.append('pagado', filtroPagado);
      if (filtroCreadasPorMi === 'true') params.append('creadas_por_mi', 'true');

      const response = await axios.get(`${API_URL}/facturas-compras?${params}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      });
      setFacturas(response.data.facturas);
      setTotalFacturas(response.data.total);
      setTotalPages(response.data.total_pages);
    } catch (error) {
      console.error('Error cargando facturas:', error);
      alert('Error al cargar facturas de compra');
    } finally {
      setLoading(false);
    }
  };

  const handleCrearFactura = async (datosFactura, observacionesIniciales) => {
    try {
      const response = await axios.post(
        `${API_URL}/facturas-compras`,
        datosFactura,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        }
      );
      
      // Si hay observaciones iniciales, agregarlas
      if (observacionesIniciales?.trim()) {
        try {
          await axios.post(
            `${API_URL}/facturas-compras/${response.data.id}/observaciones`,
            { observacion: observacionesIniciales },
            {
              headers: {
                Authorization: `Bearer ${localStorage.getItem('token')}`
              }
            }
          );
        } catch (obsError) {
          console.error('Error agregando observación inicial:', obsError);
          // No bloqueamos la creación si falla la observación
        }
      }
      
      setMostrarModalCrear(false);
      cargarFacturas();
    } catch (error) {
      console.error('Error creando factura:', error);
      alert(error.response?.data?.detail || 'Error al crear factura de compra');
      throw error; // Re-lanzar para que el modal pueda manejar el error
    }
  };

  const handleActualizarFactura = async (facturaId, cambios) => {
    try {
      const response = await axios.patch(
        `${API_URL}/facturas-compras/${facturaId}`,
        cambios,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        }
      );
      cargarFacturas();
      if (facturaSeleccionada?.id === facturaId) {
        setFacturaSeleccionada(response.data);
      }
      if (facturaAEditar?.id === facturaId) {
        setFacturaAEditar(response.data);
      }
      return response.data;
    } catch (error) {
      console.error('Error actualizando factura:', error);
      const mensajeError = error.response?.data?.detail || 'Error al actualizar factura';
      alert(mensajeError);
      throw error; // Re-lanzar para que el componente pueda manejar el error
    }
  };

  const handleEditarFactura = async (facturaId, datos) => {
    try {
      await handleActualizarFactura(facturaId, datos);
      setMostrarModalEditar(false);
      setFacturaAEditar(null);
    } catch (error) {
      // El error ya se muestra en handleActualizarFactura
    }
  };

  const handleIniciarProceso = async (facturaId) => {
    try {
      await handleActualizarFactura(facturaId, { iniciado: true });
    } catch (error) {
      // El error ya se muestra en handleActualizarFactura
      // Si es error de validación, el usuario ya vio el mensaje con los campos faltantes
    }
  };

  const handleEliminarBorrador = async (facturaId) => {
    try {
      await axios.delete(
        `${API_URL}/facturas-compras/${facturaId}`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        }
      );
      cargarFacturas();
    } catch (error) {
      console.error('Error eliminando borrador:', error);
      alert(error.response?.data?.detail || 'Error al eliminar borrador');
    }
  };

  // Función helper para transformar URL de Nextcloud a formato de visualización
  const transformToViewUrl = (url) => {
    if (!url) return null;
    
    // Si es una URL de WebDAV (/remote.php/dav/files/), no podemos visualizarla directamente
    // Estas URLs requieren autenticación y no son públicas
    if (url.includes('/remote.php/dav/files/')) {
      console.error('URL de WebDAV detectada. Esta URL requiere autenticación y no puede visualizarse públicamente.');
      alert('Este documento tiene una URL de acceso directo que requiere autenticación. Por favor, contactá al administrador para regenerar el link público.');
      return null;
    }
    
    // Si la URL ya tiene el formato completo con openfile=true, devolverla tal cual
    if (url.includes('openfile=true')) {
      return url;
    }
    
    // Si es un share URL de Nextcloud (/s/ o /index.php/s/), asegurar formato de visualización
    if (url.includes('/s/')) {
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
        // Si falla el parsing (puede ser URL relativa o mal formada), intentar transformación simple
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

  // Abrir documento en popup
  const abrirDocumentoEnPopup = (url, titulo) => {
    if (!url) {
      alert('No hay documento disponible para visualizar.');
      return;
    }
    
    // Limpiar la URL de espacios y caracteres extraños
    const cleanUrl = url.trim();
    
    const viewUrl = transformToViewUrl(cleanUrl);
    if (!viewUrl) {
      // El error ya se mostró en transformToViewUrl
      return;
    }
    
    // Validar que la URL no esté duplicada (verificar si contiene el patrón duplicado)
    if (viewUrl.includes('/s/https://') || viewUrl.includes('/s/http://')) {
      console.error('URL duplicada detectada:', viewUrl);
      // Intentar extraer solo la parte correcta
      const match = viewUrl.match(/https?:\/\/[^\/]+\/index\.php\/s\/[^?]+(\?.*)?/);
      if (match) {
        const correctedUrl = match[0];
        console.log('URL corregida:', correctedUrl);
        window.open(correctedUrl, `doc_${Date.now()}`, 'width=1200,height=800,scrollbars=yes,resizable=yes,toolbar=no,menubar=no,location=no,status=no');
        return;
      }
    }
    
    // Abrir popup sin barras de navegación pero con scroll y zoom
    // NOTA: Limitación conocida de Nextcloud: a veces el documento no se visualiza correctamente
    // en la primera carga del popup. La solución es cerrar el popup y volver a abrirlo.
    // Este comportamiento también ocurre en el sistema actual de Google Sheets.
    const popup = window.open(
      viewUrl,
      `doc_${Date.now()}`,
      'width=1200,height=800,scrollbars=yes,resizable=yes,toolbar=no,menubar=no,location=no,status=no'
    );
    
    if (!popup) {
      // Si el popup fue bloqueado, abrir en nueva pestaña
      alert('El popup fue bloqueado. Abriendo en nueva pestaña...');
      window.open(viewUrl, '_blank');
    }
  };

  const handleVerDetalle = async (factura) => {
    try {
      const response = await axios.get(
        `${API_URL}/facturas-compras/${factura.id}`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        }
      );
      setFacturaSeleccionada(response.data);
      setMostrarModalDetalle(true);
    } catch (error) {
      console.error('Error cargando detalle:', error);
      alert('Error al cargar detalle de la factura');
    }
  };

  const formatearFecha = (fecha) => {
    if (!fecha) return '-';
    return new Date(fecha).toLocaleDateString('es-AR', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getEstadoBadge = (factura) => {
    if (!factura.iniciado) return { texto: 'En borrador', clase: styles.badgeEnProceso };
    if (factura.pagado) return { texto: 'Pagado', clase: styles.badgePagado };
    if (factura.fc_cargada) return { texto: 'FC Cargada', clase: styles.badgeFcCargada };
    if (factura.oc_cargada) return { texto: 'OC Cargada', clase: styles.badgeOcCargada };
    if (factura.listo_para_pagar) return { texto: 'Listo para Pagar', clase: styles.badgeListoPagar };
    return { texto: 'En Proceso', clase: styles.badgeEnProceso };
  };

  if (!puedeVer) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>
          No tenés permiso para ver facturas de compra
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>Facturas de Compra</h1>
        <div className={styles.headerActions}>
          <span className={styles.totalCount}>
            Total: {totalFacturas.toLocaleString()} facturas
          </span>
          {puedeCrear && (
            <button
              className={styles.btnCrear}
              onClick={() => setMostrarModalCrear(true)}
            >
              ➕ Nueva Factura
            </button>
          )}
        </div>
      </div>

      {/* Filtros */}
      <div className={styles.filtros}>
        <div className={styles.filtrosRow}>
          <input
            type="text"
            placeholder="Buscar por proveedor, nro factura o nro proforma..."
            value={searchInput}
            onChange={(e) => updateFilters({ search: e.target.value, page: 1 })}
            className={styles.searchInput}
          />

          <select
            value={filtroRazonSocial}
            onChange={(e) => updateFilters({ razon_social: e.target.value, page: 1 })}
            className={styles.select}
          >
            <option value="">Todas las razones sociales</option>
            <option value="Grupo Gauss">Grupo Gauss</option>
            <option value="Pastoriza">Pastoriza</option>
          </select>

          <select
            value={filtroListoPagar}
            onChange={(e) => updateFilters({ listo_para_pagar: e.target.value, page: 1 })}
            className={styles.select}
          >
            <option value="">Todos los estados</option>
            <option value="true">Listo para pagar</option>
            <option value="false">No listo</option>
          </select>

          <select
            value={filtroOcCargada}
            onChange={(e) => updateFilters({ oc_cargada: e.target.value, page: 1 })}
            className={styles.select}
          >
            <option value="">OC - Todos</option>
            <option value="true">OC Cargada</option>
            <option value="false">OC Pendiente</option>
          </select>

          <select
            value={filtroFcCargada}
            onChange={(e) => updateFilters({ fc_cargada: e.target.value, page: 1 })}
            className={styles.select}
          >
            <option value="">FC - Todos</option>
            <option value="true">FC Cargada</option>
            <option value="false">FC Pendiente</option>
          </select>
        </div>

        <div className={styles.filtrosRow}>
          <select
            value={filtroRetirado}
            onChange={(e) => updateFilters({ retirado: e.target.value, page: 1 })}
            className={styles.select}
          >
            <option value="">Retirado - Todos</option>
            <option value="true">Retirado</option>
            <option value="false">No Retirado</option>
          </select>

          <select
            value={filtroControlado}
            onChange={(e) => updateFilters({ controlado: e.target.value, page: 1 })}
            className={styles.select}
          >
            <option value="">Controlado - Todos</option>
            <option value="true">Controlado</option>
            <option value="false">No Controlado</option>
          </select>

          <select
            value={filtroPagado}
            onChange={(e) => updateFilters({ pagado: e.target.value, page: 1 })}
            className={styles.select}
          >
            <option value="">Pago - Todos</option>
            <option value="true">Pagado</option>
            <option value="false">No Pagado</option>
          </select>

          <select
            value={filtroCreadasPorMi}
            onChange={(e) => updateFilters({ creadas_por_mi: e.target.value, page: 1 })}
            className={styles.select}
          >
            <option value="">Creadas por - Todas</option>
            <option value="true">Solo creadas por mí</option>
          </select>

          <button
            className={styles.btnLimpiar}
            onClick={() => updateFilters({
              search: '',
              razon_social: '',
              listo_para_pagar: '',
              oc_cargada: '',
              fc_cargada: '',
              retirado: '',
              controlado: '',
              pagado: '',
              creadas_por_mi: '',
              page: 1
            })}
          >
            Limpiar Filtros
          </button>
        </div>
      </div>

      {/* Tabla */}
      {loading ? (
        <div className={styles.loading}>Cargando facturas...</div>
      ) : (
        <div className={styles.tableContainer}>
          <table className={styles.table}>
            <thead>
              <tr>
                <th>ID</th>
                <th>Razón Social</th>
                <th>Proveedor</th>
                <th>Creada por</th>
                <th>Nro Proforma</th>
                <th>Nro Factura</th>
                <th>Fecha Carga</th>
                <th>Estado</th>
                <th>OC</th>
                <th>FC</th>
                <th>Retirado</th>
                <th>Controlado</th>
                <th>Pagado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {facturas.length === 0 ? (
                <tr>
                  <td colSpan="13" className={styles.empty}>
                    No se encontraron facturas
                  </td>
                </tr>
              ) : (
                facturas.map((factura) => {
                  const estado = getEstadoBadge(factura);
                  return (
                    <tr key={factura.id}>
                      <td>{factura.id}</td>
                      <td>{factura.razon_social}</td>
                      <td>{factura.proveedor_nombre || '-'}</td>
                      <td>{factura.creado_por_nombre || '-'}</td>
                      <td>
                        {factura.nro_proforma ? (
                          <button
                            className={styles.linkClickable}
                            onClick={() => {
                              if (factura.link_proforma) {
                                abrirDocumentoEnPopup(factura.link_proforma, `Proforma ${factura.nro_proforma}`);
                              }
                            }}
                            disabled={!factura.link_proforma}
                            title={factura.link_proforma ? 'Ver documento en popup' : 'Sin documento'}
                          >
                            {factura.nro_proforma}
                          </button>
                        ) : (
                          '-'
                        )}
                      </td>
                      <td>
                        {factura.nro_factura ? (
                          <button
                            className={styles.linkClickable}
                            onClick={() => {
                              if (factura.link_factura) {
                                abrirDocumentoEnPopup(factura.link_factura, `Factura ${factura.nro_factura}`);
                              }
                            }}
                            disabled={!factura.link_factura}
                            title={factura.link_factura ? 'Ver documento en popup' : 'Sin documento'}
                          >
                            {factura.nro_factura}
                          </button>
                        ) : (
                          '-'
                        )}
                      </td>
                      <td>{formatearFecha(factura.fecha_carga)}</td>
                      <td>
                        <span className={estado.clase}>{estado.texto}</span>
                      </td>
                      <td>
                        {factura.oc_cargada ? (
                          <span className={styles.badgeSi}>✓ {formatearFecha(factura.oc_fecha)}</span>
                        ) : (
                          <span className={styles.badgeNo}>✗</span>
                        )}
                      </td>
                      <td>
                        {factura.fc_cargada ? (
                          <span className={styles.badgeSi}>✓ {formatearFecha(factura.fc_fecha)}</span>
                        ) : (
                          <span className={styles.badgeNo}>✗</span>
                        )}
                      </td>
                      <td>
                        {factura.retirado ? (
                          <span className={styles.badgeSi}>✓ {formatearFecha(factura.retirado_fecha)}</span>
                        ) : (
                          <span className={styles.badgeNo}>✗</span>
                        )}
                      </td>
                      <td>
                        {factura.controlado ? (
                          <span className={styles.badgeSi}>✓ {formatearFecha(factura.controlado_fecha)}</span>
                        ) : (
                          <span className={styles.badgeNo}>✗</span>
                        )}
                      </td>
                      <td>
                        {factura.pagado ? (
                          <span className={styles.badgeSi}>✓ {formatearFecha(factura.pagado_fecha)}</span>
                        ) : (
                          <span className={styles.badgeNo}>✗</span>
                        )}
                      </td>
                      <td>
                        <button
                          className={styles.btnVer}
                          onClick={() => handleVerDetalle(factura)}
                        >
                          Ver
                        </button>
                        {!factura.iniciado && puedeEditarCompras && (
                          <>
                            <button
                              className={styles.btnSecundario}
                              onClick={() => {
                                setFacturaAEditar(factura);
                                setMostrarModalEditar(true);
                              }}
                            >
                              Editar
                            </button>
                            <button
                              className={styles.btnSecundario}
                              onClick={() => {
                                if (!window.confirm('¿Iniciar el proceso de esta factura? Los demás roles podrán verla.')) return;
                                handleIniciarProceso(factura.id);
                              }}
                            >
                              Iniciar proceso
                            </button>
                            <button
                              className={styles.btnPeligro}
                              onClick={() => {
                                if (!window.confirm('¿Eliminar este borrador de factura? Esta acción no se puede deshacer.')) return;
                                handleEliminarBorrador(factura.id);
                              }}
                            >
                              Eliminar borrador
                            </button>
                          </>
                        )}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* Paginación */}
      {totalPages > 1 && (
        <div className={styles.pagination}>
          <button
            className={styles.btnPagination}
            onClick={() => updateFilters({ page: page - 1 })}
            disabled={page === 1}
          >
            ← Anterior
          </button>
          <span className={styles.pageInfo}>
            Página {page} de {totalPages}
          </span>
          <button
            className={styles.btnPagination}
            onClick={() => updateFilters({ page: page + 1 })}
            disabled={page === totalPages}
          >
            Siguiente →
          </button>
        </div>
      )}

      {/* Modal Crear */}
      {mostrarModalCrear && (
        <ModalCrearFactura
          onClose={() => setMostrarModalCrear(false)}
          onCrear={handleCrearFactura}
        />
      )}

      {/* Modal Editar */}
      {mostrarModalEditar && facturaAEditar && (
        <ModalEditarFactura
          factura={facturaAEditar}
          onClose={() => {
            setMostrarModalEditar(false);
            setFacturaAEditar(null);
          }}
          onActualizar={handleEditarFactura}
        />
      )}

      {/* Modal Detalle */}
      {mostrarModalDetalle && facturaSeleccionada && (
        <div className="modal-overlay-tesla" onClick={() => setMostrarModalDetalle(false)}>
          <div className="modal-tesla lg" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header-tesla">
              <h2 className="modal-title-tesla">Detalle Factura #{facturaSeleccionada.id}</h2>
              <button
                className="btn-close-tesla"
                onClick={() => setMostrarModalDetalle(false)}
                type="button"
              >
                ✕
              </button>
            </div>
            <div className="modal-body-tesla">
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.5rem' }}>
                <div>
                  <strong>Razón Social:</strong> {facturaSeleccionada.razon_social}
                </div>
                <div>
                  <strong>Proveedor:</strong> {facturaSeleccionada.proveedor_nombre || '-'}
                </div>
                <div>
                  <strong>Nro Proforma:</strong> {facturaSeleccionada.nro_proforma || '-'}
                </div>
                <div>
                  <strong>Nro Factura:</strong> {facturaSeleccionada.nro_factura || '-'}
                </div>
                <div>
                  <strong>Logística:</strong> {facturaSeleccionada.logistica || '-'}
                </div>
                <div>
                  <strong>Prioridad:</strong> {facturaSeleccionada.prioridad || '-'}
                </div>
                <div>
                  <strong>Forma de Pago:</strong> {facturaSeleccionada.forma_pago || '-'}
                </div>
                <div>
                  <strong>Plazo:</strong> {facturaSeleccionada.plazo || '-'}
                </div>
                <div>
                  <strong>Tipo de Cambio:</strong> {facturaSeleccionada.tipo_cambio || '-'}
                </div>
                <div>
                  <strong>Estado:</strong> {facturaSeleccionada.iniciado ? 'En Proceso' : 'En Borrador'}
                </div>
              </div>

              {/* Sección Documentos */}
              {(facturaSeleccionada.link_proforma || facturaSeleccionada.link_factura) && (
                <div style={{ marginTop: '2rem', paddingTop: '1.5rem', borderTop: '1px solid var(--border-color)' }}>
                  <h3 style={{ marginBottom: '1rem', color: 'var(--text-primary)' }}>Documentos</h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    {facturaSeleccionada.link_proforma && (
                      <div>
                        <strong>Proforma:</strong>
                        <div style={{ marginTop: '0.5rem', display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                          <a
                            href={facturaSeleccionada.link_proforma}
                            target="_blank"
                            rel="noopener noreferrer"
                            style={{
                              color: 'var(--accent-color)',
                              textDecoration: 'underline',
                              wordBreak: 'break-all'
                            }}
                          >
                            {facturaSeleccionada.link_proforma}
                          </a>
                          <button
                            className="btn-tesla small"
                            onClick={() => abrirDocumentoEnPopup(facturaSeleccionada.link_proforma, 'Proforma')}
                          >
                            Ver en popup
                          </button>
                        </div>
                      </div>
                    )}
                    {facturaSeleccionada.link_factura && (
                      <div>
                        <strong>Factura:</strong>
                        <div style={{ marginTop: '0.5rem', display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                          <a
                            href={facturaSeleccionada.link_factura}
                            target="_blank"
                            rel="noopener noreferrer"
                            style={{
                              color: 'var(--accent-color)',
                              textDecoration: 'underline',
                              wordBreak: 'break-all'
                            }}
                          >
                            {facturaSeleccionada.link_factura}
                          </a>
                          <button
                            className="btn-tesla small"
                            onClick={() => abrirDocumentoEnPopup(facturaSeleccionada.link_factura, 'Factura')}
                          >
                            Ver en popup
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
            <div className="modal-footer-tesla">
              <button
                className="btn-tesla secondary"
                onClick={() => setMostrarModalDetalle(false)}
              >
                Cerrar
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal Visualizar Documento - Ya no se usa, se abren popups directamente */}
    </div>
  );
}
