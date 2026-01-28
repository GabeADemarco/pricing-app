# Plan de Restauración de Base de Datos

## 📋 Situación Actual

### ✅ Lo que tenemos:
1. **Dump completo de la base de datos**: `DB/pricing_full.sql.gz`
   - Contiene TODAS las migraciones aplicadas hasta el último commit de `develop` (`69fe2b1`)
   - Esto significa que NO necesitamos ejecutar las migraciones que fallaban antes

2. **Nuestras migraciones nuevas** (que SÍ necesitamos aplicar):
   - `ed9b542b9f3f` - Migración de merge (ya existe en develop, debería estar en el dump)
   - `7c95ca8072fc` - Crear sistema facturas_compras (NUEVA)
   - `0e4585fa9ede` - Agregar roles y permisos facturas_compras (NUEVA)

3. **Cambios en GitHub**: 
   - ✅ No hay cambios nuevos en `develop` que no tengamos
   - ✅ Nuestro branch `feature/sistema-facturas-compras` está actualizado

### ⚠️ Lo que necesitamos hacer:

## 🔧 Pasos para Restaurar y Sincronizar

### Paso 1: Preparar PostgreSQL

1. **Verificar que PostgreSQL esté corriendo**
   - Abrir pgAdmin 4 o verificar el servicio de Windows

2. **Crear la base de datos** (si no existe):
   ```sql
   -- En pgAdmin 4 o psql:
   CREATE DATABASE pricing_db_dev;
   ```

3. **Crear el usuario** (según `DB/crear usuario.txt`, adaptado para Windows):
   ```sql
   -- En pgAdmin 4, ejecutar como usuario postgres:
   CREATE USER pricing_user WITH PASSWORD 'pricing_pass';
   GRANT ALL PRIVILEGES ON DATABASE pricing_db_dev TO pricing_user;
   ```

### Paso 2: Restaurar el Dump

**⚠️ IMPORTANTE**: El archivo `pricing_full.sql.gz` es un SQL comprimido, NO un formato custom de PostgreSQL. Por eso `pg_restore` falla. Necesitamos descomprimirlo primero.

**Opción A: Usando pgAdmin 4 (Recomendado para Windows)**

1. **Descomprimir el archivo primero**:
   - Opción 1: Usar 7-Zip o WinRAR para descomprimir `pricing_full.sql.gz` → `pricing_full.sql`
   - Opción 2: Usar PowerShell:
     ```powershell
     # Si tienes gzip instalado:
     gzip -d DB\pricing_full.sql.gz
     
     # O usar .NET para descomprimir:
     Add-Type -AssemblyName System.IO.Compression.FileSystem
     [System.IO.Compression.GZipStream]::Decompress([System.IO.File]::OpenRead("DB\pricing_full.sql.gz"), [System.IO.File]::Create("DB\pricing_full.sql"))
     ```

2. **Restaurar usando Query Tool**:
   - Abrir pgAdmin 4
   - Click derecho en `pricing_db_dev` → `Query Tool`
   - En el menú: `File` → `Open` → Seleccionar `DB\pricing_full.sql`
   - Click en el botón "Execute" (⚡) o presionar F5
   - ⚠️ Esto puede tardar varios minutos dependiendo del tamaño del archivo

**Opción B: Usando línea de comandos (más rápido)**

```powershell
# 1. Descomprimir (si no lo hiciste antes)
# Usar 7-Zip desde línea de comandos:
& "C:\Program Files\7-Zip\7z.exe" x DB\pricing_full.sql.gz -oDB\

# O si tienes gzip en PATH:
gzip -d DB\pricing_full.sql.gz

# 2. Restaurar usando psql
# Encontrar psql.exe (normalmente en C:\Program Files\PostgreSQL\18\bin\)
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d pricing_db_dev -f DB\pricing_full.sql
```

**Opción C: Usando PowerShell para descomprimir y restaurar**

```powershell
# Descomprimir usando .NET
Add-Type -AssemblyName System.IO.Compression.FileSystem
$inFile = [System.IO.File]::OpenRead("DB\pricing_full.sql.gz")
$outFile = [System.IO.File]::Create("DB\pricing_full.sql")
$gzipStream = New-Object System.IO.Compression.GZipStream($inFile, [System.IO.Compression.CompressionMode]::Decompress)
$gzipStream.CopyTo($outFile)
$gzipStream.Close()
$outFile.Close()
$inFile.Close()

# Restaurar
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d pricing_db_dev -f DB\pricing_full.sql
```

### Paso 3: Verificar Estado de Alembic

Después de restaurar, verificar qué migraciones están aplicadas:

```powershell
cd backend
.\venv\Scripts\activate
alembic current
alembic history
```

**Resultado esperado**: Debería mostrar que está en el commit `69fe2b1` o similar (último commit de develop).

### Paso 4: Aplicar Nuestras Migraciones Nuevas

Si el dump tiene todas las migraciones hasta `69fe2b1`, entonces necesitamos aplicar solo las nuestras:

```powershell
cd backend
.\venv\Scripts\activate
alembic upgrade head
```

Esto debería aplicar:
- `7c95ca8072fc` - Crear sistema facturas_compras
- `0e4585fa9ede` - Agregar roles y permisos

### Paso 5: Verificar que Todo Funcione

1. **Verificar tablas creadas**:
   ```sql
   -- En pgAdmin 4:
   SELECT * FROM facturas_compras LIMIT 1;
   SELECT * FROM facturas_compras_observaciones LIMIT 1;
   ```

2. **Verificar roles y permisos**:
   ```sql
   SELECT * FROM roles WHERE codigo IN ('COMPRAS', 'CARGA_OC_FC_GBP', 'DEPO', 'TESORERIA');
   SELECT * FROM permisos WHERE codigo LIKE 'facturas_compras.%';
   ```

3. **Probar backend**:
   ```powershell
   cd backend
   .\venv\Scripts\activate
   python -m uvicorn app.main:app --reload --port 8002
   ```

4. **Probar frontend**:
   ```powershell
   cd frontend
   npm run dev
   ```

## 🚨 Posibles Problemas

### Problema 1: Alembic dice que hay migraciones pendientes que ya están aplicadas
**Solución**: Marcar manualmente la versión actual:
```powershell
alembic stamp <revision_id>
```

### Problema 2: El dump no tiene la migración de merge `ed9b542b9f3f`
**Solución**: Aplicar primero esa migración, luego las nuestras:
```powershell
alembic upgrade ed9b542b9f3f
alembic upgrade head
```

### Problema 3: Conflictos de migraciones
**Solución**: Verificar el historial completo y resolver manualmente si es necesario.

## 📝 Notas Importantes

1. **El dump contiene datos reales**: Ten cuidado de no sobrescribir datos importantes
2. **Backup primero**: Si ya tienes datos locales, haz un backup antes de restaurar
3. **Variables de entorno**: Asegúrate de que `backend/.env` tenga la configuración correcta:
   ```
   DATABASE_URL=postgresql://pricing_user:pricing_pass@localhost/pricing_db_dev
   ```

## ✅ Checklist Final

- [ ] PostgreSQL corriendo
- [ ] Base de datos `pricing_db_dev` creada
- [ ] Usuario `pricing_user` creado con permisos
- [ ] Dump restaurado exitosamente
- [ ] Estado de Alembic verificado
- [ ] Migraciones nuevas aplicadas
- [ ] Tablas verificadas
- [ ] Roles y permisos verificados
- [ ] Backend arranca correctamente
- [ ] Frontend arranca correctamente
