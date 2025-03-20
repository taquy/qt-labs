"""add unaccent extension

Revision ID: add_unaccent_extension
Revises: add_stock_exchanges_view
Create Date: 2024-03-20 10:32:31.123456

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_unaccent_extension'
down_revision = 'add_stock_exchanges_view'
branch_labels = None
depends_on = None


def upgrade():
    # Create unaccent extension
    op.execute('CREATE EXTENSION IF NOT EXISTS unaccent;')


def downgrade():
    # Drop unaccent extension
    op.execute('DROP EXTENSION IF EXISTS unaccent;') 