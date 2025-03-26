"""add stock portfolio

Revision ID: 004
Revises: 003
Create Date: 2024-03-24 14:15:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime, timezone

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None

def upgrade():
    # Create stock table if it doesn't exist
    if not op.get_bind().dialect.has_table(op.get_bind(), 'stock'):
        op.create_table('stock',
            sa.Column('symbol', sa.String(10), primary_key=True),
            sa.Column('name', sa.String(100), nullable=False),
            sa.Column('icon', sa.String(255), nullable=True),
            sa.Column('exchange', sa.String(50), nullable=True),
            sa.Column('market_cap', sa.Float(), nullable=True),
            sa.Column('last_updated', sa.DateTime(), nullable=True)
        )
    
    # Create stock_stats table if it doesn't exist
    if not op.get_bind().dialect.has_table(op.get_bind(), 'stock_stats'):
        op.create_table('stock_stats',
            sa.Column('symbol', sa.String(10), sa.ForeignKey('stock.symbol'), primary_key=True),
            sa.Column('price', sa.Float(), nullable=True),
            sa.Column('market_cap', sa.Float(), nullable=True),
            sa.Column('eps', sa.Float(), nullable=True),
            sa.Column('pe', sa.Float(), nullable=True),
            sa.Column('pb', sa.Float(), nullable=True),
            sa.Column('last_updated', sa.DateTime(), nullable=True)
        )
    
    # Create stock_portfolio table if it doesn't exist
    if not op.get_bind().dialect.has_table(op.get_bind(), 'stock_portfolio'):
        op.create_table('stock_portfolio',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('user.id'), nullable=False),
            sa.Column('name', sa.String(100), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('user_id', 'name', name='unique_portfolio_name_per_user')
        )
    
    # Create portfolio_stocks association table if it doesn't exist
    if not op.get_bind().dialect.has_table(op.get_bind(), 'portfolio_stocks'):
        op.create_table('portfolio_stocks',
            sa.Column('portfolio_id', sa.Integer(), sa.ForeignKey('stock_portfolio.id'), primary_key=True),
            sa.Column('stock_symbol', sa.String(10), sa.ForeignKey('stock.symbol'), primary_key=True),
            sa.Column('created_at', sa.DateTime(), nullable=True)
        )
    
    # Create user_stock_stats association table if it doesn't exist
    if not op.get_bind().dialect.has_table(op.get_bind(), 'user_stock_stats'):
        op.create_table('user_stock_stats',
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('user.id'), primary_key=True),
            sa.Column('stock_symbol', sa.String(10), sa.ForeignKey('stock_stats.symbol'), primary_key=True),
            sa.Column('created_at', sa.DateTime(), nullable=True)
        )

def downgrade():
    # Drop tables in reverse order if they exist
    if op.get_bind().dialect.has_table(op.get_bind(), 'user_stock_stats'):
        op.drop_table('user_stock_stats')
    if op.get_bind().dialect.has_table(op.get_bind(), 'portfolio_stocks'):
        op.drop_table('portfolio_stocks')
    if op.get_bind().dialect.has_table(op.get_bind(), 'stock_portfolio'):
        op.drop_table('stock_portfolio')
    if op.get_bind().dialect.has_table(op.get_bind(), 'stock_stats'):
        op.drop_table('stock_stats')
    if op.get_bind().dialect.has_table(op.get_bind(), 'stock'):
        op.drop_table('stock') 