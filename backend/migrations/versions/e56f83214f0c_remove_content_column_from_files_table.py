"""Remove content column from files table

Revision ID: e56f83214f0c
Revises: 81a97c49be34
Create Date: 2024-11-13 18:55:19.230912

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e56f83214f0c'
down_revision = '81a97c49be34'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('files', schema=None) as batch_op:
        batch_op.alter_column('storage_path',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('files', schema=None) as batch_op:
        batch_op.alter_column('storage_path',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)

    # ### end Alembic commands ###