# 📋 Sistema de Carga de Facturas de Compra

Sistema para gestionar el proceso completo de carga de facturas de compra, desde la carga inicial hasta el pago, con roles específicos y control de permisos granular.

## 📋 Requisitos

- Python 3.11+
- PostgreSQL 14+
- FastAPI (ya instalado)
- SQLAlchemy (ya instalado)
- React + Vite (frontend)

---

## 🚀 Instalación

### 1. Aplicar Migraciones de Base de Datos

El sistema requiere dos migraciones:

#### Migración 1: Crear Tablas (`7c95ca8072fc`)

Crea las tablas principales del sistema:
- `facturas_compras` - Tabla principal con todos los campos del proceso
- `facturas_compras_observaciones` - Historial de observaciones por rol

**Aplicar migración:**
```bash
cd backend
# Con el entorno virtual activado
alembic upgrade head
```

Esta migración crea:
- Tabla `facturas_compras` con todos los campos necesarios
- Tabla `facturas_compras_observaciones` para historial de observaciones
- ENUMs de PostgreSQL: `razonsocial`, `logistica`, `prioridad`, `formapago`

#### Migración 2: Crear Roles y Permisos (`0e4585fa9ede`)

Crea los roles y permisos del sistema:
- Roles: `COMPRAS`, `CARGA_OC_FC_GBP`, `DEPO`, `TESORERIA`
- Permisos: Todos los `facturas_compras.*`

**Aplicar migración:**
```bash
# La migración se aplica automáticamente con alembic upgrade head
# Si ya aplicaste la primera, solo necesitas ejecutar:
alembic upgrade head
```

Esta migración:
- Inserta 11 permisos nuevos en la tabla `permisos`
- Crea 4 roles nuevos en la tabla `roles`
- Asigna permisos a cada rol según su función

### 2. Verificar Migraciones

```bash
# Ver estado actual
alembic current

# Ver historial
alembic history

# Deberías ver ambas migraciones aplicadas
```

### 3. Reiniciar Backend

```bash
# En desarrollo
uvicorn app.main:app --reload --host 0.0.0.0 --port 8002

# En producción
sudo systemctl restart pricing-api
```

---

## 📊 Estructura de Base de Datos

### Tabla: `facturas_compras`

Tabla principal que contiene todos los campos del proceso.

#### Campos de COMPRAS (carga inicial)
- `razon_social` (ENUM) - "Grupo Gauss" o "Pastoriza"
- `fecha_carga` (DateTime) - Fecha automática de creación
- `proveedor_id` (Integer) - FK al ERP (nullable hasta integrar)
- `proveedor_nombre` (String) - Nombre del proveedor (cache)
- `nro_proforma` (String) - Número de proforma
- `link_proforma` (String) - URL al cloud storage
- `logistica` (ENUM) - "GAUSS", "PROVEEDOR", "TERCERO"
- `prioridad` (ENUM) - "NORMAL", "URGENTE" (default: NORMAL)
- `nro_factura` (String) - Número de factura
- `link_factura` (String) - URL al cloud storage
- `forma_pago` (ENUM) - "CONTADO", "CHEQUE", "CTA CTE"
- `plazo` (String) - Texto libre
- `tipo_cambio` (String) - Ej: "1480 - 3%"
- `listo_para_pagar` (Boolean) - Trigger para iniciar proceso

#### Campos de CARGA_OC_FC_GBP
- `oc_cargada` (Boolean) - Si la OC fue cargada en GBP
- `oc_fecha` (DateTime) - Fecha automática al marcar como cargada
- `fc_cargada` (Boolean) - Si la FC fue cargada en GBP
- `fc_fecha` (DateTime) - Fecha automática al marcar como cargada
- `tiene_devoluciones` (Boolean) - Si hay devoluciones
- `rma_id` (String) - ID de RMA si aplica

#### Campos de DEPO
- `retirado` (Boolean) - Si fue retirado/recibido
- `retirado_fecha` (DateTime) - Fecha automática al marcar como retirado
- `controlado` (Boolean) - Si fue controlado físicamente
- `controlado_fecha` (DateTime) - Fecha automática al marcar como controlado

#### Campos de TESORERIA
- `pagado` (Boolean) - Si fue pagado
- `pagado_fecha` (DateTime) - Fecha automática al marcar como pagado

#### Auditoría
- `created_at` (DateTime) - Fecha de creación
- `updated_at` (DateTime) - Última actualización
- `creado_por_id` (Integer) - FK a usuarios

### Tabla: `facturas_compras_observaciones`

Historial de observaciones con registro de quién escribió qué.

**Campos:**
- `id` (PK)
- `factura_compra_id` (FK) - Referencia a factura
- `rol_codigo` (String) - Rol que escribió (COMPRAS, CARGA_OC_FC_GBP, DEPO, TESORERIA)
- `usuario_id` (FK) - Usuario que escribió (opcional, para auditoría)
- `observacion` (Text) - Contenido de la observación
- `created_at` (DateTime) - Timestamp

