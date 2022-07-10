"""Changes for a new structure of data base

Revision ID: 75c55617ec99
Revises: ecbf37435f47
Create Date: 2022-07-09 09:24:26.352574

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '75c55617ec99'
down_revision = 'ecbf37435f47'
branch_labels = None
depends_on = None


def upgrade() -> None:
    ### TABLE USER_DATA ###
    op.drop_constraint(constraint_name="user_data_ibfk_1",
                       table_name="user_data",
                       type_="foreignkey")
    op.drop_table('users')
    op.drop_column('user_data', 'id_user')
    op.add_column('user_data', sa.Column('login', sa.String(50), nullable=False, unique=True))
    op.add_column('user_data', sa.Column('password', sa.String(200), nullable=False))
    op.add_column('user_data', sa.Column('creation_date', sa.DateTime(timezone=False), nullable=False))

    ### TABLE CARD_TRANSACTIONS ###
    op.add_column('card_transactions', sa.Column('id_card', sa.Integer, nullable=False))
    op.create_foreign_key(
        constraint_name="card_transactions_ibfk_2",
        source_table='card_transactions',
        referent_table='cards',
        local_cols=['id_card'],
        remote_cols=['id'])

    ### TABLE CURRENCY INCOMES ###
    op.drop_constraint(constraint_name="currency_incomes_ibfk_1",
                       table_name="currency_incomes",
                       type_="foreignkey")
    op.drop_table('currency_incomes')

    ### TABLE CURRENCY EXPENSES ###
    op.drop_constraint(constraint_name="currency_expenses_ibfk_1",
                       table_name="currency_expenses",
                       type_="foreignkey")
    op.drop_table('currency_expenses')

    ### TABLE CURRENCY EXCHANGES ###
    op.create_table(
        'currency_exchanges',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('id_user_account_out', sa.Integer, nullable=False),
        sa.Column('transfer_amount_out', sa.Numeric(precision=6, scale=2)),
        sa.Column('exchange_rate_out', sa.Numeric(precision=3, scale=2)),
        sa.Column('balance_out', sa.Numeric(precision=6, scale=2)),
        sa.Column('id_user_account_in', sa.Integer, nullable=False),
        sa.Column('transfer_amount_in', sa.Numeric(precision=6, scale=2)),
        sa.Column('exchange_rate_in', sa.Numeric(precision=3, scale=2)),
        sa.Column('balance_in', sa.Numeric(precision=6, scale=2)),
        sa.Column('transaction_time', sa.DateTime(timezone=False), nullable=False),
        sa.ForeignKeyConstraint(['id_user_account_out'], ['user_accounts.id']),
        sa.ForeignKeyConstraint(['id_user_account_in'], ['user_accounts.id'])
    )


def downgrade() -> None:
    ### TABLE USER_DATA ###
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('login', sa.String(50), nullable=False, unique=True),
        sa.Column('password', sa.String(200), nullable=False),
        sa.Column('creation_date', sa.DateTime(timezone=False), nullable=False)
    )
    op.drop_column('user_data', 'login')
    op.drop_column('user_data', 'password')
    op.drop_column('user_data', 'creation_date')
    op.add_column('user_data', sa.Column('id_user', sa.Integer, nullable=False, unique=True))
    op.create_foreign_key(
        constraint_name="user_data_ibfk_2",
        source_table='user_data',
        referent_table='users',
        local_cols=['id_user'],
        remote_cols=['id'])

    ### TABLE CARD_TRANSACTIONS ###
    op.drop_constraint(constraint_name="card_transactions_ibfk_2",
                       table_name="card_transactions",
                       type_="foreignkey")
    op.drop_column('card_transactions', 'id_card')

    ### TABLE CURRENCY EXCHANGES ###
    op.drop_constraint(constraint_name="currency_exchanges_ibfk_1",
                       table_name="currency_exchanges",
                       type_="foreignkey")
    op.drop_constraint(constraint_name="currency_exchanges_ibfk_2",
                       table_name="currency_exchanges",
                       type_="foreignkey")
    op.drop_table('currency_exchanges')

    ### TABLE CURRENCY INCOMES ###
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

    ### TABLE CURRENCY EXPENSES ###
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