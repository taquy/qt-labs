"""Update schema with correct column names

Revision ID: schema_update_v1
Revises: 
Create Date: 2024-03-19 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'schema_update_v1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Drop existing tables if they exist
    op.execute('DROP TABLE IF EXISTS stock_stats CASCADE')
    op.execute('DROP TABLE IF EXISTS stock CASCADE')
    
    # Create stock table
    op.create_table('stock',
        sa.Column('symbol', sa.String(10), primary_key=True),
        sa.Column('name', sa.String(100)),
        sa.Column('last_updated', sa.DateTime(), nullable=True)
    )
    
    # Create stock_stats table with correct column names
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