---

## 🔐 Roles y Permisos

### Roles del Sistema

#### COMPRAS
**Descripción:** Rol para carga inicial de facturas de compra.

**Permisos:**
- `facturas_compras.ver` - Ver facturas
- `facturas_compras.crear` - Crear nuevas facturas
- `facturas_compras.editar_campos_compras` - Editar campos iniciales
- `facturas_compras.marcar_listo_pagar` - Marcar como listo para pagar
- `facturas_compras.agregar_observacion` - Agregar observaciones
- `facturas_compras.ver_observaciones` - Ver observaciones

#### CARGA_OC_FC_GBP
**Descripción:** Rol para cargar Orden de Compra y Factura en el sistema GBP/ERP.

**Permisos:**
- `facturas_compras.ver` - Ver facturas
- `facturas_compras.cargar_oc` - Cargar OC en GBP
- `facturas_compras.cargar_fc` - Cargar FC en GBP
- `facturas_compras.agregar_observacion` - Agregar observaciones
- `facturas_compras.ver_observaciones` - Ver observaciones

#### DEPO
**Descripción:** Rol para retiro y control físico de facturas de compra.

**Permisos:**
- `facturas_compras.ver` - Ver facturas
- `facturas_compras.marcar_retirado` - Marcar como retirado
- `facturas_compras.marcar_controlado` - Marcar como controlado
- `facturas_compras.agregar_observacion` - Agregar observaciones
- `facturas_compras.ver_observaciones` - Ver observaciones

#### TESORERIA
**Descripción:** Rol del área de Administración y Tesorería para marcar pagos.

**Permisos:**
- `facturas_compras.ver` - Ver facturas
- `facturas_compras.marcar_pagado` - Marcar como pagado
- `facturas_compras.agregar_observacion` - Agregar observaciones
- `facturas_compras.ver_observaciones` - Ver observaciones

### Permisos Disponibles

Todos los permisos están bajo la categoría `facturas_compras`:

- `facturas_compras.ver` - Ver facturas de compra
- `facturas_compras.crear` - Crear factura de compra
- `facturas_compras.editar_campos_compras` - Editar campos de COMPRAS
- `facturas_compras.marcar_listo_pagar` - Marcar listo para pagar
- `facturas_compras.cargar_oc` - Cargar OC en GBP
- `facturas_compras.cargar_fc` - Cargar FC en GBP
- `facturas_compras.marcar_retirado` - Marcar como retirado
- `facturas_compras.marcar_controlado` - Marcar como controlado
- `facturas_compras.marcar_pagado` - Marcar como pagado
- `facturas_compras.agregar_observacion` - Agregar observación
- `facturas_compras.ver_observaciones` - Ver observaciones

**Nota:** El rol `ADMIN` del sistema (administrador general) tiene acceso completo mediante `facturas_compras.*`.

---

## 📚 API Endpoints

### Facturas de Compra

#### `GET /api/facturas-compras`
Lista facturas con filtros y paginación.

**Query params:**
- `page` (int, default: 1) - Número de página
- `page_size` (int, default: 50, max: 1000) - Registros por página
- `razon_social` (enum) - Filtrar por razón social
- `listo_para_pagar` (bool) - Filtrar por listo para pagar
- `oc_cargada` (bool) - Filtrar por OC cargada
- `fc_cargada` (bool) - Filtrar por FC cargada
- `retirado` (bool) - Filtrar por retirado
- `controlado` (bool) - Filtrar por controlado
- `pagado` (bool) - Filtrar por pagado
- `search` (string) - Buscar por proveedor, nro factura o nro proforma

**Requiere permiso:** `facturas_compras.ver`

**Response:**
```json
{
  "total": 100,
  "page": 1,
  "page_size": 50,
  "total_pages": 2,
  "facturas": [
    {
      "id": 1,
      "razon_social": "Grupo Gauss",
      "fecha_carga": "2025-01-27T10:00:00Z",
      "proveedor_nombre": "Proveedor XYZ",
      "nro_factura": "FC-001",
      "listo_para_pagar": true,
      "oc_cargada": true,
      "fc_cargada": false,
      "retirado": false,
      "controlado": false,
      "pagado": false,
      ...
    }
  ]
}
```

#### `GET /api/facturas-compras/{id}`
Obtiene una factura específica por ID.

**Requiere permiso:** `facturas_compras.ver`

#### `POST /api/facturas-compras`
Crea una nueva factura de compra.

**Requiere permiso:** `facturas_compras.crear`

