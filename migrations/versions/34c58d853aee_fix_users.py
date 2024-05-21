"""fix users

Revision ID: 34c58d853aee
Revises: edf16c0a1340
Create Date: 2024-02-13 02:37:51.060991

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '34c58d853aee'
down_revision: Union[str, None] = 'edf16c0a1340'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('disabled', sa.Boolean(), nullable=True))
    op.alter_column('users', 'password',
               existing_type=postgresql.BYTEA(),
               type_=sa.Text(),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'password',
               existing_type=sa.Text(),
               type_=postgresql.BYTEA(),
               existing_nullable=False)
    op.drop_column('users', 'disabled')
    # ### end Alembic commands ###
