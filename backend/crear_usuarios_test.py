#!/usr/bin/env python3
"""
Script para crear usuarios de prueba para el sistema de Facturas de Compra
Uso: python crear_usuarios_test.py
"""
import sys
import os

# Agregar el directorio backend al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.usuario import Usuario
from app.models.rol import Rol
import bcrypt

# Usuarios a crear
USUARIOS_TEST = [
    {
        "username": "compras",
        "password": "compras123",
        "nombre": "Usuario Compras Test",
        "rol": "COMPRAS"
    },
    {
        "username": "carga",
        "password": "carga123",
        "nombre": "Usuario Carga OC/FC Test",
        "rol": "CARGA_OC_FC_GBP"
    },
    {
        "username": "depo",
        "password": "depo123",
        "nombre": "Usuario Depósito Test",
        "rol": "DEPO"
    },
    {
        "username": "tesoreria",
        "password": "tesoreria123",
        "nombre": "Usuario Tesorería Test",
        "rol": "TESORERIA"
    }
]

def crear_usuarios():
    """Crea los usuarios de prueba"""
    db = SessionLocal()
    
    print("=" * 60)
    print("CREANDO USUARIOS DE PRUEBA PARA FACTURAS DE COMPRA")
    print("=" * 60)
    print()
    
    creados = 0
    existentes = 0
    errores = 0
    
    for usuario_data in USUARIOS_TEST:
        username = usuario_data["username"]
        password = usuario_data["password"]
        nombre = usuario_data["nombre"]
        rol_codigo = usuario_data["rol"]
        
        try:
            # Verificar si el usuario ya existe
            existe = db.query(Usuario).filter(Usuario.username == username).first()
            if existe:
                print(f"[INFO] Usuario '{username}' ya existe, omitiendo...")
                existentes += 1
                continue
            
            # Buscar el rol
            rol_obj = db.query(Rol).filter(Rol.codigo == rol_codigo).first()
            if not rol_obj:
                print(f"[ERROR] Rol '{rol_codigo}' no existe")
                errores += 1
                continue
            
            # Crear hash de la contraseña
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Crear usuario
            nuevo_usuario = Usuario(
                username=username,
                nombre=nombre,
                password_hash=password_hash,
                rol=None,  # Deprecado, usar rol_id
                rol_id=rol_obj.id,
                auth_provider="local",
                activo=True
            )
            
            db.add(nuevo_usuario)
            db.commit()
            db.refresh(nuevo_usuario)
            
            print(f"[OK] Usuario '{username}' creado exitosamente")
            print(f"     Nombre: {nombre}")
            print(f"     Rol: {rol_codigo}")
            print(f"     Password: {password}")
            print()
            
            creados += 1
            
        except Exception as e:
            db.rollback()
            print(f"[ERROR] Error al crear usuario '{username}': {str(e)}")
            errores += 1
            print()
    
    db.close()
    
    print("=" * 60)
    print("RESUMEN:")
    print(f"  [OK] Creados: {creados}")
    print(f"  [INFO] Ya existian: {existentes}")
    print(f"  [ERROR] Errores: {errores}")
    print("=" * 60)

if __name__ == "__main__":
    try:
        crear_usuarios()
    except Exception as e:
        print(f"[ERROR] Error fatal: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
