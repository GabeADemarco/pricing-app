# Checklist - Sistema de Facturas de Compra

## ✅ Completado

- [x] Base de datos restaurada (111 tablas)
- [x] Migraciones aplicadas (facturas_compras creadas)
- [x] Backend funcionando
- [x] Frontend funcionando
- [x] Usuario con rol ADMIN asignado
- [x] Página `/facturas-compras` accesible
- [x] Tabla visible (aunque vacía)

## 📋 Próximos Pasos

### Paso 1: Crear Usuarios Genéricos para Pruebas ✅

Crear usuarios de prueba para cada rol:

- [x] **Usuario COMPRAS**
  - Username: `compras`
  - Password: `compras123`
  - Rol: `COMPRAS`
  
- [x] **Usuario CARGA_OC_FC_GBP**
  - Username: `carga`
  - Password: `carga123`
  - Rol: `CARGA_OC_FC_GBP`
  
- [x] **Usuario DEPO**
  - Username: `depo`
  - Password: `depo123`
  - Rol: `DEPO`
  
- [x] **Usuario TESORERIA**
  - Username: `tesoreria`
  - Password: `tesoreria123`
  - Rol: `TESORERIA`

### Paso 1.5: Ajustes del Formulario de Creación

- [ ] Modificar la obligatoriedad del iniciar proceso del formulario inicial
- [ ] Cambiar a guardado de archivos locales (en el servidor)

### Paso 2: Probar Acceso y Vista de Cada Rol

Para cada usuario creado:

- [ ] Hacer login con cada usuario
- [ ] Acceder a `/facturas-compras`
- [ ] Verificar qué campos/columnas ve cada rol
- [ ] Verificar qué acciones puede realizar cada rol
- [ ] Documentar diferencias entre roles

### Paso 3: Implementar Formulario de Creación ✅

- [x] Crear componente de formulario para nueva factura
- [x] Campos iniciales (COMPRAS):
  - Razón Social (select: Grupo Gauss / Pastoriza)
  - Proveedor (input texto)
  - Nro Proforma
  - Link Proforma (input URL)
  - Logística (select: GAUSS / PROVEEDOR / TERCERO)
  - Prioridad (select: NORMAL / URGENTE)
  - Nro Factura
  - Link Factura (input URL)
  - Forma de Pago (select: CONTADO / CHEQUE / CTA CTE)
  - Plazo (texto)
  - Tipo de Cambio (texto)
  - Observaciones (textarea)
- [x] Validaciones del formulario
- [x] Integración con API POST `/api/facturas-compras`
- [x] Manejo de errores

### Paso 4: Cargar Factura de Prueba y Verificar Vistas ✅

- [x] Crear una factura de prueba usando usuario COMPRAS
- [x] Verificar que aparece en la tabla
- [x] Probar flujo de borrador:
  - [x] Crear factura como **borrador** (desmarcando "Iniciar proceso de carga de facturas")
  - [x] Verificar que el estado muestre **"En borrador"**
  - [x] Probar botón **"Eliminar borrador"** (con confirmación)
  - [x] Probar botón **"Iniciar proceso"** y verificar que cambia a **"En Proceso"** y ya no se puede borrar
- [x] Hacer login con cada rol y verificar visibilidad:
  - [x] COMPRAS: Ve todas las facturas (borradores e iniciadas)
  - [x] CARGA_OC_FC_GBP: Solo ve facturas iniciadas (`iniciado = true`)
  - [x] DEPO: Solo ve facturas iniciadas (`iniciado = true`)
  - [x] TESORERIA: Solo ve facturas iniciadas (`iniciado = true`)
- [x] Verificar que cada rol solo ve lo que debe ver
- [ ] Verificar qué campos/columnas específicas ve cada rol (pendiente)
- [ ] Verificar qué acciones puede realizar cada rol (pendiente)

### Paso 4.5: Mejoras de UX (ANTES DEL PASO 5) 🚧 (EN PROGRESO)

#### 4.5.1: Edición de Borradores ✅
- [x] Permitir editar facturas con `iniciado = false` (borradores)
- [x] Crear modal de edición (similar al de creación)
- [x] Validar campos obligatorios solo al "Iniciar proceso" (backend):
  - [x] Razón Social
  - [x] Proveedor
  - [x] Nro Proforma
  - [x] Link Proforma
  - [x] Logística
  - [x] Prioridad
  - [x] Forma de Pago
  - [x] Nro Factura
  - [x] Link Factura
