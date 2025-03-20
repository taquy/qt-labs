"""add icon and exchange to stock

Revision ID: add_icon_exchange_to_stock
Revises: initial_schema
Create Date: 2024-03-20 10:32:31.123456

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_icon_exchange_to_stock'
down_revision = 'initial_schema'
branch_labels = None
depends_on = None


def upgrade():
    # Add icon and exchange columns to stock table
    op.add_column('stock', sa.Column('icon', sa.String(length=255), nullable=True))
    op.add_column('stock', sa.Column('exchange', sa.String(length=50), nullable=True))


def downgrade():
    # Remove icon and exchange columns from stock table
    op.drop_column('stock', 'exchange')
    op.drop_column('stock', 'icon') 