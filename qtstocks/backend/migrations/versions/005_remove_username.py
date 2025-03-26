"""Remove username from user table

Revision ID: 005
Revises: 004
Create Date: 2024-03-22 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None

def upgrade():
    # Drop the username column
    op.drop_column('user', 'username')

def downgrade():
    # Add back the username column
    op.add_column('user', sa.Column('username', sa.String(80), nullable=False, unique=True)) 