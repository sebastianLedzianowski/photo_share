"""fix Rating.data

Revision ID: 3222bc834d8c
Revises: 86beb3801306
Create Date: 2024-03-09 19:46:14.098815

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '3222bc834d8c'
down_revision: Union[str, None] = '86beb3801306'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Deleting an existing 'date' column
    op.drop_column('rating', 'data')
    # Adding a new Integer 'rat' column
    op.add_column('rating', sa.Column('rat', sa.Integer(), nullable=True))

def downgrade() -> None:
    # Removing the 'rat' column
    op.drop_column('rating', 'rat')
    # Restoring the 'date' column as JSON
    op.add_column('rating', sa.Column('data', postgresql.JSON(astext_type=sa.Text()), nullable=True))
