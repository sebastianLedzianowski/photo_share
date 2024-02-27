"""update bool level

Revision ID: 0e447b4659f7
Revises: d4b9334092ad
Create Date: 2024-02-27 15:51:36.762475

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0e447b4659f7'
down_revision: Union[str, None] = 'd4b9334092ad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
