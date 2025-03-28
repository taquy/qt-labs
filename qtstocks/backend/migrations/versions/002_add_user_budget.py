"""002_add_user_budget

Revision ID: 002
Revises: 001
Create Date: 2024-03-21 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None

def upgrade():
    # Add budget column to user table with default value 0.0
    op.add_column('user', sa.Column('budget', sa.Float(), nullable=False, server_default='0.0'))

def downgrade():
    # Remove budget column from user table
    op.drop_column('user', 'budget') 