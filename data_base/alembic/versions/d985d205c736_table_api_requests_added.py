"""table api_requests added

Revision ID: d985d205c736
Revises: 75c55617ec99
Create Date: 2022-07-12 20:03:44.841276

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd985d205c736'
down_revision = '75c55617ec99'
branch_labels = None
depends_on = None


def upgrade() -> None:
    ### TABLE API_REQUESTS ###
    op.create_table(
        'api_requests',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('transactions_a_day', sa.Integer),
        sa.Column('transactions_date', sa.DateTime(timezone=False))
    )


def downgrade() -> None:
    op.drop_table('api_requests')
