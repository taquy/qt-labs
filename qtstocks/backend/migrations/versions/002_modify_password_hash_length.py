"""modify password hash length

Revision ID: 002
Revises: 001
Create Date: 2024-03-21 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Modify password_hash column to VARCHAR(255)
    op.alter_column('user', 'password_hash',
                    existing_type=sa.String(128),
                    type_=sa.String(255),
                    existing_nullable=True)


def downgrade():
    # Revert password_hash column back to VARCHAR(128)
    op.alter_column('user', 'password_hash',
                    existing_type=sa.String(255),
                    type_=sa.String(128),
                    existing_nullable=True) 