# Guía Completa para Replicar el Sistema de Planillas de Compras

**Versión:** 1.0  
**Fecha:** 2026-01-19  
**Propósito:** Documento único con toda la información necesaria para replicar el sistema en otro proyecto (pricing app de Gauss)

---

## 📋 Tabla de Contenidos

1. [Descripción General del Sistema](#descripción-general-del-sistema)
2. [Arquitectura y Componentes](#arquitectura-y-componentes)
3. [Modelo de Datos](#modelo-de-datos)
4. [Flujo de Eventos](#flujo-de-eventos)
5. [Configuración y Constantes](#configuración-y-constantes)
6. [Sistema de Protección de Celdas](#sistema-de-protección-de-celdas)
7. [Web Apps y Despliegues](#web-apps-y-despliegues)
8. [Identificación Dinámica de Columnas](#identificación-dinámica-de-columnas)
9. [Optimizaciones Implementadas](#optimizaciones-implementadas)
10. [Optimizaciones Pendientes](#optimizaciones-pendientes)
11. [Tareas Pendientes](#tareas-pendientes)
12. [Consideraciones para Replicación](#consideraciones-para-replicación)

---

## 🎯 Descripción General del Sistema

### ¿Qué es?

Sistema de gestión de compras basado en Google Sheets que coordina múltiples planillas operativas mediante eventos. Cada planilla representa una etapa del proceso de compras y se comunica con una planilla central (MASTER) que actúa como router, logger y autoridad de bloqueos.

### Planillas del Sistema

1. **COMPRAS**: Planilla origen que genera nuevas filas y dispara el proceso inicial
2. **ADMIN**: Gestiona la parte del pago
3. **ALEN_GABE**: Gestiona la carga de Orden de Compra (OC) y Factura (FC)
4. **DEPO**: Gestiona la recepción/retiro de mercadería y control físico
5. **MASTER**: Planilla central que recibe eventos, distribuye cambios y mantiene logs

### Características Principales

- **Identificación lógica por `row_id`**: Cada fila tiene un identificador único que la identifica lógicamente (no por posición)
- **Eventos basados en checkboxes**: Los eventos se disparan cuando un checkbox cambia de FALSE a TRUE
- **Protección dinámica de celdas**: Las celdas se protegen después de eventos para evitar ediciones no deseadas
- **Sincronización entre planillas**: Los cambios se propagan automáticamente entre planillas relacionadas
- **Logging centralizado**: Todos los eventos se registran en MASTER

---

## 🏗️ Arquitectura y Componentes

### Estructura de Archivos

```
Planilla-Compras/
├── 0.MASTER/
│   └── MASTER.gs          # Router central, logger, autoridad de bloqueos
├── 1.COMPRAS/
│   ├── COMPRAS.gs         # Trigger onEdit para COMPRAS
│   ├── common.gs          # Funciones compartidas (Web App, protección)
│   └── config.gs          # Configuración específica de COMPRAS
├── 2.ADMIN/
│   ├── ADMIN.gs
│   ├── common.gs
│   └── config.gs
├── 3.ALEN_GABE/
│   ├── ALEN_GABE.gs
│   ├── common.gs
│   └── config.gs
├── 4.DEPO/
│   ├── DEPO.gs
│   ├── common.gs
│   └── config.gs
└── src/                   # Código fuente (copia de referencia)
```

### Componentes Principales

#### 1. Planillas Operativas (COMPRAS, ADMIN, ALEN_GABE, DEPO)

Cada planilla tiene:
- **`{NOMBRE}.gs`**: Trigger `onEdit` que detecta cambios y dispara eventos
- **`common.gs`**: Funciones compartidas:
  - `doGet()`: Web App para protección y escritura en celdas protegidas
  - `buildEventJSON()`: Construye el JSON del evento
  - `sendToMaster()`: Envía evento a MASTER vía HTTP POST
  - `getColumnIndexMap()`: Mapea nombres internos a índices de columna
  - `protectReadOnlyColumns()`: Protege columnas no editables
  - `lockColumns()`: Bloquea columnas después de eventos
- **`config.gs`**: Configuración específica:
  - `SHEET_CONFIGS`: Define columnas editables, no editables y eventos
  - `MASTER_URL`: URL del Web App de MASTER
  - `PROTECTION_WEBAPP_URL`: URL del Web App local

#### 2. MASTER

- **`MASTER.gs`**: 
  - `doPost()`: Recibe eventos de planillas operativas
  - `processEvent()`: Procesa y distribuye eventos
  - `updateSheet()`: Actualiza planillas destino
  - `createRowsInOtherSheets()`: Crea filas nuevas en otras planillas
  - `findRowByRowId()`: Busca fila por `row_id` (identificación lógica)
  - `logEvent()`: Registra eventos en hoja LOG
  - `writeBatchViaWebAppForSheet()`: Escribe múltiples celdas en batch

### Comunicación entre Componentes

```
Usuario edita celda
    ↓
onEdit() (planilla operativa)
    ↓
buildEventJSON()
    ↓
sendToMaster() → HTTP POST → MASTER.doPost()
    ↓
processEvent()
    ↓
updateSheet() / createRowsInOtherSheets()
    ↓
writeBatchViaWebAppForSheet() → HTTP GET → common.gs.doGet()
    ↓
Escritura en celdas protegidas
```

---

## 📊 Modelo de Datos

### Estructura de Filas en Google Sheets

Cada planilla tiene esta estructura:

- **Fila 1 (INTERNAL_NAMES_ROW)**: Nombres internos de columnas (oculta)
  - Ejemplo: `row_id,company_id,row_date,prov_name,...`
  - Se usa para identificación dinámica de columnas
- **Fila 2**: Named Range `SISTEMA_AYUDA` (para mensajes al usuario)
- **Fila 12 (HEADER_ROW)**: Nombres visibles de columnas (cabeceras)
- **Fila 13+ (FIRST_DATA_ROW)**: Datos

### Nombres Internos de Columnas (Completos)

```
row_id,company_id,row_date,prov_name,profo_id,profo_link,oc_date,oc_bool,
logistics,priority,deliv_date,deliv_bool,fc_id,fc_link,control_date,
control_bool,fc_date,fc_bool,comments,payrdy_bool,pay_method,pay_terms,
pay_tc,pay_date,pay_bool,comments_input
```

### Columnas por Planilla

#### COMPRAS (25 columnas)
- **Editables (2-15)**: `company_id`, `row_date`, `prov_name`, `profo_id`, `profo_link`, `logistics`, `priority`, `fc_id`, `fc_link`, `comments`, `pay_method`, `pay_terms`, `pay_tc`, `payrdy_bool`
- **No editables (1, 16-25)**: `row_id`, `pay_date`, `pay_bool`, `deliv_date`, `deliv_bool`, `control_date`, `control_bool`, `oc_date`, `oc_bool`, `fc_date`, `fc_bool`

#### ADMIN (13 columnas)
- **No editables (1-11)**: `row_id`, `company_id`, `row_date`, `prov_name`, `profo_id`, `profo_link`, `pay_method`, `pay_terms`, `pay_tc`, `comments`, `pay_date`
- **Editables (12-13)**: `comments_input`, `pay_bool`

#### ALEN_GABE (18 columnas)
- **No editables (1-15)**: `row_id`, `company_id`, `row_date`, `prov_name`, `profo_id`, `profo_link`, `logistics`, `priority`, `fc_id`, `fc_link`, `comments`, `control_date`, `control_bool`, `oc_date`, `fc_date`
- **Editables (16-18)**: `oc_bool`, `fc_bool`, `comments_input`

#### DEPO (18 columnas)
- **No editables (1-15)**: `row_id`, `company_id`, `row_date`, `prov_name`, `profo_id`, `profo_link`, `logistics`, `priority`, `fc_id`, `fc_link`, `comments`, `oc_bool`, `fc_bool`, `deliv_date`, `control_date`
- **Editables (16-18)**: `deliv_bool`, `control_bool`, `comments_input`

**Nota**: Ver `docs/ORDEN_COLUMNAS_REORGANIZADAS.md` para el orden exacto y constantes.

### Identificador Único: `row_id`

- **Formato**: `{SHEET_TYPE}_{timestamp}_{random}`
  - Ejemplo: `COMPRAS_1768814635246_5c6lnhs`
- **Generación**: Solo COMPRAS puede generar `row_id` nuevos
- **Propósito**: Identificar filas lógicamente (no por posición física)
- **Uso**: Todas las búsquedas y actualizaciones usan `row_id`, no número de fila

---

## 🔄 Flujo de Eventos

### Eventos Disponibles

| Planilla | Columna Trigger | Evento | Descripción |
|----------|----------------|--------|-------------|
| COMPRAS | `payrdy_bool` | `COMPRAS_NEWIDSENT` | Genera `row_id` y crea filas en otras planillas |
| ADMIN | `pay_bool` | `ADMIN_PAGO` | Registra pago realizado |
| ALEN_GABE | `oc_bool` | `ALENGABE_OC_CARGADA` | Registra carga de Orden de Compra |
| ALEN_GABE | `fc_bool` | `ALENGABE_FC_CARGADA` | Registra carga de Factura |
| DEPO | `deliv_bool` | `DEPO_DELIVERY_RECIBIDO` | Registra recepción/retiro |
| DEPO | `control_bool` | `DEPO_CONTROLADO` | Registra control físico |

### Flujo Detallado de un Evento

#### 1. Usuario edita checkbox (ej: `payrdy_bool = TRUE`)

```javascript
// En COMPRAS.gs
function onEdit(e) {
  // Validaciones: fila correcta, columna válida, valor = TRUE
  // Generar row_id si no existe (solo COMPRAS)
  // Construir JSON del evento
  // Enviar a MASTER
}
```

#### 2. Construcción del JSON del evento

```javascript
// En common.gs
function buildEventJSON(row, eventColumn, sheetType) {
  const eventConfig = config.events[eventColumn];
  const changes = {};
  
  // Agregar columnas según columnsToSend
  eventConfig.columnsToSend.forEach(colName => {
    changes[colName] = getCellValueByColumnName(row, colName);
  });
  
  return {
    row_id: getRowId(row),
    source_sheet: sheetType,
    event_type: eventConfig.eventType,
    timestamp: getLocalTimestamp(),
    changes: changes,
    source_row: row
  };
}
```

#### 3. Envío a MASTER

```javascript
// En common.gs
function sendToMaster(eventJSON) {
  const options = {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify(eventJSON),
    muteHttpExceptions: true
  };
  
  const response = UrlFetchApp.fetch(MASTER_URL, options);
  // Manejo de errores...
}
```

#### 4. Procesamiento en MASTER

```javascript
// En MASTER.gs
function doPost(e) {
  const eventData = JSON.parse(e.postData.contents);
  const result = processEvent(eventData);
  // Logging...
}

function processEvent(eventData) {
  const { row_id, source_sheet, event_type, changes } = eventData;
  
  // Buscar fila en todas las planillas por row_id
  const rowPositions = findRowByRowId(row_id);
  
  // Determinar qué columnas actualizar según el evento
  // Actualizar planillas destino
  // Bloquear columnas según el evento
  
  return { success: true, result: 'APPLIED' };
}
```

#### 5. Actualización de Planillas Destino

```javascript
// En MASTER.gs
function updateSheet(sheetName, row_id, changes) {
  // Buscar fila por row_id
  // Escribir cambios vía Web App (para celdas protegidas)
  // Usar batch write para múltiples celdas
}

function createRowsInOtherSheets(rowId, changes) {
  // Para COMPRAS_NEWIDSENT: crear filas nuevas en ADMIN, ALEN_GABE, DEPO
  // Escribir múltiples columnas en batch
}
```

### Ejemplo de JSON de Evento

```json
{
  "row_id": "COMPRAS_1768814635246_5c6lnhs",
  "source_sheet": "COMPRAS",
  "event_type": "COMPRAS_NEWIDSENT",
  "timestamp": "2026-01-19T06:23:58.000",
  "changes": {
    "row_id": "COMPRAS_1768814635246_5c6lnhs",
    "company_id": "Empresa XYZ",
    "row_date": "2026-01-19",
    "prov_name": "Proveedor ABC",
    "profo_id": "PROF-123",
    "profo_link": "https://...",
    "logistics": "Retiro",
    "priority": "Alta",
    "fc_id": "FC-456",
    "fc_link": "https://...",
    "comments": "Observaciones",
    "payrdy_bool": true,
    "pay_method": "Transferencia",
    "pay_terms": "30 días",
    "pay_tc": "USD"
  },
  "source_row": 15
}
```

---

## ⚙️ Configuración y Constantes

### Constantes en `config.gs` (Planillas Operativas)

```javascript
// URLs
const MASTER_URL = 'https://script.google.com/macros/s/.../exec';
const PROTECTION_WEBAPP_URL = 'https://script.google.com/macros/s/.../exec';

// Estructura de filas
const CONFIG = {
  HEADER_ROW: 12,           // Fila de cabeceras visibles
  FIRST_DATA_ROW: 13,       // Primera fila con datos
  INTERNAL_NAMES_ROW: 1,    // Fila con nombres internos (oculta)
  ALERT_ROW: 2              // Fila para avisos (deprecated, usar SISTEMA_AYUDA)
};

const MAIN_SHEET_NAME = 'PROCESO_DE_COMPRAS';
const MANUAL_SHEET_TYPE = 'COMPRAS'; // 'COMPRAS', 'ADMIN', 'ALEN_GABE', 'DEPO'
```

### Configuración de Eventos (`SHEET_CONFIGS`)

```javascript
const SHEET_CONFIGS = {
  COMPRAS: {
    allowedColumns: ['company_id', 'row_date', ...],      // Columnas editables
    readOnlyColumns: ['row_id', 'pay_date', ...],          // Columnas protegidas
    events: {
      'payrdy_bool': {
        eventType: 'COMPRAS_NEWIDSENT',
        columnsToLock: ['payrdy_bool', 'company_id', ...], // Columnas a bloquear después
        columnsToSend: ['row_id', 'company_id', ...]       // Columnas a enviar a MASTER
      }
    },
    hasCommentsInput: false
  },
  // ... otras planillas
};
```

### Constantes en `MASTER.gs`

```javascript
// IDs de las planillas
const SHEET_IDS = {
  COMPRAS: '14JZHVpR36Nm-t_bdKW-o29XjAqPes80VohkE_bIqcFI',
  ADMIN: '1W46nlLgxin6xMMYEQq61riHqezNuikzpzlR-JryAr9k',
  ALEN_GABE: '1mPszZaBG5vzBzMSCEnVQ59PXiIGBE_eaEEkH937fvEg',
  DEPO: '15eg2vDQio_0M9se6kz8jFvfbGzOcyjMY6txKa4VMNkM'
};

// URLs de Web Apps de planillas operativas
const WEBAPP_URLS = {
  COMPRAS: 'https://script.google.com/macros/s/.../exec',
  ADMIN: 'https://script.google.com/macros/s/.../exec',
  // ...
};

const LOG_SHEET_NAME = 'LOG';
```

---

## 🔒 Sistema de Protección de Celdas

### Estrategia de Protección

#### Protección Global Inicial

- **Configuración manual en Google Sheets**: Protección global de toda la hoja con excepciones para columnas editables
- **Columnas NO editables**: Protegidas desde el inicio (siempre)
- **Columnas editables**: Desprotegidas inicialmente, se protegen después de eventos

#### Protección Dinámica Después de Eventos

- Cuando un evento se dispara, las columnas especificadas en `columnsToLock` se protegen
- La protección se hace vía Web App (con permisos de propietario)
- **Estrategia futura (NO implementada)**: Extender rangos contiguos y consolidar periódicamente

### Funciones de Protección

#### `protectReadOnlyColumns()` (en `common.gs`)

Protege columnas no editables. Actualmente usa protección global manual, pero el código está preparado para protección por rangos.

#### `lockColumns()` (en `common.gs`)

Bloquea columnas después de un evento. Se llama desde MASTER vía Web App.

```javascript
function lockColumns(row, columnNames, sheetType) {
  // Proteger columnas específicas en una fila específica
  // Usado después de eventos
}
```

### Named Range: `SISTEMA_AYUDA`

- **Propósito**: Mostrar mensajes de ayuda o alertas al usuario
- **Ubicación**: Fila 2 (configurable)
- **Uso**: `ss.getRangeByName('SISTEMA_AYUDA').setValue(message)`
- **Estado**: Creado en todas las planillas, pendiente implementar en código

---

## 🌐 Web Apps y Despliegues

### ¿Qué son los Web Apps?

Los Web Apps permiten que el código se ejecute con permisos de **propietario**, incluso cuando un usuario sin permisos hace una acción. Esto es necesario para escribir en celdas protegidas.

### Web Apps en el Sistema

1. **MASTER Web App**: Recibe eventos de planillas operativas (`doPost`)
2. **Planillas Operativas Web Apps**: Escriben en celdas protegidas y aplican protecciones (`doGet`)

### Acciones del Web App de Planillas Operativas (`doGet`)

```javascript
// ?action=write&sheet=...&row=...&column=...&value=...
// ?action=writeBatch&data=[{row,column,value},...]
// ?action=protect&row=...&columns=[...]
// ?action=lock&row=...&columns=[...]
```

### Acciones del Web App de MASTER (`doPost`)

```javascript
// POST con JSON del evento
{
  "row_id": "...",
  "source_sheet": "...",
  "event_type": "...",
  "changes": {...}
}
```

### ⚠️ IMPORTANTE: Actualizar Web Apps

**SIEMPRE** que cambies código en:
- `common.gs` (especialmente `doGet()`)
- `MASTER.gs` (especialmente `doPost()`)

**Debes**:
1. Abrir editor de Apps Script
2. Implementar → Administrar implementaciones
3. Nueva versión → Guardar nueva versión
4. **NO cambiar** la URL (se mantiene igual)

---

## 🔍 Identificación Dinámica de Columnas

### Sistema: `getColumnIndexMap()`

**NO usa named ranges** para identificar columnas. En su lugar, usa un sistema dinámico basado en la **fila 1** (nombres internos).

#### Cómo Funciona

1. **Fila 1 (INTERNAL_NAMES_ROW)**: Contiene los nombres internos de las columnas
   - Ejemplo: `row_id,company_id,row_date,prov_name,...`
   - Esta fila está **oculta** en la hoja
   - Debe estar en el mismo orden que las columnas visibles

2. **Función `getColumnIndexMap()`**: Lee la fila 1 y crea un mapa
   ```javascript
   function getColumnIndexMap() {
     const sheet = ss.getSheetByName(MAIN_SHEET_NAME);
     const headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
     
     const columnMap = {};
     headers.forEach((header, index) => {
       columnMap[header.trim()] = index + 1; // +1 porque columnas empiezan en 1
     });
     
     return columnMap; // {row_id: 1, company_id: 2, ...}
   }
   ```

3. **Uso en el código**: Se accede al índice por nombre
   ```javascript
   const columnMap = getColumnIndexMap();
   const rowIdCol = columnMap['row_id']; // Obtiene el número de columna
   sheet.getRange(row, rowIdCol).setValue(value);
   ```

#### Ventajas

- ✅ **Performance**: Solo 1 llamada a la API por evento
- ✅ **Flexibilidad**: Si reorganizas columnas, solo actualizas la fila 1
- ✅ **Dinámico**: El código se adapta automáticamente al orden de columnas

#### ⚠️ Importante: Mantener Consistencia

- La **fila 1** debe tener los nombres internos en el mismo orden que las columnas visibles
- Los nombres internos deben coincidir exactamente con los usados en `SHEET_CONFIGS`
- Si cambias el orden de columnas físicamente, **debes actualizar la fila 1** también

---

## ⚡ Optimizaciones Implementadas

### ✅ Batch de Escrituras en Web Apps

**Problema**: `writeCellViaWebAppForSheet` hacía una llamada HTTP por celda. En `createRowsInOtherSheets` se escribían 5-6 celdas por planilla = 15-18 llamadas HTTP totales.

**Solución**: 
- Modificado `doGet` en `common.gs` para aceptar acción `writeBatch` con múltiples celdas
- Creado `writeBatchViaWebAppForSheet` en `MASTER.gs` para acumular celdas y hacer una sola llamada por planilla

**Impacto**: Reducción significativa en tiempo de `COMPRAS_NEWIDSENT` (de ~300s a ~244s, aunque aún lento)

**Código**:
```javascript
// En common.gs - doGet
} else if (action === 'writeBatch') {
  const cells = JSON.parse(decodeURIComponent(e.parameter.data));
  // Escribir todas las celdas en batch
  // ...
}

// En MASTER.gs
function writeBatchViaWebAppForSheet(sheetName, cells, webappUrl) {
  const batchData = { cells: cells };
  const dataParam = encodeURIComponent(JSON.stringify(batchData));
  const url = `${webappUrl}?action=writeBatch&data=${dataParam}`;
  // ...
}
```

### ✅ Reducción de Logs

**Problema**: Muchos `Logger.log` y `debugLogs.push` en funciones críticas.

**Solución**: Reducidos logs a solo errores críticos en:
- `processEvent()`, `logEvent()`, `findRowByRowId()`, `createRowsInOtherSheets()`, etc.

**Impacto**: Mejora en performance (aunque no medida exactamente)

### ✅ Timestamps Locales (Argentina UTC-3)

**Problema**: Timestamps en logs en UTC, difíciles de leer.

**Solución**: Creada función `getLocalTimestamp()` en `MASTER.gs` que convierte a UTC-3.

**Código**:
```javascript
function getLocalTimestamp() {
  const now = new Date();
  const offset = -3 * 60; // -3 horas en minutos
  const localTime = new Date(now.getTime() + (offset * 60 * 1000));
  // Formatear como ISO en hora local
  return `${year}-${month}-${day}T${hours}:${minutes}:${seconds}.${milliseconds}`;
}
```

**Estado**: Implementado en `MASTER.gs`, pendiente aplicar en planillas operativas.

---

## 📋 Optimizaciones Pendientes

### 🔴 Alta Prioridad

#### 1. Reducir logs en `onEditInstalled` de planillas operativas
- **Archivos**: `COMPRAS.gs`, `ADMIN.gs`, `ALEN_GABE.gs`, `DEPO.gs`
- **Acción**: Eliminar logs de debug, mantener solo errores críticos
- **Impacto esperado**: Reducción de 10-20 segundos por evento
- **Complejidad**: Baja

#### 2. Cambiar timestamps a hora local en planillas operativas
- **Archivos**: `common.gs` de todas las planillas operativas
- **Acción**: Usar `getLocalTimestamp()` (ya existe en MASTER)
- **Impacto esperado**: Mejora UX, no afecta performance
- **Complejidad**: Baja

### 🟡 Media Prioridad

#### 3. Cachear resultados de `findRowByRowId` durante un evento
- **Archivos**: `MASTER.gs`
- **Acción**: Cachear `rowPositions` en `processEvent` y pasarlo a funciones que lo necesiten
- **Impacto esperado**: Reducción de 5-10 segundos por evento
- **Complejidad**: Media (requiere refactorizar varias funciones)

#### 4. Reducir validaciones redundantes en `updateSheet`
- **Archivos**: `MASTER.gs`
- **Acción**: Cachear referencias a sheets durante el procesamiento de un evento
- **Impacto esperado**: Reducción de 3-5 segundos por evento
- **Complejidad**: Media

### 🟢 Baja Prioridad

#### 5. Optimizar `getColumnIndexMapForSheet` con cache global
- **Archivos**: `MASTER.gs`, `config.gs`
- **Acción**: Cachear en Properties Service (persistente entre ejecuciones)
- **Impacto esperado**: Reducción de 1-2 segundos por evento
- **Complejidad**: Media-Alta (requiere manejo de invalidación de cache)
- **⚠️ CONSIDERACIÓN**: Conversar sobre estrategia de invalidación antes de implementar

#### 6. Paralelizar escrituras a diferentes sheets
- **Archivos**: `MASTER.gs`
- **Acción**: Usar `UrlFetchApp.fetchAll` para paralelizar Web App calls
- **Impacto esperado**: Reducción de 30-50% en tiempo total (si es posible)
- **Complejidad**: Alta (Apps Script puede no permitir paralelismo real)

**Ver `docs/OPTIMIZACIONES_PENDIENTES.md` para más detalles.**

---

## 📝 Tareas Pendientes

### Mejoras de Código

1. **Implementar Named Range SISTEMA_AYUDA en el código**
   - Archivos: `src/common.gs` (y copias)
   - Acción: Reemplazar uso de `CONFIG.ALERT_ROW`, `ALERT_COL_START`, `ALERT_COL_END` por `getRangeByName('SISTEMA_AYUDA')`
   - Estado: Named range creado, falta actualizar código

2. **Actualizar constantes de columnas después de reorganización**
   - Archivos: `src/config.gs` (y copias), `MASTER.gs`
   - Acción: Agregar constantes `COMPRAS_PROTECTED_COLUMNS`, `ADMIN_PROTECTED_COLUMNS`, etc.
   - Estado: Reorganización completada, listo para implementar

### Sistema de Protecciones (NO implementar todavía)

1. **Implementar protección por filas con extensión de rangos contiguos**
   - Archivos: `MASTER.gs` (función `lockColumnsForEvent`)
   - Funcionalidad: Al proteger una fila nueva, verificar si es contigua a rangos protegidos existentes y extender

2. **Implementar consolidación periódica de protecciones**
   - Archivos: `MASTER.gs` (nueva función)
   - Funcionalidad: Trigger periódico a las 3:00 AM para consolidar protecciones contiguas

**Ver `docs/TAREAS_PENDIENTES.md` para lista completa y detalles.**

---

## 🔄 Consideraciones para Replicación

### Diferencias Clave con Pricing App de Gauss

1. **Plataforma**: 
   - **Actual**: Google Sheets + Apps Script
   - **Nueva**: Pricing App de Gauss (probablemente base de datos + frontend)

2. **Identificación de Columnas**:
   - **Actual**: Sistema dinámico basado en fila 1 (nombres internos)
   - **Nueva**: Probablemente schema de base de datos o configuración JSON

3. **Protección de Celdas**:
   - **Actual**: Protección de rangos en Google Sheets
   - **Nueva**: Probablemente permisos a nivel de usuario/rol en la base de datos

4. **Web Apps**:
   - **Actual**: Apps Script Web Apps para escribir en celdas protegidas
   - **Nueva**: Probablemente API REST con autenticación/autorización

### Conceptos a Replicar

1. **Sistema de Eventos**: 
   - Eventos basados en cambios de estado (checkboxes)
   - JSON de eventos con `row_id`, `source_sheet`, `event_type`, `changes`
   - Router central (MASTER) que distribuye eventos

2. **Identificación Lógica**:
   - `row_id` como identificador único lógico (no posición física)
   - Búsquedas por `row_id` en lugar de número de fila

3. **Sincronización entre Módulos**:
   - Cuando un evento se dispara, actualizar módulos relacionados
   - Batch writes para múltiples actualizaciones

4. **Logging Centralizado**:
   - Todos los eventos se registran en un lugar central
   - Timestamps locales, información de cambios aplicados

5. **Protección Dinámica**:
   - Campos editables hasta que se dispara un evento
   - Después del evento, campos se bloquean para evitar ediciones

### Preguntas para el Nuevo Proyecto

1. **¿Cómo se manejarán los permisos?** (equivalente a protección de celdas)
2. **¿Cómo se identificarán los registros?** (equivalente a `row_id`)
3. **¿Cómo se dispararán los eventos?** (equivalente a `onEdit` con checkboxes)
4. **¿Habrá un router central?** (equivalente a MASTER)
5. **¿Cómo se sincronizarán los datos entre módulos?** (equivalente a `updateSheet`)
6. **¿Cómo se hará el logging?** (equivalente a hoja LOG en MASTER)

### Estructura de Datos Sugerida para Replicación

```javascript
// Equivalente a SHEET_CONFIGS
const MODULE_CONFIGS = {
  COMPRAS: {
    editableFields: ['company_id', 'row_date', ...],
    readOnlyFields: ['row_id', 'pay_date', ...],
    events: {
      'payrdy_bool': {
        eventType: 'COMPRAS_NEWIDSENT',
        fieldsToLock: ['payrdy_bool', 'company_id', ...],
        fieldsToSend: ['row_id', 'company_id', ...]
      }
    }
  }
};

// Equivalente a evento JSON
{
  "row_id": "COMPRAS_1768814635246_5c6lnhs",
  "source_module": "COMPRAS",
  "event_type": "COMPRAS_NEWIDSENT",
  "timestamp": "2026-01-19T06:23:58.000",
  "changes": {
    "row_id": "...",
    "company_id": "...",
    // ...
  }
}
```

---

## 📚 Documentos Relacionados

- **`GUIA_DESARROLLADOR.md`**: Guía detallada para desarrolladores (modificar planillas, agregar nuevas, troubleshooting)
- **`OPTIMIZACIONES_PENDIENTES.md`**: Detalles técnicos de optimizaciones de performance
- **`ORDEN_COLUMNAS_REORGANIZADAS.md`**: Orden exacto de columnas después de reorganización
- **`PLAN_REORGANIZACION_COLUMNAS.md`**: Plan de implementación de reorganización (FASE 1 completada)
- **`TAREAS_PENDIENTES.md`**: Lista maestra de todas las tareas pendientes
- **`doc_funcional.md`**: Documentación funcional original del sistema

---

## 💡 Notas Finales

### Tiempos Actuales de Ejecución

- **COMPRAS_NEWIDSENT**: ~244 segundos (4 minutos) - ⚠️ MUY LENTO
- **ADMIN_PAGO**: ~48 segundos
- **ALENGABE_OC_CARGADA**: ~52 segundos
- **ALENGABE_FC_CARGADA**: ~64 segundos
- **DEPO_DELIVERY_RECIBIDO**: ~70 segundos
- **DEPO_CONTROLADO**: ~77 segundos

### Mejores Prácticas Aprendidas

1. **Batch writes**: Siempre agrupar múltiples escrituras en una sola llamada HTTP
2. **Logs mínimos**: Solo errores críticos en producción
3. **Identificación lógica**: Usar `row_id` en lugar de números de fila
4. **Sistema dinámico**: Leer configuración de columnas desde la planilla (fila 1) en lugar de hardcodear
5. **Web Apps**: Siempre actualizar después de cambios en código

### Limitaciones Conocidas

1. **Performance**: Apps Script es lento para operaciones masivas
2. **Paralelismo**: Apps Script puede no permitir paralelismo real
3. **Límites de API**: Google Sheets API tiene límites de rate limiting
4. **Protecciones**: Manejar protecciones dinámicas es complejo en Sheets

---

**¿Preguntas?** Este documento debe servir como base para conversar sobre la replicación del sistema. Si necesitas más detalles sobre algún aspecto específico, consulta los documentos relacionados o pregunta directamente.
