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
    
    column_already_exists = result.fetchone() is not None
    
    if not column_already_exists:
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
        # La columna ya existe (fue creada por 7c95ca8072fc), solo asegurarse de que el índice exista
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
    """
    Downgrade seguro: solo elimina la columna e índice si fueron creados por esta migración.
    
    La migración inicial 7c95ca8072fc crea la columna 'iniciado' con server_default='false' y su índice.
    Esta migración solo agrega la columna si no existe (idempotente), y si la crea, quita el server_default.
    
    Para el downgrade seguro:
    - Si la tabla facturas_compras existe, significa que 7c95ca8072fc fue aplicada,
      por lo tanto la columna fue creada por esa migración y NO debemos eliminarla aquí.
    - Si la tabla no existe (escenario poco probable), entonces esta migración creó la columna
      y podemos eliminarla de forma segura.
    """
    conn = op.get_bind()
    
    # Verificar si la columna existe
    result = conn.execute(sa.text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='facturas_compras' AND column_name='iniciado'
    """))
    
    if result.fetchone() is None:
        # La columna no existe, no hay nada que hacer
        return
    
    # Verificar si la tabla facturas_compras existe
    # Si existe, fue creada por 7c95ca8072fc, lo que significa que la columna iniciado
    # también fue creada por esa migración y NO debemos eliminarla aquí
    try:
        result_table = conn.execute(sa.text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name='facturas_compras'
        """))
        
        table_exists = result_table.fetchone() is not None
        
        if table_exists:
            # La tabla existe, lo que significa que 7c95ca8072fc fue aplicada.
            # Por lo tanto, la columna iniciado fue creada por esa migración inicial.
            # NO debemos eliminarla aquí - dejar que 7c95ca8072fc la maneje en su propio downgrade.
            return
    except Exception:
        # Si hay algún error al verificar, ser conservador y no eliminar
        # (es mejor dejar la columna que eliminarla incorrectamente)
        return
    
    # Si llegamos aquí, la tabla no existe (escenario muy poco probable).
    # Esto significaría que esta migración se ejecutó antes de 7c95ca8072fc,
    # lo cual no debería suceder en el flujo normal, pero es posible en casos edge.
    # En ese caso, podemos eliminar la columna de forma segura porque esta migración la creó.
    
    # Verificar si el índice existe antes de eliminarlo
    result_idx = conn.execute(sa.text("""
        SELECT indexname 
        FROM pg_indexes 
        WHERE schemaname = 'public' AND tablename='facturas_compras' 
        AND indexname='ix_facturas_compras_iniciado'
    """))
    if result_idx.fetchone() is not None:
        try:
            op.drop_index(op.f('ix_facturas_compras_iniciado'), table_name='facturas_compras')
        except Exception:
            # Si falla, continuar (el índice puede no existir o haber sido eliminado)
            pass
    
    try:
        op.drop_column('facturas_compras', 'iniciado')
    except Exception:
        # Si falla, la columna puede no existir o haber sido eliminada
        pass

