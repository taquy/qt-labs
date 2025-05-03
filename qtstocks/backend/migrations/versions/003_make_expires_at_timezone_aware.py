"""make expires_at timezone aware

Revision ID: 003
Revises: 002
Create Date: 2024-03-21 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime, timezone


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    # Convert existing expires_at values to timezone-aware
    op.execute("""
        UPDATE user_jwt 
        SET expires_at = expires_at AT TIME ZONE 'UTC'
        WHERE expires_at IS NOT NULL
    """)
    
    # Modify expires_at column to be timezone-aware
    op.alter_column('user_jwt', 'expires_at',
                    existing_type=sa.DateTime(),
                    type_=sa.DateTime(timezone=True),
                    existing_nullable=False)


def downgrade():
    # Convert timezone-aware values back to naive
    op.execute("""
        UPDATE user_jwt 
        SET expires_at = expires_at AT TIME ZONE 'UTC'
        WHERE expires_at IS NOT NULL
    """)
    
    # Modify expires_at column back to naive datetime
    op.alter_column('user_jwt', 'expires_at',
                    existing_type=sa.DateTime(timezone=True),
                    type_=sa.DateTime(),
                    existing_nullable=False) 