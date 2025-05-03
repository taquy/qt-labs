"""create stock exchanges view

Revision ID: 004
Revises: 003
Create Date: 2024-03-21 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    # Create stock_exchanges view
    op.execute("""
        CREATE OR REPLACE VIEW stock_exchanges AS
        SELECT DISTINCT exchange
        FROM stock
        WHERE exchange IS NOT NULL
        ORDER BY exchange;
    """)


def downgrade():
    # Drop stock_exchanges view
    op.execute("""
        DROP VIEW IF EXISTS stock_exchanges;
    """) 