from database.repository.crud_repo import CrudRepo
from database.model.tables import *
from datetime import date, datetime
from decimal import Decimal


class GenerateData:
    @staticmethod
    def check_data(engine):
        """Check if the data is a database"""
        return CrudRepo(engine, UserDataTable).find_by_id(1)

    @staticmethod
    def generate_data(engine):
        """Generate data for an empty database"""
        CrudRepo(engine, UserDataTable).add(
            name="name",
            surname="surname",
            country="country",
            address="address",
            email="email",
            phone="phone",
            login="login",
            password="password",
            creation_date=datetime.today(),
            main_currency="GBP")
        CrudRepo(engine, ServiceTable).add(
            id_user_data=1,
            user_account_id=1,
            card_id=1)
        CrudRepo(engine, CardTable).add(
            id_user_data=1,
            card_number="1234567891234567",
            valid_thru=date.today(),
            cvv="123",
            blocked=False,
            daily_limit=2000,
            internet_limit=1000,
            contactless_limit=100,
            card_pin="1234",
            sec_online_transactions=True,
            sec_location=False,
            sec_magnetic_strip=False,
            sec_withdrawals_atm=True,
            sec_contactless=True,
            card_name="card name",
            card_type="STANDARD",
            main_currency="GBP")
        CrudRepo(engine, UserAccountTable).add(
            id_user_data=1,
            account_number="1234567891234567891234",
            currency="GBP",
            balance=Decimal(1000))
        CrudRepo(engine, CardTransactionTable).add(
            id_user_account=1,
            transaction_time=datetime.today(),
            amount=Decimal(10),
            commission_in_main_user_currency=Decimal(2),
            balance=Decimal(800),
            payer_name="payer_name",
            id_card=1,
            payout="YES",
            payment="NO",
            rate_to_main_card_currency=Decimal(1),
            transaction_type="Withdrawals ATM",
            rate_tu_used_account=Decimal(1),
            payer_account_number="1234567891234567891234",
            amount_in_main_user_currency=Decimal(100))
        CrudRepo(engine, CurrencyExchangeTable).add(
            id_user_account_out=1,
            transfer_amount_out=Decimal(100),
            exchange_rate_out=Decimal(1),
            balance_out=Decimal(1000),
            id_user_account_in=1,
            transfer_amount_in=Decimal(100),
            exchange_rate_in=Decimal(1),
            balance_in=Decimal(1000),
            transaction_time=datetime.today(),
            amount_in_main_user_currency=Decimal(800),
            commission_in_main_user_currency=Decimal(1))
        CrudRepo(engine, TransactionTable).add(
            id_user_account=1,
            payment="YES",
            payout="NO",
            transfer_title="transfer title",
            transaction_time=datetime.today(),
            amount=Decimal(100),
            balance=Decimal(1000),
            payer_name="payer name",
            payer_account_number="1234567891234567891234")
