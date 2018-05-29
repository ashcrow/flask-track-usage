"""Increase ip_info size

Revision ID: ca514840f404
Revises: 0aedc36acb3f
Create Date: 2018-05-29 11:15:09.515284

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ca514840f404'
down_revision = '0aedc36acb3f'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('flask_usage', 'ip_info', type_=sa.String(1024), existing_type=sa.String(length=128))


def downgrade():
    op.alter_column('flask_usage', 'ip_info', type_=sa.String(128), existing_type=sa.String(length=1024))
