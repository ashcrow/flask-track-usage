"""Increase sql path column length to 128

Revision ID: 799310dca712
Revises: ca514840f404
Create Date: 2020-04-09 11:34:05.456439

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '799310dca712'
down_revision = 'ca514840f404'
branch_labels = None
depends_on = None



def upgrade():
    op.alter_column('flask_usage', 'path', type_=sa.String(128), existing_type=sa.String(length=32))


def downgrade():
    op.alter_column('flask_usage', 'path', type_=sa.String(32), existing_type=sa.String(length=128))
