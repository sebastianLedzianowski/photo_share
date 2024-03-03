"""add picture_edited_url

Revision ID: e87aac741e3e
Revises: 9823fc072f4f
Create Date: 2024-03-02 15:18:38.244210

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e87aac741e3e'
down_revision: Union[str, None] = '9823fc072f4f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('picture', sa.Column('picture_edited_url', sa.String(length=255), nullable=True))
    op.drop_column('picture', 'picture_url_eddited')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('picture', sa.Column('picture_url_eddited', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
    op.drop_column('picture', 'picture_edited_url')
    # ### end Alembic commands ###