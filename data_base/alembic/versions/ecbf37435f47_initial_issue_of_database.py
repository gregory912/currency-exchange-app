"""Initial issue of database

Revision ID: ecbf37435f47
Revises: 
Create Date: 2022-06-02 13:44:07.063557

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ecbf37435f47'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('login', sa.String(50), nullable=False, unique=True),
        sa.Column('password', sa.String(200), nullable=False),
        sa.Column('creation_date', sa.DateTime(timezone=False), nullable=False)
    )

    op.create_table(
        'user_data',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('id_user', sa.Integer, nullable=False, unique=True),
        sa.Column('name', sa.String(20), nullable=False),
        sa.Column('surname', sa.String(20), nullable=False),
        sa.Column('country', sa.String(50), nullable=False),
        sa.Column('address', sa.String(50), nullable=False),
        sa.Column('email', sa.String(50), nullable=False, unique=True),
        sa.Column('phone', sa.String(15), nullable=False),
        sa.ForeignKeyConstraint(['id_user'], ['users.id'])
    )

    op.create_table(
        'services',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('id_user_data', sa.Integer, nullable=False, unique=True),
        sa.Column('user_account_id', sa.Integer, nullable=False, unique=True),
        sa.ForeignKeyConstraint(['id_user_data'], ['user_data.id'])
    )

    op.create_table(
        'cards',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('id_user_data', sa.Integer, nullable=False),
        sa.Column('card_number', sa.String(16), nullable=False, unique=True),
        sa.Column('valid_thru', sa.Date, nullable=False),
        sa.Column('cvv', sa.String(3), nullable=False),
        sa.Column('blocked', sa.Boolean, default=False),
        sa.Column('daily_limit', sa.Integer, default=1000),
        sa.Column('internet_limit', sa.Integer, default=5000),
        sa.Column('contactless_limit', sa.Integer, default=100),
        sa.Column('card_pin', sa.String(4), nullable=False),
        sa.Column('sec_online_transactions', sa.Boolean, default=True),
        sa.Column('sec_location', sa.Boolean, default=False),
        sa.Column('sec_magnetic_strip', sa.Boolean, default=False),
        sa.Column('sec_withdrawals_atm', sa.Boolean, default=True),
        sa.Column('sec_contactless', sa.Boolean, default=True),
        sa.ForeignKeyConstraint(['id_user_data'], ['user_data.id'])
    )

    op.create_table(
        'user_accounts',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('id_user_data', sa.Integer, nullable=False),
        sa.Column('account_number', sa.String(26), nullable=False, unique=True),
        sa.Column('currency', sa.String(3), nullable=False),
        sa.Column('balance', sa.Numeric(precision=6, scale=2), default=0),
        sa.ForeignKeyConstraint(['id_user_data'], ['user_data.id'])
    )

    op.create_table(
        'card_transactions',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('id_user_account', sa.Integer, nullable=False),
        sa.Column('transaction_time', sa.DateTime(timezone=False), nullable=False),
        sa.Column('amount', sa.Numeric(precision=6, scale=2)),
        sa.Column('commission', sa.Numeric(precision=3, scale=2)),
        sa.Column('balance', sa.Numeric(precision=6, scale=2)),
        sa.Column('payer_name', sa.String(50), nullable=False),
        sa.ForeignKeyConstraint(['id_user_account'], ['user_accounts.id'])
    )

    op.create_table(
        'currency_incomes',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('id_user_account', sa.Integer, nullable=False),
        sa.Column('transfer_amount', sa.Numeric(precision=6, scale=2)),
        sa.Column('exchange_rate', sa.Numeric(precision=3, scale=2)),
        sa.Column('transaction_time', sa.DateTime(timezone=False), nullable=False),
        sa.Column('balance', sa.Numeric(precision=6, scale=2)),
        sa.ForeignKeyConstraint(['id_user_account'], ['user_accounts.id'])
    )

    op.create_table(
        'currency_expenses',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('id_user_account', sa.Integer, nullable=False),
        sa.Column('transfer_amount', sa.Numeric(precision=6, scale=2)),
        sa.Column('exchange_rate', sa.Numeric(precision=3, scale=2)),
        sa.Column('transaction_time', sa.DateTime(timezone=False), nullable=False),
        sa.Column('balance', sa.Numeric(precision=6, scale=2)),
        sa.ForeignKeyConstraint(['id_user_account'], ['user_accounts.id'])
    )

    op.create_table(
        'transactions',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('id_user_account', sa.Integer, nullable=False),
        sa.Column('payment', sa.String(3), nullable=True),
        sa.Column('payout', sa.String(3), nullable=True),
        sa.Column('transfer_title', sa.String(50), nullable=False),
        sa.Column('transaction_time', sa.DateTime(timezone=False), nullable=False),
        sa.Column('amount', sa.Numeric(precision=6, scale=2)),
        sa.Column('balance', sa.Numeric(precision=6, scale=2)),
        sa.Column('payer_name', sa.String(30), nullable=False),
        sa.Column('payer_account_number', sa.String(26), nullable=False),
        sa.ForeignKeyConstraint(['id_user_account'], ['user_accounts.id'])
    )


def downgrade() -> None:
    op.drop_table('transactions')
    op.drop_table('currency_incomes')
    op.drop_table('currency_expenses')
    op.drop_table('card_transactions')
    op.drop_table('user_accounts')
    op.drop_table('cards')
    op.drop_table('services')
    op.drop_table('user_data')
    op.drop_table('users')







