from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Numeric, Date, ForeignKey


base = declarative_base()


class UserTable(base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    login = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    creation_date = Column(DateTime(timezone=False), nullable=False)

    user_data_to_users = relationship("UserDataTable", back_populates="users_to_user_data", uselist=False)


class UserDataTable(base):
    __tablename__ = 'user_data'
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_user = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True)
    name = Column(String(20), nullable=False)
    surname = Column(String(20), nullable=False)
    country = Column(String(50), nullable=False)
    address = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False, unique=True)
    phone = Column(String(15), nullable=False)

    users_to_user_data = relationship("UserTable", back_populates="user_data_to_users")
    services_to_user_data = relationship("ServiceTable", back_populates="user_data_to_services", uselist=False)
    cards_to_user_data = relationship("CardTable", back_populates="user_data_to_cards")
    user_accounts_to_user_data = relationship("UserAccountTable", back_populates="user_data_to_user_accounts")


class ServiceTable(base):
    __tablename__ = 'services'
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_user_data = Column(Integer, ForeignKey('user_data.id'), nullable=False, unique=True)
    user_account_id = Column(Integer, nullable=False, unique=True)

    user_data_to_services = relationship("UserDataTable", back_populates="services_to_user_data")


class CardTable(base):
    __tablename__ = 'cards'
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_user_data = Column(Integer, ForeignKey('user_data.id'), nullable=False)
    card_number = Column(String(16), nullable=False, unique=True)
    valid_thru = Column(Date, nullable=False)
    cvv = Column(String(3), nullable=False)
    blocked = Column(Boolean, default=False)
    daily_limit = Column(Integer, default=1000)
    internet_limit = Column(Integer, default=5000)
    contactless_limit = Column(Integer, default=100)
    card_pin = Column(String(4), nullable=False)
    sec_online_transactions = Column(Boolean, default=True)
    sec_location = Column(Boolean, default=False)
    sec_magnetic_strip = Column(Boolean, default=False)
    sec_withdrawals_atm = Column(Boolean, default=True)
    sec_contactless = Column(Boolean, default=True)

    user_data_to_cards = relationship("UserDataTable", back_populates="cards_to_user_data")


class UserAccountTable(base):
    __tablename__ = 'user_accounts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_user_data = Column(Integer, ForeignKey('user_data.id'), nullable=False)
    account_number = Column(String(26), nullable=False, unique=True)
    currency = Column(String(3), nullable=False)
    amount = Column(Numeric(precision=6, scale=2), default=0)

    user_data_to_user_accounts = relationship("UserDataTable", back_populates="user_accounts_to_user_data")
    card_transactions_to_user_accounts = relationship("CardTransactionTable",
                                                      back_populates="user_accounts_to_card_transactions")
    currency_expenses_to_user_accounts = relationship("CurrencyExpenseTable",
                                                      back_populates="user_accounts_to_currency_expenses")
    currency_incomes_to_user_accounts = relationship("CurrencyIncomeTable",
                                                     back_populates="user_accounts_to_currency_incomes")
    transactions_to_user_accounts = relationship("TransactionTable", back_populates="user_accounts_to_transactions")


class CardTransactionTable(base):
    __tablename__ = 'card_transactions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_user_account = Column(Integer, ForeignKey('user_accounts.id'), nullable=False)
    transaction_time = Column(DateTime(timezone=False), nullable=False)
    amount = Column(Numeric(precision=6, scale=2))
    commission = Column(Numeric(precision=3, scale=2))
    balance = Column(Numeric(precision=6, scale=2))
    payer_name = Column(String(50), nullable=False)

    user_accounts_to_card_transactions = relationship("UserAccountTable",
                                                      back_populates="card_transactions_to_user_accounts")


class CurrencyExpenseTable(base):
    __tablename__ = 'currency_expenses'
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_user_account = Column(Integer, ForeignKey('user_accounts.id'), nullable=False)
    transfer_amount = Column(Numeric(precision=6, scale=2))
    exchange_rate = Column(Numeric(precision=3, scale=2))
    transaction_time = Column(DateTime(timezone=False), nullable=False)
    balance = Column(Numeric(precision=6, scale=2))

    user_accounts_to_currency_expenses = relationship("UserAccountTable",
                                                      back_populates="currency_expenses_to_user_accounts")


class CurrencyIncomeTable(base):
    __tablename__ = 'currency_incomes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_user_account = Column(Integer, ForeignKey('user_accounts.id'), nullable=False)
    transfer_amount = Column(Numeric(precision=6, scale=2))
    exchange_rate = Column(Numeric(precision=3, scale=2))
    transaction_time = Column(DateTime(timezone=False), nullable=False)
    balance = Column(Numeric(precision=6, scale=2))
    user_accounts_to_currency_incomes = relationship("UserAccountTable",
                                                     back_populates="currency_incomes_to_user_accounts")


class TransactionTable(base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_user_account = Column(Integer, ForeignKey('user_accounts.id'), nullable=False)
    payment = Column(String(3), nullable=True)
    payout = Column(String(3), nullable=True)
    transfer_title = Column(String(50), nullable=False)
    transaction_time = Column(DateTime(timezone=False), nullable=False)
    amount = Column(Numeric(precision=6, scale=2))
    balance = Column(Numeric(precision=6, scale=2))
    payer_name = Column(String(30), nullable=False)
    payer_account_number = Column(String(26), nullable=False)
    user_accounts_to_transactions = relationship("UserAccountTable", back_populates="transactions_to_user_accounts")
