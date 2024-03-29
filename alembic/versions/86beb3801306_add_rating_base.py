"""add Rating(Base)

Revision ID: 86beb3801306
Revises: 144a96c47d22
Create Date: 2024-03-09 16:44:38.742700

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '86beb3801306'
down_revision: Union[str, None] = '144a96c47d22'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('rating',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('picture_id', sa.Integer(), nullable=True),
    sa.Column('data', sa.JSON(), nullable=True),
    sa.ForeignKeyConstraint(['picture_id'], ['picture.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rating_id'), 'rating', ['id'], unique=False)
    op.drop_column('picture', 'rating')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('picture', sa.Column('rating', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_index(op.f('ix_rating_id'), table_name='rating')
    op.drop_table('rating')
    # ### end Alembic commands ###
