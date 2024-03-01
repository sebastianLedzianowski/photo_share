"""pictures_upgrade

Revision ID: c2082ca6ef35
Revises: 77ae5d54f233
Create Date: 2024-02-29 20:46:53.733093

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c2082ca6ef35'
down_revision: Union[str, None] = '77ae5d54f233'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
