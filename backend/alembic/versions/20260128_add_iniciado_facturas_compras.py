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
    # Agregar columna iniciado a facturas_compras
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


def downgrade() -> None:
    op.drop_index(op.f('ix_facturas_compras_iniciado'), table_name='facturas_compras')
    op.drop_column('facturas_compras', 'iniciado')

