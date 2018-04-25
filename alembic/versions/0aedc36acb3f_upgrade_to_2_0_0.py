"""Upgrade to 2.0.0

Revision ID: 0aedc36acb3f
Revises: 07c46d368ba4
Create Date: 2018-04-25 09:39:38.879327

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0aedc36acb3f'
down_revision = '07c46d368ba4'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('flask_usage', sa.Column('track_var', sa.String(128), nullable=True))
    op.add_column('flask_usage', sa.Column('username', sa.String(128), nullable=True))

def downgrade():
    op.drop_column('flask_usage', 'track_var')
    op.drop_column('flask_usage', 'username')