- [x] Mostrar mensaje claro con campos faltantes si se intenta iniciar sin completar
- [ ] (Opcional) Validación en frontend antes de iniciar proceso para mejor UX

#### 4.5.2: Vista de Documentos en Modal ✅
- [x] Mejorar modal "Ver Detalle" para mostrar documentos
- [x] Agregar sección "Documentos" con:
  - [x] Link a Proforma (si existe)
  - [x] Link a Factura (si existe)
  - [x] Botones para abrir en nueva pestaña
- [x] Números de factura/proforma clickeables que abren popup con documento
- [x] Transformación automática de URLs a formato de visualización de Nextcloud
- [ ] (Futuro: vista previa cuando tengamos password_app)
- **Nota:** Limitación conocida de Nextcloud: a veces el documento no se visualiza correctamente en la primera carga del popup. Solución: cerrar y volver a abrir. Este comportamiento también ocurre en el sistema actual de Google Sheets.

#### 4.5.3: Badges Acumulativas (DESPUÉS)
- [ ] Reemplazar columnas individuales (OC, FC, RETIRADO, etc.) por badges horizontales
- [ ] Columna "Estado": "En borrador", "En Proceso", "Completado"
- [ ] Columna "Progreso": badges con colores individuales cuando se completan
- [ ] Badges: Listo para Pagar, OC, FC, Retirado, Controlado, Pagado

### Paso 5: Implementar Procesos de Cada Rol

#### 5.1: COMPRAS
- [ ] Botón "Marcar Listo para Pagar"
  - Cambia `listo_para_pagar = true`
  - Habilita acciones para otros roles
  - Validaciones (todos los campos requeridos completos)

#### 5.2: CARGA_OC_FC_GBP
- [ ] Botón "Cargar OC"
  - Campo para ingresar número de OC
  - Marca `oc_cargada = true`
  - Establece `oc_fecha = now()`
  - Validación: requiere `listo_para_pagar = true`
  
- [ ] Botón "Cargar FC"
  - Campo para ingresar número de FC
  - Marca `fc_cargada = true`
  - Establece `fc_fecha = now()`
  - Validación: requiere `retirado = true`

#### 5.3: DEPO
- [ ] Botón "Marcar Retirado"
  - Marca `retirado = true`
  - Establece `retirado_fecha = now()`
  
- [ ] Botón "Marcar Controlado"
  - Marca `controlado = true`
  - Establece `controlado_fecha = now()`
  - Advertencia si `oc_cargada = false` (pero permite continuar)

#### 5.4: TESORERIA
- [ ] Botón "Marcar Pagado"
  - Marca `pagado = true`
  - Establece `pagado_fecha = now()`
  - Validación: requiere `fc_cargada = true`
  - **Nota:** El pago no bloquea nada (según usuario)

### Paso 6: Sistema de Observaciones

- [ ] Campo de observaciones visible para todos los roles
- [ ] Formulario para agregar observación
- [ ] Mostrar historial de observaciones con:
  - Rol que la agregó
  - Usuario que la agregó
  - Fecha/hora
  - Contenido
- [ ] Integración con API POST `/api/facturas-compras/{id}/observaciones`

### Paso 7: Mejoras Visuales y UX

- [ ] Badges de estado más claros
- [ ] Colores diferenciados por estado
- [ ] Filtros funcionando correctamente
- [ ] Paginación funcionando
- [ ] Búsqueda funcionando
- [ ] Modal de detalle completo con todos los campos
- [ ] Edición inline o modal según corresponda

### Paso 8: Validaciones y Reglas de Negocio

- [ ] Validar que COMPRAS no puede avanzar estados de otros roles
- [ ] Validar que CARGA_OC_FC_GBP no puede marcar retirado/controlado
- [ ] Validar que DEPO no puede marcar pagado
- [ ] Validar que TESORERIA solo puede pagar
- [ ] Advertencias visuales cuando falta información requerida
- [ ] Mensajes de error claros

## 📝 Notas

- El pago **NO bloquea** nada (según requerimiento del usuario)
- Las observaciones son compartidas entre todos los roles
- Cada rol puede ver todas las observaciones
- Las fechas se establecen automáticamente cuando se marca cada acción

## 🎯 Objetivo Final

Tener un sistema completamente funcional donde:
1. COMPRAS carga la factura inicial
2. COMPRAS marca "Listo para Pagar"
3. CARGA_OC_FC_GBP carga OC y FC
4. DEPO marca retirado y controlado
5. TESORERIA marca pagado
6. Todos pueden ver el progreso y agregar observaciones