**Request body:**
```json
{
  "razon_social": "Grupo Gauss",
  "proveedor_id": 123,
  "proveedor_nombre": "Proveedor XYZ",
  "nro_proforma": "PROF-001",
  "link_proforma": "https://cloud.../proforma.pdf",
  "logistica": "GAUSS",
  "prioridad": "NORMAL",
  "nro_factura": "FC-001",
  "link_factura": "https://cloud.../factura.pdf",
  "forma_pago": "CONTADO",
  "plazo": "30 días",
  "tipo_cambio": "1480 - 3%"
}
```

#### `PATCH /api/facturas-compras/{id}`
Actualiza una factura de compra.

**Validaciones automáticas:**
- FC solo se puede cargar si está retirado (validación hard)
- Controlado puede hacerse sin OC (solo aviso, no bloquea)
- Fechas se establecen automáticamente al marcar estados

**Requiere permisos específicos según el campo:**
- Campos COMPRAS: `facturas_compras.editar_campos_compras`
- Marcar listo para pagar: `facturas_compras.marcar_listo_pagar`
- Cargar OC: `facturas_compras.cargar_oc`
- Cargar FC: `facturas_compras.cargar_fc`
- Marcar retirado: `facturas_compras.marcar_retirado`
- Marcar controlado: `facturas_compras.marcar_controlado`
- Marcar pagado: `facturas_compras.marcar_pagado`

**Request body (parcial):**
```json
{
  "listo_para_pagar": true,
  "oc_cargada": true,
  "fc_cargada": true,
  "retirado": true,
  "controlado": true,
  "pagado": true
}
```

#### `GET /api/facturas-compras/{id}/observaciones`
Lista las observaciones de una factura.

**Requiere permiso:** `facturas_compras.ver_observaciones`

**Response:**
```json
[
  {
    "id": 1,
    "factura_compra_id": 1,
    "rol_codigo": "COMPRAS",
    "usuario_id": 5,
    "observacion": "Factura pendiente de revisión",
    "created_at": "2025-01-27T10:00:00Z"
  }
]
```

#### `POST /api/facturas-compras/{id}/observaciones`
Agrega una observación a una factura.

**Requiere permiso:** `facturas_compras.agregar_observacion`

**Request body:**
```json
{
  "observacion": "Factura pendiente de revisión"
}
```

---

## 🎨 Frontend

### Página Principal

**Ruta:** `/facturas-compras`

**Componente:** `frontend/src/pages/FacturasCompras.jsx`

**Características:**
- Tabla con todas las facturas
- Filtros por razón social, estados (listo para pagar, OC, FC, retirado, controlado, pagado)
- Búsqueda por proveedor, nro factura o nro proforma
- Paginación server-side
- Badges de estado con colores
- Botón "Nueva Factura" (solo si tiene permiso)
- Modal de detalle (placeholder, por implementar)
- Modal de creación (placeholder, por implementar)

**Permisos requeridos:**
- `facturas_compras.ver` - Para ver la página

### Estilos

**Archivo:** `frontend/src/pages/FacturasCompras.module.css`

Usa design tokens de Tesla Design System:
- `var(--color-bg)`, `var(--color-text)`
- `var(--color-primary)`, `var(--color-border)`
- Soporte completo para dark mode

---

## 🔄 Flujo del Proceso

### 1. COMPRAS - Carga Inicial
1. Usuario con rol `COMPRAS` crea nueva factura
2. Completa todos los campos iniciales:
   - Razón social, proveedor, proforma, factura
   - Logística, prioridad, forma de pago, etc.
3. Marca "Listo para pagar" → Inicia el proceso

### 2. CARGA_OC_FC_GBP - Carga de Documentos
1. Usuario con rol `CARGA_OC_FC_GBP` ve facturas listas para pagar
2. Carga OC en el sistema GBP/ERP → Se marca `oc_cargada = true`, fecha automática
3. Espera a que DEPO marque como retirado
4. Carga FC en el sistema GBP/ERP → Se marca `fc_cargada = true`, fecha automática
   - **Validación:** FC solo se puede cargar si `retirado = true`

### 3. DEPO - Retiro y Control
1. Usuario con rol `DEPO` ve facturas pendientes
2. Marca como retirado → `retirado = true`, fecha automática
3. Controla físicamente → `controlado = true`, fecha automática
   - **Aviso (no bloqueo):** Si no hay OC cargada, se muestra aviso pero permite controlar

### 4. TESORERIA - Pago
1. Usuario con rol `TESORERIA` ve facturas listas para pagar
2. Realiza el pago
3. Marca como pagado → `pagado = true`, fecha automática

### Observaciones (Todos los Roles)
- Cualquier rol puede agregar observaciones en cualquier momento
- Las observaciones se guardan con el código del rol y el usuario
- Todos los roles pueden ver todas las observaciones

---

## ✅ Validaciones de Negocio

### Validaciones Hard (Bloquean la acción)

