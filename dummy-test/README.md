# Demo Estática - Sistema de Facturas de Compra

Esta carpeta contiene una demo estática del sistema de facturas de compra que funciona **sin necesidad de backend ni base de datos**. Utiliza `localStorage` del navegador para simular la persistencia de datos.

## 📋 Requisitos

- **Python 3.x** (cualquier versión reciente)
- Un navegador web moderno (Chrome, Firefox, Edge, etc.)

## 🚀 Inicio Rápido

### Paso 1: Iniciar el servidor local

Abre una terminal en esta carpeta (`dummy-test`) y ejecuta:

```powershell
python -m http.server 8000
```

**Nota para Windows PowerShell:**
```powershell
cd dummy-test
python -m http.server 8000
```

**Nota para Linux/Mac:**
```bash
cd dummy-test
python3 -m http.server 8000
```

### Paso 2: Abrir los HTML en el navegador

Una vez que el servidor esté corriendo, abre **4 pestañas diferentes** en tu navegador y navega a:

1. **COMPRAS**: `http://localhost:8000/compras.html`
2. **CARGA_OC_FC_GBP**: `http://localhost:8000/carga.html`
3. **DEPO**: `http://localhost:8000/depo.html`
4. **TESORERIA**: `http://localhost:8000/tesoreria.html`

### Paso 3: Probar el flujo

1. En la pestaña de **COMPRAS**, crea una nueva factura (puedes dejarla como borrador o iniciarla).
2. Si la inicias, deberías verla aparecer en las otras 3 pestañas.
3. Cada rol puede realizar sus acciones específicas según sus permisos.

## 📁 Archivos Incluidos

- `compras.html` - Vista del rol COMPRAS (ve todo, puede crear/editar/iniciar)
- `carga.html` - Vista del rol CARGA_OC_FC_GBP (carga OC y FC)
- `depo.html` - Vista del rol DEPO (marca retirado y controlado)
- `tesoreria.html` - Vista del rol TESORERIA (marca pagado)
- `README.md` - Esta guía

## 🔑 Funcionalidades por Rol

### COMPRAS (`compras.html`)
- ✅ Ve **todas** las facturas (borradores e iniciadas)
- ✅ Ve **todas** las columnas
- ✅ Puede **crear** nuevas facturas
- ✅ Puede **editar** facturas (borradores e iniciadas)
- ✅ Puede **iniciar proceso** (cambia de borrador a iniciada)
- ✅ Puede **eliminar borradores**
- ✅ Puede agregar observaciones

### CARGA_OC_FC_GBP (`carga.html`)
- ✅ Ve solo facturas **iniciadas** (`iniciado = true`)
- ✅ Ve columnas: genéricas + `retirado`, `controlado`, `tc`, `oc`, `fc`
- ✅ Puede **marcar OC cargada** (requiere `iniciado = true`)
- ✅ Puede **marcar FC cargada** (requiere `iniciado = true` Y `controlado = true`)
- ✅ Puede agregar observaciones

### DEPO (`depo.html`)
- ✅ Ve solo facturas **iniciadas** (`iniciado = true`)
- ✅ Ve columnas: genéricas + `oc`, `retirado`, `controlado`
- ✅ Puede **marcar retirado** (requiere `iniciado = true`)
- ✅ Puede **marcar controlado** (requiere `iniciado = true` Y `retirado = true`)
- ✅ Puede agregar observaciones

### TESORERIA (`tesoreria.html`)
- ✅ Ve solo facturas **iniciadas** (`iniciado = true`)
- ✅ Ve columnas: genéricas + `tc`, `plazo`, `forma_pago`, `pagado`
- ✅ Puede **marcar pagado** (requiere `iniciado = true`)
- ✅ Puede agregar observaciones

## 📊 Columnas Genéricas (visibles para todos)

- Razón Social
- Proveedor
- Creada por
- Nro Proforma
- Nro Factura
- Fecha de Carga
- Estado (En borrador / En Proceso)

## 💾 Almacenamiento de Datos

Los datos se guardan en `localStorage` del navegador con la clave `facturas_compras_demo`. 

**Importante:** 
- Los datos son **compartidos** entre todas las pestañas que abran los HTML desde el mismo origen (`http://localhost:8000`).
- Si cierras el navegador, los datos se mantienen (localStorage persiste).
- Para **limpiar los datos**, abre la consola del navegador (F12) y ejecuta:
  ```javascript
  localStorage.removeItem('facturas_compras_demo');
  location.reload();
  ```

## 🎯 Flujo de Prueba Recomendado

1. **Crear factura en borrador** (COMPRAS):
   - Abre `compras.html`
   - Click en "Nueva Factura"
   - Completa algunos campos (no todos)
   - Guarda **sin** marcar "Iniciar proceso"
   - Verifica que aparece como "En borrador"
   - Verifica que **NO** aparece en las otras 3 pestañas

