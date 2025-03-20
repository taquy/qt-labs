"""add stock exchanges view

Revision ID: add_stock_exchanges_view
Revises: add_icon_exchange_to_stock
Create Date: 2024-03-20 10:32:31.123456

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_stock_exchanges_view'
down_revision = 'add_icon_exchange_to_stock'
branch_labels = None
depends_on = None


def upgrade():
    # Create view for distinct exchanges
    op.execute("""
        CREATE OR REPLACE VIEW stock_exchanges AS
        SELECT DISTINCT exchange
        FROM stock
        WHERE exchange IS NOT NULL
        ORDER BY exchange;
    """)


def downgrade():
    # Drop the view
    op.execute("DROP VIEW IF EXISTS stock_exchanges;") 