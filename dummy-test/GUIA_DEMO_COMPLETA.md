# Guía Demo Completa - Pricing App

Esta guía permite preparar y ejecutar la demo del Pricing App con funcionalidad idéntica al ambiente de desarrollo. Incluye la demo estática (solo Facturas) y la demo completa (app entera con backend).

---

## Tabla de contenidos

1. [Requisitos previos](#1-requisitos-previos)
2. [Generar el dump de la base de datos](#2-generar-el-dump-de-la-base-de-datos)
3. [Opción A: Demo estática (2 minutos)](#3-opción-a-demo-estática-2-minutos)
4. [Opción B: Demo completa con backend](#4-opción-b-demo-completa-con-backend)
5. [Configuración de variables de entorno](#5-configuración-de-variables-de-entorno)
6. [Crear primer usuario (solo instalación nueva)](#6-crear-primer-usuario-solo-instalación-nueva)
7. [Arrancar backend y frontend](#7-arrancar-backend-y-frontend)
8. [Verificación y qué esperar](#8-verificación-y-qué-esperar)
9. [Solución de problemas](#9-solución-de-problemas)

---

## 1. Requisitos previos

| Software | Versión | Descarga |
|----------|---------|----------|
| **Git** | Reciente | https://git-scm.com/download/win |
| **Python** | 3.11+ | https://www.python.org/downloads/ (marcar "Add to PATH") |
| **Node.js** | 18 LTS+ | https://nodejs.org/ |
| **PostgreSQL** | 14+ | https://www.postgresql.org/download/windows/ |

Durante la instalación de PostgreSQL, anotá la contraseña del usuario `postgres`.

---

## 2. Generar el dump de la base de datos

Si vas a usar la demo completa en otro equipo, generá el dump donde tenés la base actual.

### Ubicación del dump

El dump debe guardarse en: **`DB/demo/pricing_full.sql`** (dentro del proyecto).

### Comando (ejecutar desde la raíz del proyecto)

```powershell
cd D:\Gabriel\PFA\Gauss\pricing-app\pricing-app\DB
mkdir demo -ErrorAction SilentlyContinue
& "C:\Program Files\PostgreSQL\18\bin\pg_dump.exe" -U postgres -d pricing_db_dev -f "demo\pricing_full.sql"
```

- Reemplazá `18` por tu versión de PostgreSQL si es distinta (ej: `16`, `15`).
- Reemplazá `pricing_db_dev` si tu base tiene otro nombre.
- El archivo queda en `DB\demo\pricing_full.sql`.
- La operación puede tardar varios minutos.

### Transportar el dump

La carpeta `DB/` está en `.gitignore`, así que no se sube a GitHub. Para llevarlo a otro equipo:

- Google Drive, OneDrive, Dropbox
- USB o disco externo
- WeTransfer (link temporal)

---

## 3. Opción A: Demo estática (2 minutos)

Solo Facturas de Compra, sin backend ni base de datos.

```powershell
cd dummy-test
python -m http.server 8000
```

Abrir en el navegador:
- **COMPRAS:** http://localhost:8000/compras.html
- **CARGA_OC_FC_GBP:** http://localhost:8000/carga.html
- **DEPO:** http://localhost:8000/depo.html
- **TESORERIA:** http://localhost:8000/tesoreria.html

Ver [README.md](README.md) para el flujo de prueba.

---

## 4. Opción B: Demo completa con backend

### 4.1. Clonar el repositorio

```powershell
git clone <URL_DEL_REPO> pricing-app
cd pricing-app
```

### 4.2. Crear base de datos

```powershell
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -c "CREATE DATABASE pricing_db_dev;"
```

### 4.3. Restaurar el dump

```powershell
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d pricing_db_dev -f "DB\demo\pricing_full.sql"
```

- Te pedirá la contraseña de `postgres`.
- Puede tardar varios minutos.

**Importante:** Si restaurás el dump, no hace falta crear usuarios: usá las mismas credenciales que en tu ambiente actual.

### 4.4. Aplicar migraciones (si quedaron pendientes)

```powershell
cd backend
.\venv\Scripts\activate
alembic upgrade head
```

### 4.5. Instalación desde cero (sin dump)

Si no tenés dump:

1. Crear base: `CREATE DATABASE pricing_db_dev;`
2. En `backend`: `python -m venv venv`, `.\venv\Scripts\activate`, `pip install -r requirements.txt`
3. `alembic upgrade head`
4. Crear usuario con el script de la [sección 6](#6-crear-primer-usuario-solo-instalación-nueva)

---

## 5. Configuración de variables de entorno

### Backend – `backend/.env`

Crear `backend/.env`:

```env
DATABASE_URL=postgresql://postgres:TU_PASSWORD@localhost/pricing_db_dev
SECRET_KEY=clave-secreta-para-demo-minimo-32-caracteres
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
ERP_BASE_URL=http://localhost
ERP_PRODUCTOS_ENDPOINT=/consulta?intExpgr_id=64
ERP_STOCK_ENDPOINT=/consulta?opName=ItemStock&intStor_id=1&intItem_id=-1
ENVIRONMENT=development
```

Reemplazá `TU_PASSWORD` por la contraseña de PostgreSQL.

### Frontend – `frontend/.env`

Crear `frontend/.env`:

```env
VITE_API_URL=http://localhost:8002/api
```

---

## 6. Crear primer usuario (solo instalación nueva)

Solo si no restauraste el dump y la base está vacía.

### Script `backend/crear_superadmin.py`

```python
#!/usr/bin/env python3
"""Crea un usuario SUPERADMIN para desarrollo/demo."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.usuario import Usuario
from app.models.rol import Rol
from passlib.context import CryptContext

def crear_superadmin():
    db = SessionLocal()
    pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
    rol = db.query(Rol).filter(Rol.codigo == "SUPERADMIN").first()
    if not rol:
        print("ERROR: Rol SUPERADMIN no existe. ¿Ejecutaste alembic upgrade head?")
        sys.exit(1)
    if db.query(Usuario).filter(Usuario.username == "admin").first():
        print("El usuario 'admin' ya existe.")
        db.close()
        return
    nuevo = Usuario(
        username="admin",
        email="admin@demo.local",
        nombre="Administrador Demo",
        password_hash=pwd.hash("admin123"),
        rol=None,
        rol_id=rol.id,
        auth_provider="local",
        activo=True
    )
    db.add(nuevo)
    db.commit()
    db.close()
    print("Usuario creado: username=admin, password=admin123")

if __name__ == "__main__":
    crear_superadmin()
```

### Ejecutar

```powershell
cd backend
.\venv\Scripts\activate
python crear_superadmin.py
```

Credenciales: **admin** / **admin123**

---

## 7. Arrancar backend y frontend

### Terminal 1 – Backend

```powershell
cd pricing-app
.\start-backend.ps1
```

O manualmente:

```powershell
cd backend
.\venv\Scripts\activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

### Terminal 2 – Frontend

```powershell
cd pricing-app
.\start-frontend.ps1
```

O manualmente:

```powershell
cd frontend
npm install
npm run dev
```

### URLs

- **App:** http://localhost:5173
- **API docs:** http://localhost:8002/api/docs

---

## 8. Verificación y qué esperar

### Con dump restaurado

- Productos, precios, ventas, facturas igual que en tu ambiente.
- Usá las mismas credenciales que en tu PC.

### Con instalación nueva

- Login: `admin` / `admin123`.
- Admin, Facturas de Compra, Clientes, etc. funcionan.
- Productos y dashboards pueden estar vacíos sin ERP/ML/TN.

---

## 9. Solución de problemas

| Problema | Solución |
|----------|----------|
| "could not connect to server" | Verificar que PostgreSQL esté corriendo y `DATABASE_URL` correcta |
| "relation does not exist" | Ejecutar `alembic upgrade head` |
| Frontend no conecta | Backend en 8002, `VITE_API_URL=http://localhost:8002/api` |
| "Usuario o contraseña incorrectos" | Con dump: credenciales reales. Sin dump: ejecutar `crear_superadmin.py` |
| Puerto ocupado | Cambiar puerto: `--port 8003` y actualizar `VITE_API_URL` |
| Ruta de psql distinta | Buscar: `Get-ChildItem -Path "C:\Program Files" -Recurse -Filter "psql.exe"` |

---

## Resumen de comandos

```powershell
# Generar dump
cd DB
mkdir demo -ErrorAction SilentlyContinue
& "C:\Program Files\PostgreSQL\18\bin\pg_dump.exe" -U postgres -d pricing_db_dev -f "demo\pricing_full.sql"

# Restaurar dump
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d pricing_db_dev -f "DB\demo\pricing_full.sql"

# Backend
cd backend
.\venv\Scripts\activate
alembic upgrade head
python crear_superadmin.py   # Solo si es instalación nueva
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload

# Frontend (otra terminal)
cd frontend
npm install
npm run dev
```
