"""Initial schema

Revision ID: initial_schema
Revises: 
Create Date: 2024-03-20 10:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create user table
    op.create_table('user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=80), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('google_id', sa.String(length=255), nullable=True),
        sa.Column('name', sa.String(length=64), nullable=True),
        sa.Column('is_admin', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('google_id')
    )

    # Create stock table
    op.create_table('stock',
        sa.Column('symbol', sa.String(length=10), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=True),
        sa.Column('last_updated', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('symbol')
    )

    # Create stock_stats table
    op.create_table('stock_stats',
        sa.Column('symbol', sa.String(length=10), nullable=False),
        sa.Column('price', sa.Float(), nullable=True),
        sa.Column('market_cap', sa.Float(), nullable=True),
        sa.Column('eps', sa.Float(), nullable=True),
        sa.Column('pe', sa.Float(), nullable=True),
        sa.Column('pb', sa.Float(), nullable=True),
        sa.Column('last_updated', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('symbol')
    )

    # Create user_stock_stats table
    op.create_table('user_stock_stats',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('stock_symbol', sa.String(length=10), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.ForeignKeyConstraint(['stock_symbol'], ['stock_stats.symbol'], ),
        sa.PrimaryKeyConstraint('user_id', 'stock_symbol')
    )

    # Create user_settings table
    op.create_table('user_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('setting_key', sa.String(length=50), nullable=False),
        sa.Column('setting_value', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'setting_key', name='unique_user_setting')
    )

    # Create user_jwt table
    op.create_table('user_jwt',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(length=500), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token')
    )


def downgrade():
    op.drop_table('user_jwt')
    op.drop_table('user_settings')
    op.drop_table('user_stock_stats')
    op.drop_table('stock_stats')
    op.drop_table('stock')
    op.drop_table('user') 