"""table api requests removed

Revision ID: afb274284dfc
Revises: 97a5ed19b4e9
Create Date: 2022-07-27 21:07:18.594573

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'afb274284dfc'
down_revision = '97a5ed19b4e9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_table('api_requests')


def downgrade() -> None:
    op.create_table(
        'api_requests',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('transactions_a_day', sa.Integer),
        sa.Column('transactions_date', sa.DateTime(timezone=False))
    )
