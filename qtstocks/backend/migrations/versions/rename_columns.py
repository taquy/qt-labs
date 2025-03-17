"""Rename pe_ratio and pb_ratio columns

Revision ID: rename_ratio_columns
Revises: update_schema_symbol_pk
Create Date: 2024-03-19 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'rename_ratio_columns'
down_revision = 'update_schema_symbol_pk'
branch_labels = None
depends_on = None


def upgrade():
    # Rename columns in stock_stats table
    op.alter_column('stock_stats', 'pe_ratio', new_column_name='pe')
    op.alter_column('stock_stats', 'pb_ratio', new_column_name='pb')


def downgrade():
    # Revert column names
    op.alter_column('stock_stats', 'pe', new_column_name='pe_ratio')
    op.alter_column('stock_stats', 'pb', new_column_name='pb_ratio') 