"""agregar roles y permisos facturas compras

Revision ID: 0e4585fa9ede
Revises: 7c95ca8072fc
Create Date: 2025-01-27

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0e4585fa9ede'
down_revision: Union[str, None] = '7c95ca8072fc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Nuevos permisos de facturas de compra
NUEVOS_PERMISOS = [
    ("facturas_compras.ver", "Ver facturas de compra", "Acceso a la lista de facturas de compra", "facturas_compras", 80, False),
    ("facturas_compras.crear", "Crear factura de compra", "Crear nueva factura de compra", "facturas_compras", 81, False),
    ("facturas_compras.editar_campos_compras", "Editar campos de COMPRAS", "Editar campos iniciales de la factura (razón social, proveedor, proforma, etc.)", "facturas_compras", 82, False),
    ("facturas_compras.marcar_listo_pagar", "Marcar listo para pagar", "Marcar factura como lista para pagar e iniciar el proceso", "facturas_compras", 83, False),
    ("facturas_compras.cargar_oc", "Cargar OC en GBP", "Cargar Orden de Compra en el sistema GBP/ERP", "facturas_compras", 84, False),
    ("facturas_compras.cargar_fc", "Cargar FC en GBP", "Cargar Factura en el sistema GBP/ERP", "facturas_compras", 85, False),
    ("facturas_compras.marcar_retirado", "Marcar como retirado", "Marcar factura como retirada/recibida en depósito", "facturas_compras", 86, False),
    ("facturas_compras.marcar_controlado", "Marcar como controlado", "Marcar factura como controlada físicamente en depósito", "facturas_compras", 87, False),
    ("facturas_compras.marcar_pagado", "Marcar como pagado", "Marcar factura como pagada", "facturas_compras", 88, False),
    ("facturas_compras.agregar_observacion", "Agregar observación", "Agregar observaciones a facturas de compra", "facturas_compras", 89, False),
    ("facturas_compras.ver_observaciones", "Ver observaciones", "Ver observaciones de facturas de compra", "facturas_compras", 90, False),
]

# Nuevos roles
NUEVOS_ROLES = [
    ("COMPRAS", "Compras", "Rol para carga inicial de facturas de compra", 6),
    ("CARGA_OC_FC_GBP", "Carga OC y FC en GBP", "Rol para cargar Orden de Compra y Factura en el sistema GBP/ERP", 7),
    ("DEPO", "Depósito", "Rol para retiro y control físico de facturas de compra", 8),
    ("TESORERIA", "Tesorería", "Rol del área de Administración y Tesorería para marcar pagos de facturas de compra", 9),
]


def upgrade() -> None:
    # ========================================
    # 0. Agregar "facturas_compras" al ENUM categoriapermiso si no existe
    # NOTA: PostgreSQL requiere commit antes de usar nuevos valores de ENUM.
    # Si este paso falla, ejecutar manualmente en pgAdmin:
    # ALTER TYPE categoriapermiso ADD VALUE IF NOT EXISTS 'facturas_compras';
    # ========================================
    conn = op.get_bind()
    # Verificar si el valor ya existe en el ENUM
    result = conn.execute(sa.text("""
        SELECT 1 FROM pg_enum 
        WHERE enumlabel = 'facturas_compras' 
        AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'categoriapermiso')
    """))
    if result.fetchone() is None:
        # Intentar agregar el valor al ENUM
        # Si falla con "unsafe use of new value", ejecutar manualmente antes de esta migración
        try:
            op.execute("ALTER TYPE categoriapermiso ADD VALUE IF NOT EXISTS 'facturas_compras'")
        except Exception as e:
            if "UnsafeNewEnumValueUsage" in str(e) or "unsafe use" in str(e).lower():
                raise Exception(
                    "PostgreSQL requiere commit antes de usar nuevos valores de ENUM. "
                    "Por favor ejecuta manualmente en pgAdmin:\n"
                    "ALTER TYPE categoriapermiso ADD VALUE IF NOT EXISTS 'facturas_compras';\n"
                    "Luego vuelve a ejecutar esta migración."
                ) from e
            raise
    
    # ========================================
    # 1. Insertar nuevos permisos
    # ========================================
    for codigo, nombre, descripcion, categoria, orden, es_critico in NUEVOS_PERMISOS:
        op.execute(f"""
            INSERT INTO permisos (codigo, nombre, descripcion, categoria, orden, es_critico)
            VALUES ('{codigo}', '{nombre}', '{descripcion}', '{categoria}', {orden}, {str(es_critico).lower()})
            ON CONFLICT (codigo) DO NOTHING
        """)

    # ========================================
    # 2. Insertar nuevos roles
    # ========================================
    for codigo, nombre, descripcion, orden in NUEVOS_ROLES:
        op.execute(f"""
            INSERT INTO roles (codigo, nombre, descripcion, es_sistema, orden, activo)
            VALUES ('{codigo}', '{nombre}', '{descripcion}', false, {orden}, true)
            ON CONFLICT (codigo) DO NOTHING
        """)

    # ========================================
    # 3. Asignar permisos a ADMIN (ya tiene facturas_compras.* en PERMISOS_POR_ROL)
    # ========================================
    op.execute("""
        INSERT INTO roles_permisos_base (rol_id, permiso_id)
        SELECT r.id, p.id
        FROM roles r, permisos p
        WHERE r.codigo = 'ADMIN'
        AND p.codigo LIKE 'facturas_compras.%'
        ON CONFLICT DO NOTHING
    """)

    # ========================================
    # 4. Asignar permisos a COMPRAS
    # ========================================
    op.execute("""
        INSERT INTO roles_permisos_base (rol_id, permiso_id)
        SELECT r.id, p.id
        FROM roles r, permisos p
        WHERE r.codigo = 'COMPRAS'
        AND p.codigo IN (
            'facturas_compras.ver',
            'facturas_compras.crear',
            'facturas_compras.editar_campos_compras',
            'facturas_compras.marcar_listo_pagar',
            'facturas_compras.agregar_observacion',
            'facturas_compras.ver_observaciones'
        )
        ON CONFLICT DO NOTHING
    """)

    # ========================================
    # 5. Asignar permisos a CARGA_OC_FC_GBP
    # ========================================
    op.execute("""
        INSERT INTO roles_permisos_base (rol_id, permiso_id)
        SELECT r.id, p.id
        FROM roles r, permisos p
        WHERE r.codigo = 'CARGA_OC_FC_GBP'
        AND p.codigo IN (
            'facturas_compras.ver',
            'facturas_compras.cargar_oc',
            'facturas_compras.cargar_fc',
            'facturas_compras.agregar_observacion',
            'facturas_compras.ver_observaciones'
        )
        ON CONFLICT DO NOTHING
    """)

    # ========================================
    # 6. Asignar permisos a DEPO
    # ========================================
    op.execute("""
        INSERT INTO roles_permisos_base (rol_id, permiso_id)
        SELECT r.id, p.id
        FROM roles r, permisos p
        WHERE r.codigo = 'DEPO'
        AND p.codigo IN (
            'facturas_compras.ver',
            'facturas_compras.marcar_retirado',
            'facturas_compras.marcar_controlado',
            'facturas_compras.agregar_observacion',
            'facturas_compras.ver_observaciones'
        )
        ON CONFLICT DO NOTHING
    """)

    # ========================================
    # 7. Asignar permisos a TESORERIA
    # ========================================
    op.execute("""
        INSERT INTO roles_permisos_base (rol_id, permiso_id)
        SELECT r.id, p.id
        FROM roles r, permisos p
        WHERE r.codigo = 'TESORERIA'
        AND p.codigo IN (
            'facturas_compras.ver',
            'facturas_compras.marcar_pagado',
            'facturas_compras.agregar_observacion',
            'facturas_compras.ver_observaciones'
        )
        ON CONFLICT DO NOTHING
    """)


def downgrade() -> None:
    # Eliminar asignaciones de permisos a roles
    op.execute("""
        DELETE FROM roles_permisos_base
        WHERE permiso_id IN (
            SELECT id FROM permisos WHERE codigo LIKE 'facturas_compras.%'
        )
    """)

    # Eliminar roles nuevos
    op.execute("""
        DELETE FROM roles
        WHERE codigo IN ('COMPRAS', 'CARGA_OC_FC_GBP', 'DEPO', 'TESORERIA')
    """)

    # Eliminar permisos nuevos
    op.execute("""
        DELETE FROM permisos
        WHERE codigo LIKE 'facturas_compras.%'
    """)
