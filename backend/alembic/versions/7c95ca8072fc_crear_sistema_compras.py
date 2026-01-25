"""crear sistema facturas compras

Revision ID: 7c95ca8072fc
Revises: ed9b542b9f3f
Create Date: 2025-01-27

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '7c95ca8072fc'
down_revision: Union[str, None] = 'ed9b542b9f3f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ========================================
    # 1. Crear ENUMs
    # ========================================
    razon_social_enum = postgresql.ENUM('Grupo Gauss', 'Pastoriza', name='razonsocial')
    razon_social_enum.create(op.get_bind(), checkfirst=True)
    
    logistica_enum = postgresql.ENUM('GAUSS', 'PROVEEDOR', 'TERCERO', name='logistica')
    logistica_enum.create(op.get_bind(), checkfirst=True)
    
    prioridad_enum = postgresql.ENUM('NORMAL', 'URGENTE', name='prioridad')
    prioridad_enum.create(op.get_bind(), checkfirst=True)
    
    forma_pago_enum = postgresql.ENUM('CONTADO', 'CHEQUE', 'CTA CTE', name='formapago')
    forma_pago_enum.create(op.get_bind(), checkfirst=True)

    # ========================================
    # 2. Crear tabla facturas_compras
    # ========================================
    op.create_table(
        'facturas_compras',
        sa.Column('id', sa.Integer(), nullable=False),
        
        # Campos de COMPRAS (carga inicial)
        sa.Column('razon_social', razon_social_enum, nullable=False),
        sa.Column('fecha_carga', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('proveedor_id', sa.Integer(), nullable=True),
        sa.Column('proveedor_nombre', sa.String(255), nullable=True),
        sa.Column('nro_proforma', sa.String(100), nullable=True),
        sa.Column('link_proforma', sa.String(500), nullable=True),
        sa.Column('logistica', logistica_enum, nullable=True),
        sa.Column('prioridad', prioridad_enum, nullable=True, server_default='NORMAL'),
        sa.Column('nro_factura', sa.String(100), nullable=True),
        sa.Column('link_factura', sa.String(500), nullable=True),
        sa.Column('forma_pago', forma_pago_enum, nullable=True),
        sa.Column('plazo', sa.String(100), nullable=True),
        sa.Column('tipo_cambio', sa.String(100), nullable=True),
        sa.Column('listo_para_pagar', sa.Boolean(), nullable=False, server_default='false'),
        
        # Campos de CARGA_OC_FC_GBP (carga de OC y FC en GBP/ERP)
        sa.Column('oc_cargada', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('oc_fecha', sa.DateTime(timezone=True), nullable=True),
        sa.Column('fc_cargada', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('fc_fecha', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tiene_devoluciones', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('rma_id', sa.String(100), nullable=True),
        
        # Campos de DEPO (Retiro y Control)
        sa.Column('retirado', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('retirado_fecha', sa.DateTime(timezone=True), nullable=True),
        sa.Column('controlado', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('controlado_fecha', sa.DateTime(timezone=True), nullable=True),
        
        # Campos de ADMIN (Pago)
        sa.Column('pagado', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('pagado_fecha', sa.DateTime(timezone=True), nullable=True),
        
        # Auditoría
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('creado_por_id', sa.Integer(), nullable=True),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['creado_por_id'], ['usuarios.id'], name='fk_compras_creado_por_id')
    )
    
    # Índices para facturas_compras
    op.create_index(op.f('ix_facturas_compras_id'), 'facturas_compras', ['id'], unique=False)
    op.create_index(op.f('ix_facturas_compras_razon_social'), 'facturas_compras', ['razon_social'], unique=False)
    op.create_index(op.f('ix_facturas_compras_fecha_carga'), 'facturas_compras', ['fecha_carga'], unique=False)
    op.create_index(op.f('ix_facturas_compras_proveedor_id'), 'facturas_compras', ['proveedor_id'], unique=False)
    op.create_index(op.f('ix_facturas_compras_listo_para_pagar'), 'facturas_compras', ['listo_para_pagar'], unique=False)
    op.create_index(op.f('ix_facturas_compras_oc_cargada'), 'facturas_compras', ['oc_cargada'], unique=False)
    op.create_index(op.f('ix_facturas_compras_fc_cargada'), 'facturas_compras', ['fc_cargada'], unique=False)
    op.create_index(op.f('ix_facturas_compras_retirado'), 'facturas_compras', ['retirado'], unique=False)
    op.create_index(op.f('ix_facturas_compras_controlado'), 'facturas_compras', ['controlado'], unique=False)
    op.create_index(op.f('ix_facturas_compras_pagado'), 'facturas_compras', ['pagado'], unique=False)
    op.create_index(op.f('ix_facturas_compras_creado_por_id'), 'facturas_compras', ['creado_por_id'], unique=False)

    # ========================================
    # 3. Crear tabla facturas_compras_observaciones
    # ========================================
    op.create_table(
        'facturas_compras_observaciones',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('factura_compra_id', sa.Integer(), nullable=False),
        sa.Column('rol_codigo', sa.String(50), nullable=False),
        sa.Column('usuario_id', sa.Integer(), nullable=True),
        sa.Column('observacion', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['factura_compra_id'], ['facturas_compras.id'], name='fk_facturas_compras_observaciones_factura_compra_id', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], name='fk_facturas_compras_observaciones_usuario_id')
    )
    
    # Índices para facturas_compras_observaciones
    op.create_index(op.f('ix_facturas_compras_observaciones_id'), 'facturas_compras_observaciones', ['id'], unique=False)
    op.create_index(op.f('ix_facturas_compras_observaciones_factura_compra_id'), 'facturas_compras_observaciones', ['factura_compra_id'], unique=False)
    op.create_index(op.f('ix_facturas_compras_observaciones_rol_codigo'), 'facturas_compras_observaciones', ['rol_codigo'], unique=False)
    op.create_index(op.f('ix_facturas_compras_observaciones_usuario_id'), 'facturas_compras_observaciones', ['usuario_id'], unique=False)
    op.create_index(op.f('ix_facturas_compras_observaciones_created_at'), 'facturas_compras_observaciones', ['created_at'], unique=False)


def downgrade() -> None:
    # Eliminar tablas en orden inverso
    op.drop_index(op.f('ix_facturas_compras_observaciones_created_at'), table_name='facturas_compras_observaciones')
    op.drop_index(op.f('ix_facturas_compras_observaciones_usuario_id'), table_name='facturas_compras_observaciones')
    op.drop_index(op.f('ix_facturas_compras_observaciones_rol_codigo'), table_name='facturas_compras_observaciones')
    op.drop_index(op.f('ix_facturas_compras_observaciones_factura_compra_id'), table_name='facturas_compras_observaciones')
    op.drop_index(op.f('ix_facturas_compras_observaciones_id'), table_name='facturas_compras_observaciones')
    op.drop_table('facturas_compras_observaciones')
    
    op.drop_index(op.f('ix_facturas_compras_creado_por_id'), table_name='facturas_compras')
    op.drop_index(op.f('ix_facturas_compras_pagado'), table_name='facturas_compras')
    op.drop_index(op.f('ix_facturas_compras_controlado'), table_name='facturas_compras')
    op.drop_index(op.f('ix_facturas_compras_retirado'), table_name='facturas_compras')
    op.drop_index(op.f('ix_facturas_compras_fc_cargada'), table_name='facturas_compras')
    op.drop_index(op.f('ix_facturas_compras_oc_cargada'), table_name='facturas_compras')
    op.drop_index(op.f('ix_facturas_compras_listo_para_pagar'), table_name='facturas_compras')
    op.drop_index(op.f('ix_facturas_compras_proveedor_id'), table_name='facturas_compras')
    op.drop_index(op.f('ix_facturas_compras_fecha_carga'), table_name='facturas_compras')
    op.drop_index(op.f('ix_facturas_compras_razon_social'), table_name='facturas_compras')
    op.drop_index(op.f('ix_facturas_compras_id'), table_name='facturas_compras')
    op.drop_table('facturas_compras')
    
    # Eliminar ENUMs
    op.execute('DROP TYPE IF EXISTS formapago CASCADE')
    op.execute('DROP TYPE IF EXISTS prioridad CASCADE')
    op.execute('DROP TYPE IF EXISTS logistica CASCADE')
    op.execute('DROP TYPE IF EXISTS razonsocial CASCADE')