2. **Iniciar proceso** (COMPRAS):
   - En `compras.html`, click en "Iniciar Proceso"
   - Verifica que el estado cambia a "En Proceso"
   - Verifica que **SÍ** aparece en las otras 3 pestañas

3. **Cargar OC** (CARGA_OC_FC_GBP):
   - En `carga.html`, click en "Marcar OC Cargada"
   - Verifica que el estado de OC cambia

4. **Marcar Retirado** (DEPO):
   - En `depo.html`, click en "Marcar Retirado"
   - Verifica que el estado cambia

5. **Marcar Controlado** (DEPO):
   - En `depo.html`, click en "Marcar Controlado"
   - Verifica que el estado cambia

6. **Cargar FC** (CARGA_OC_FC_GBP):
   - En `carga.html`, click en "Marcar FC Cargada"
   - Verifica que ahora está habilitado (porque está controlado)

7. **Marcar Pagado** (TESORERIA):
   - En `tesoreria.html`, click en "Marcar Pagado"
   - Verifica que el estado cambia

## ⚠️ Limitaciones de la Demo

Esta es una demo **simplificada** para mostrar el flujo básico. No incluye:

- ❌ Validaciones complejas del backend
- ❌ Autenticación real (cada HTML simula un rol fijo)
- ❌ Subida de archivos reales (los links son texto)
- ❌ Paginación avanzada
- ❌ Filtros complejos
- ❌ Búsqueda avanzada
- ❌ Historial de observaciones completo
- ❌ Integración con ERP/GBP

## 🐛 Solución de Problemas

### El servidor no inicia
- Verifica que Python esté instalado: `python --version`
- Verifica que el puerto 8000 esté libre
- Intenta otro puerto: `python -m http.server 8080` (y cambia las URLs a `:8080`)

### Los datos no se comparten entre pestañas
- Asegúrate de que todas las pestañas abran desde `http://localhost:8000/...`
- **NO** abras los HTML con doble clic (`file://`), deben abrirse desde el servidor
- Recarga todas las pestañas después de hacer cambios

### Los botones no funcionan
- Abre la consola del navegador (F12) para ver errores
- Verifica que el servidor esté corriendo
- Verifica que estés usando `http://localhost:8000/...` y no `file://`

## 💡 Cargar Datos de Ejemplo

Para probar rápidamente con datos pre-cargados, abre la consola del navegador (F12) en cualquier HTML y ejecuta:

```javascript
// Datos de ejemplo: 1 borrador y 1 iniciada
const datosEjemplo = [
  {
    id: 1,
    razon_social: "Grupo Gauss",
    proveedor_nombre: "Proveedor Ejemplo S.A.",
    creado_por_nombre: "COMPRAS",
    nro_proforma: "PROF-001",
    link_proforma: "https://ejemplo.com/proforma1.pdf",
    logistica: "GAUSS",
    prioridad: "NORMAL",
    nro_factura: "",
    link_factura: "",
    forma_pago: "CONTADO",
    plazo: "",
    tipo_cambio: "1480 - 3%",
    observaciones: "",
    iniciado: false,
    oc_cargada: false,
    fc_cargada: false,
    retirado: false,
    controlado: false,
    pagado: false,
    fecha_carga: new Date().toISOString(),
    created_at: new Date().toISOString()
  },
  {
    id: 2,
    razon_social: "Pastoriza",
    proveedor_nombre: "Otro Proveedor S.R.L.",
    creado_por_nombre: "COMPRAS",
    nro_proforma: "PROF-002",
    link_proforma: "https://ejemplo.com/proforma2.pdf",
    logistica: "PROVEEDOR",
    prioridad: "URGENTE",
    nro_factura: "FC-001",
    link_factura: "https://ejemplo.com/factura1.pdf",
    forma_pago: "CTA CTE",
    plazo: "30 días",
    tipo_cambio: "1500",
    observaciones: "Factura de prueba iniciada",
    iniciado: true,
    oc_cargada: false,
    fc_cargada: false,
    retirado: false,
    controlado: false,
    pagado: false,
    fecha_carga: new Date().toISOString(),
    created_at: new Date().toISOString()
  }
];

localStorage.setItem('facturas_compras_demo', JSON.stringify(datosEjemplo));
location.reload();
```

Esto cargará 2 facturas de ejemplo:
- **Factura 1**: Borrador (solo visible en COMPRAS)
- **Factura 2**: Iniciada (visible en todos los roles)

## 📝 Notas

- Esta demo es **solo para visualización** del flujo de trabajo.
- Los datos se pierden si limpias el localStorage del navegador.
- Para una demo más realista, necesitarías el backend completo corriendo.
- Los datos se sincronizan automáticamente entre todas las pestañas abiertas desde el mismo origen.
