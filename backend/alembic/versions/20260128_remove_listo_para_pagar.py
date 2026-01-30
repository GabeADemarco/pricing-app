"""remove listo_para_pagar column from facturas_compras

Revision ID: 20260128_remove_listo_para_pagar
Revises: 20260128_add_iniciado
Create Date: 2026-01-28

Elimina la columna listo_para_pagar ya que se reemplaza por el campo 'iniciado'
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '20260128_remove_listo_para_pagar'
down_revision: Union[str, None] = '20260128_add_iniciado'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Eliminar índice primero
    op.drop_index(op.f('ix_facturas_compras_listo_para_pagar'), table_name='facturas_compras', if_exists=True)
    # Eliminar columna
    op.drop_column('facturas_compras', 'listo_para_pagar')


def downgrade() -> None:
    # Recrear columna (si se necesita revertir)
    op.add_column(
        'facturas_compras',
        sa.Column('listo_para_pagar', sa.Boolean(), nullable=False, server_default='false')
    )
    op.create_index(
        op.f('ix_facturas_compras_listo_para_pagar'),
        'facturas_compras',
        ['listo_para_pagar'],
        unique=False,
    )
    op.alter_column('facturas_compras', 'listo_para_pagar', server_default=None)
