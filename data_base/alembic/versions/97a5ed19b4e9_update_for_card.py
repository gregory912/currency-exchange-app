"""update for card

Revision ID: 97a5ed19b4e9
Revises: d985d205c736
Create Date: 2022-07-16 09:43:52.414369

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '97a5ed19b4e9'
down_revision = 'd985d205c736'
branch_labels = None
depends_on = None


def upgrade() -> None:
    ### TABLE SERVICE ###
    op.add_column('services', sa.Column('card_id', sa.Integer, unique=True))

    ### TABLE CARDS ###
    op.add_column('cards', sa.Column('card_name', sa.String(50), nullable=False))
    op.add_column('cards', sa.Column('card_type', sa.String(30), nullable=False))

    ### TABLE CARD TRANSACTION ###
    op.add_column('card_transactions', sa.Column('payout', sa.String(3), nullable=False))
    op.add_column('card_transactions', sa.Column('payment', sa.String(3), nullable=False))


def downgrade() -> None:
    ### TABLE SERVICE ###
    op.drop_column('services', 'card_id')

    ### TABLE CARDS ###
    op.drop_column('cards', 'card_name')
    op.drop_column('cards', 'card_type')

    ### TABLE CARD TRANSACTION ###
    op.drop_column('card_transactions', 'payout')
    op.drop_column('card_transactions', 'payment')