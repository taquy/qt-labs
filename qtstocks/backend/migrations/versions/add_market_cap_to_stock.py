"""add market_cap to stock

Revision ID: add_market_cap_to_stock
Revises: add_unaccent_extension
Create Date: 2024-03-20 10:32:31.123456

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_market_cap_to_stock'
down_revision = 'add_unaccent_extension'
branch_labels = None
depends_on = None


def upgrade():
    # Add market_cap column to stock table
    op.add_column('stock', sa.Column('market_cap', sa.Float(), nullable=True))


def downgrade():
    # Remove market_cap column from stock table
    op.drop_column('stock', 'market_cap') 