import { useState, useEffect, useMemo } from 'react';
import { useDebounce } from '../hooks/useDebounce';
import { useQueryFilters } from '../hooks/useQueryFilters';
import { usePermisos } from '../hooks/usePermisos';
import styles from './FacturasCompras.module.css';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'https://pricing.gaussonline.com.ar';

export default function FacturasCompras() {
  const { tienePermiso } = usePermisos();
  const [facturas, setFacturas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [totalFacturas, setTotalFacturas] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  const [mostrarModalCrear, setMostrarModalCrear] = useState(false);
  const [mostrarModalDetalle, setMostrarModalDetalle] = useState(false);
  const [facturaSeleccionada, setFacturaSeleccionada] = useState(null);

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
    pagado: ''
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

      const response = await axios.get(`${API_URL}/api/facturas-compras?${params}`, {
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

  const handleCrearFactura = async (datosFactura) => {
    try {
      const response = await axios.post(
        `${API_URL}/api/facturas-compras`,
        datosFactura,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        }
      );
      setMostrarModalCrear(false);
      cargarFacturas();
    } catch (error) {
      console.error('Error creando factura:', error);
      alert(error.response?.data?.detail || 'Error al crear factura de compra');
    }
  };

  const handleActualizarFactura = async (facturaId, cambios) => {
    try {
      const response = await axios.patch(
        `${API_URL}/api/facturas-compras/${facturaId}`,
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
    } catch (error) {
      console.error('Error actualizando factura:', error);
      alert(error.response?.data?.detail || 'Error al actualizar factura');
    }
  };

  const handleVerDetalle = async (factura) => {
    try {
      const response = await axios.get(
        `${API_URL}/api/facturas-compras/${factura.id}`,
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
                <th>Nro Factura</th>
                <th>Nro Proforma</th>
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
                      <td>{factura.nro_factura || '-'}</td>
                      <td>{factura.nro_proforma || '-'}</td>
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

      {/* Modal Crear (placeholder - se implementará después) */}
      {mostrarModalCrear && (
        <div className={styles.modalOverlay} onClick={() => setMostrarModalCrear(false)}>
          <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h2>Nueva Factura de Compra</h2>
              <button
                className={styles.btnCerrar}
                onClick={() => setMostrarModalCrear(false)}
              >
                ✕
              </button>
            </div>
            <div className={styles.modalBody}>
              <p>Formulario de creación - Por implementar</p>
            </div>
          </div>
        </div>
      )}

      {/* Modal Detalle (placeholder - se implementará después) */}
      {mostrarModalDetalle && facturaSeleccionada && (
        <div className={styles.modalOverlay} onClick={() => setMostrarModalDetalle(false)}>
          <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h2>Detalle Factura #{facturaSeleccionada.id}</h2>
              <button
                className={styles.btnCerrar}
                onClick={() => setMostrarModalDetalle(false)}
              >
                ✕
              </button>
            </div>
            <div className={styles.modalBody}>
              <p>Detalle y edición - Por implementar</p>
              <pre>{JSON.stringify(facturaSeleccionada, null, 2)}</pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
