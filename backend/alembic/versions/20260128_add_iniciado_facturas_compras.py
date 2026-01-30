"""add iniciado flag to facturas_compras

Revision ID: 20260128_add_iniciado
Revises: 0e4585fa9ede
Create Date: 2026-01-28

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '20260128_add_iniciado'
down_revision: Union[str, None] = '0e4585fa9ede'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Verificar si la columna iniciado ya existe (puede existir si se ejecutó la migración inicial 7c95ca8072fc)
    conn = op.get_bind()
    result = conn.execute(sa.text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='facturas_compras' AND column_name='iniciado'
    """))
    
    if result.fetchone() is None:
        # La columna no existe, agregarla
        op.add_column(
            'facturas_compras',
            sa.Column('iniciado', sa.Boolean(), nullable=False, server_default='false')
        )
        op.create_index(
            op.f('ix_facturas_compras_iniciado'),
            'facturas_compras',
            ['iniciado'],
            unique=False,
        )
        # Quitar server_default para futuras inserciones (deja el default en el modelo)
        op.alter_column('facturas_compras', 'iniciado', server_default=None)
    else:
        # La columna ya existe, solo asegurarse de que el índice exista
        result_idx = conn.execute(sa.text("""
            SELECT indexname 
            FROM pg_indexes 
            WHERE tablename='facturas_compras' AND indexname='ix_facturas_compras_iniciado'
        """))
        if result_idx.fetchone() is None:
            op.create_index(
                op.f('ix_facturas_compras_iniciado'),
                'facturas_compras',
                ['iniciado'],
                unique=False,
            )


def downgrade() -> None:
    op.drop_index(op.f('ix_facturas_compras_iniciado'), table_name='facturas_compras')
    op.drop_column('facturas_compras', 'iniciado')