1. **FC solo si está retirado:**
   - No se puede cargar FC (`fc_cargada = true`) sin que `retirado = true`
   - Error 400 si se intenta

### Validaciones Soft (Avisan pero no bloquean)

1. **Controlar sin OC:**
   - Se puede controlar sin OC cargada
   - Se muestra aviso pero no bloquea la acción
   - Implementado para no trabar el proceso si falta la OC

---

## 📁 Estructura de Archivos

### Backend

```
backend/
├── app/
│   ├── models/
│   │   └── factura_compra.py          # Modelos SQLAlchemy
│   ├── api/
│   │   └── endpoints/
│   │       └── facturas_compras.py    # Endpoints FastAPI
│   └── main.py                         # Router agregado
├── alembic/
│   └── versions/
│       ├── 7c95ca8072fc_crear_sistema_compras.py
│       └── 0e4585fa9ede_agregar_roles_y_permisos_facturas_.py
```

### Frontend

```
frontend/src/
├── pages/
│   ├── FacturasCompras.jsx            # Componente principal
│   └── FacturasCompras.module.css     # Estilos
└── App.jsx                             # Ruta agregada
```

---

## 🧪 Testing Manual

### Checklist de Pruebas

**Backend:**
- [ ] Endpoints responden correctamente
- [ ] Validaciones de permisos funcionan
- [ ] Validación hard: FC solo si retirado
- [ ] Fechas se establecen automáticamente
- [ ] Observaciones se guardan correctamente

**Frontend:**
- [ ] Página carga sin errores
- [ ] Filtros funcionan correctamente
- [ ] Paginación funciona
- [ ] Badges de estado se muestran correctamente
- [ ] Permisos ocultan/muestran botones según rol

---

## 🚀 Próximos Pasos (Post-MVP)

1. **Modal de Creación Completo**
   - Formulario con todos los campos
   - Validación de campos requeridos
   - Integración con ERP para lista de proveedores
   - Drag & drop para links de cloud

2. **Modal de Detalle/Edición**
   - Vista completa de la factura
   - Edición inline de campos según permisos
   - Botones de acción por rol (marcar OC, FC, retirado, etc.)
   - Sección de observaciones con historial

3. **Integración con ERP**
   - Lista de proveedores desde ERP
   - Validación de proveedores existentes
   - Sincronización automática de datos

4. **Sistema de Notificaciones Push**
   - Notificaciones cuando hay tareas pendientes
   - Alertas por rol (ej: "Hay 5 facturas listas para cargar OC")
   - Notificaciones Windows (futuro)

5. **Exportación**
   - Exportar facturas a Excel/CSV
   - Filtros aplicados en la exportación

---

## 📝 Notas de Implementación

### Decisiones de Diseño

1. **Una sola tabla:** En lugar de replicar la arquitectura de 4 planillas de Sheets, se usa una sola tabla con todos los campos. Los permisos controlan qué campos puede ver/editar cada rol.

2. **Observaciones separadas:** Las observaciones están en tabla separada para permitir historial completo y filtrado por rol.

3. **Fechas automáticas:** Las fechas se establecen automáticamente al marcar estados (OC, FC, retirado, controlado, pagado) para evitar errores manuales.

4. **Validaciones soft:** El control sin OC es un aviso, no un bloqueo, para no trabar el proceso operativo.

5. **Roles específicos:** Cada rol del proceso es independiente del rol ADMIN del sistema para evitar confusiones.

---

## 🔧 Troubleshooting

### "No tengo permiso para ver facturas"

**Solución:**
1. Verificar que el usuario tenga el rol correcto asignado
2. Verificar que el rol tenga el permiso `facturas_compras.ver`
3. Verificar que las migraciones se aplicaron correctamente

### "Error al crear factura: tabla no existe"

**Solución:**
1. Verificar que la migración `7c95ca8072fc` se aplicó: `alembic current`
2. Si no está aplicada: `alembic upgrade head`
3. Verificar que PostgreSQL está corriendo

### "Los roles no aparecen en el panel de admin"

**Solución:**
1. Verificar que la migración `0e4585fa9ede` se aplicó
2. Verificar en la base de datos: `SELECT * FROM roles WHERE codigo IN ('COMPRAS', 'CARGA_OC_FC_GBP', 'DEPO', 'TESORERIA');`

---

## 📚 Referencias

- **Modelo de datos:** `backend/app/models/factura_compra.py`
- **Endpoints:** `backend/app/api/endpoints/facturas_compras.py`
- **Frontend:** `frontend/src/pages/FacturasCompras.jsx`
- **Migraciones:** `backend/alembic/versions/7c95ca8072fc_*.py` y `0e4585fa9ede_*.py`
- **Permisos:** `backend/app/models/permiso.py` (líneas 520-562)

---

**Última actualización:** Enero 2025
