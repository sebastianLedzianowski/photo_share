"""Add ban_status column to user table

Revision ID: ce05737cd946
Revises: a61fdcc332d0
Create Date: 2024-03-08 17:49:30.071656

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ce05737cd946'
down_revision: Union[str, None] = 'a61fdcc332d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('ban_status', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'ban_status')
    # ### end Alembic commands ###
