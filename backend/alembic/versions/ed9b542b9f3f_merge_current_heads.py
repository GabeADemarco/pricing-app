"""merge current heads

Revision ID: ed9b542b9f3f
Revises: 20260123_exportar_pvp, create_tb_item_association
Create Date: 2026-01-25 08:35:07.878937

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ed9b542b9f3f'
down_revision: Union[str, None] = ('20260123_exportar_pvp', 'create_tb_item_association')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
