"""Update schema to use symbol as primary key

Revision ID: update_schema_symbol_pk
Revises: 
Create Date: 2024-03-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'update_schema_symbol_pk'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Drop existing tables in correct order
    op.drop_table('stock_stats')
    op.drop_table('stock')
    
    # Create new stock table with symbol as primary key
    op.create_table('stock',
        sa.Column('symbol', sa.String(10), primary_key=True),
        sa.Column('name', sa.String(100)),
        sa.Column('last_updated', sa.DateTime(), nullable=True)
    )
    
    # Create new stock_stats table with symbol as primary key and foreign key
    op.create_table('stock_stats',
        sa.Column('symbol', sa.String(10), sa.ForeignKey('stock.symbol'), primary_key=True),
        sa.Column('price', sa.Float()),
        sa.Column('market_cap', sa.Float()),
        sa.Column('eps', sa.Float()),
        sa.Column('pe', sa.Float()),
        sa.Column('pb', sa.Float()),
        sa.Column('last_updated', sa.DateTime(), nullable=True)
    )


def downgrade():
    # Drop tables in correct order
    op.drop_table('stock_stats')
    op.drop_table('stock') 