"""add products

Revision ID: 3
Revises: 2
Create Date: 2024-03-24 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '3'
down_revision = '2'
branch_labels = None
depends_on = None

def upgrade():
    # Create products table
    op.create_table(
        'product',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False, server_default='USD'),
        sa.Column('interval', sa.String(20), nullable=False),
        sa.Column('features', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add product_id to subscriptions table
    op.add_column('subscription', sa.Column('product_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_subscription_product', 'subscription', 'product', ['product_id'], ['id'])
    
    # Remove plan_type from subscriptions table
    op.drop_column('subscription', 'plan_type')

def downgrade():
    # Add back plan_type to subscriptions table
    op.add_column('subscription', sa.Column('plan_type', sa.String(50), nullable=False))
    
    # Remove product_id from subscriptions table
    op.drop_constraint('fk_subscription_product', 'subscription', type_='foreignkey')
    op.drop_column('subscription', 'product_id')
    
    # Drop products table
    op.drop_table('product') 