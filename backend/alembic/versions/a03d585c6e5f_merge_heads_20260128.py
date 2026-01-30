"""merge_heads_20260128

Revision ID: a03d585c6e5f
Revises: 20250129_tn_lowercase, 20260128_remove_listo_para_pagar, 20260128_rename_isactive
Create Date: 2026-01-30 06:36:42.301862

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a03d585c6e5f'
down_revision: Union[str, None] = ('20250129_tn_lowercase', '20260128_remove_listo_para_pagar', '20260128_rename_isactive')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
