"""Initial database schema

Revision ID: 000
Revises: 
Create Date: 2023-04-30 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '000'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create user table
    op.create_table('user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('name', sa.String(length=120), nullable=True),
        sa.Column('password_hash', sa.String(length=128), nullable=True),
        sa.Column('google_id', sa.String(length=100), nullable=True),
        sa.Column('is_admin', sa.Boolean(), nullable=True, default=False),
        sa.Column('budget', sa.Float(), nullable=True, default=0.0),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=sa.text('now()')),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('google_id')
    )

    # Create stock table
    op.create_table('stock',
        sa.Column('symbol', sa.String(length=10), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('icon', sa.String(length=255), nullable=True),
        sa.Column('exchange', sa.String(length=50), nullable=True),
        sa.Column('market_cap', sa.Float(), nullable=True),
        sa.Column('last_updated', sa.DateTime(), nullable=True, default=sa.text('now()')),
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
        sa.Column('last_updated', sa.DateTime(), nullable=True, default=sa.text('now()')),
        sa.ForeignKeyConstraint(['symbol'], ['stock.symbol'], ),
        sa.PrimaryKeyConstraint('symbol')
    )

    # Create stock_portfolio table
    op.create_table('stock_portfolio',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'name', name='unique_portfolio_name_per_user')
    )

    # Create user_settings table
    op.create_table('user_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('setting_key', sa.String(length=50), nullable=False),
        sa.Column('setting_value', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'setting_key', name='unique_user_setting')
    )

    # Create user_jwt table
    op.create_table('user_jwt',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(length=500), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.text('now()')),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token')
    )

    # Create role table
    op.create_table('role',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # Create permission table
    op.create_table('permission',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('resource', sa.String(length=50), nullable=False),
        sa.Column('action', sa.String(length=20), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # Create payment table
    op.create_table('payment',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=True),
        sa.Column('payment_method', sa.String(length=50), nullable=False),
        sa.Column('transaction_id', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('payment_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create product table
    op.create_table('product',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=True),
        sa.Column('interval', sa.String(length=20), nullable=False),
        sa.Column('features', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )

    # Create subscription table
    op.create_table('subscription',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('auto_renew', sa.Boolean(), nullable=True, default=True),
        sa.Column('payment_id', sa.Integer(), nullable=True),
        sa.Column('subscription_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=sa.text('now()')),
        sa.ForeignKeyConstraint(['payment_id'], ['payment.id'], ),
        sa.ForeignKeyConstraint(['product_id'], ['product.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create association tables
    op.create_table('user_stock_stats',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('stock_symbol', sa.String(length=10), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.text('now()')),
        sa.ForeignKeyConstraint(['stock_symbol'], ['stock_stats.symbol'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('user_id', 'stock_symbol')
    )

    op.create_table('portfolio_stocks',
        sa.Column('portfolio_id', sa.Integer(), nullable=False),
        sa.Column('stock_symbol', sa.String(length=10), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.text('now()')),
        sa.ForeignKeyConstraint(['portfolio_id'], ['stock_portfolio.id'], ),
        sa.ForeignKeyConstraint(['stock_symbol'], ['stock.symbol'], ),
        sa.PrimaryKeyConstraint('portfolio_id', 'stock_symbol')
    )

    op.create_table('product_roles',
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.text('now()')),
        sa.ForeignKeyConstraint(['product_id'], ['product.id'], ),
        sa.ForeignKeyConstraint(['role_id'], ['role.id'], ),
        sa.PrimaryKeyConstraint('product_id', 'role_id')
    )

    op.create_table('role_permissions',
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('permission_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.text('now()')),
        sa.ForeignKeyConstraint(['permission_id'], ['permission.id'], ),
        sa.ForeignKeyConstraint(['role_id'], ['role.id'], ),
        sa.PrimaryKeyConstraint('role_id', 'permission_id')
    )

    op.create_table('user_roles',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.text('now()')),
        sa.ForeignKeyConstraint(['role_id'], ['role.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('user_id', 'role_id')
    )

def downgrade():
    # Drop all tables in reverse order
    op.drop_table('user_roles')
    op.drop_table('role_permissions')
    op.drop_table('product_roles')
    op.drop_table('portfolio_stocks')
    op.drop_table('user_stock_stats')
    op.drop_table('subscription')
    op.drop_table('product')
    op.drop_table('payment')
    op.drop_table('permission')
    op.drop_table('role')
    op.drop_table('user_jwt')
    op.drop_table('user_settings')
    op.drop_table('stock_portfolio')
    op.drop_table('stock_stats')
    op.drop_table('stock')
    op.drop_table('user')

