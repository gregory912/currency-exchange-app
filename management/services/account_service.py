from management.validation import *
from data_base.repository.crud_repo import CrudRepo
from data_base.repository.service_repo import ServiceRepo
from data_base.repository.user_account_repo import UserAccountRepo
from data_base.model.tables import *
from random import randint
from decimal import Decimal
from management.conversions import *
from datetime import datetime


class AccountManagement:
    @staticmethod
    def switch_accounts(engine, id_user_data: int):
        """Change the account for which the operations will be performed"""
        accounts = UserAccountRepo(engine, UserAccountTable).find_all_accounts(id_user_data)
        accounts_named_tuple = [user_account_named_tuple(account) for account in accounts]
        for x in range(0, len(accounts_named_tuple)):
            print(f"{' ' * 12}", x+1, ' ', accounts_named_tuple[x].currency, ' ', accounts_named_tuple[x].balance)
        chosen_operation = get_answer(
            validation_chosen_operation,
            'Enter chosen operation: ',
            'Entered data contains illegal characters. Try again: ',
            (1, len(accounts_named_tuple)))
        chosen_account = accounts_named_tuple[int(chosen_operation)-1].id
        AccountManagement.update_service(engine, id_user_data, chosen_account)

    @staticmethod
    def add_account(engine, id_user_data: int):
        """Add a new currency account. Check if the account no longer exists"""
        currency = AccountManagement.choose_currency()
        if UserAccountRepo(engine, UserAccountTable).check_if_account_exist(id_user_data, currency):
            return True
        else:
            CrudRepo(engine, UserAccountTable).add(
                id_user_data=id_user_data,
                account_number=AccountManagement.generate_account_number(engine),
                currency=currency,
                balance=Decimal(0))
            return False

    @staticmethod
    def add_service(engine, id_user_data: int):
        """Add a new row to the service table"""
        user_account_lastrow = CrudRepo(engine, UserAccountTable).get_last_row()[0]
        CrudRepo(engine, ServiceTable).add(id_user_data=id_user_data, user_account_id=user_account_lastrow)

    @staticmethod
    def update_service(engine, id_user_data: int, chosen_account: int = None):
        """Update an existing row in the service table"""
        if not chosen_account:
            chosen_account = CrudRepo(engine, UserAccountTable).get_last_row()[0]
        service_row = ServiceRepo(engine, ServiceTable).find_service(id_user_data)
        CrudRepo(engine, ServiceTable).update_by_id(
            service_row[0],
            id_user_data=id_user_data,
            user_account_id=chosen_account)

    @staticmethod
    def generate_account_number(engine):
        """Generate an account number and check that it has not been used before"""
        while True:
            account_number = ''.join([str(randint(0, 9)) for _ in range(25)])
            if not UserAccountRepo(engine, UserAccountTable).find_account_number(account_number):
                return account_number

    @staticmethod
    def choose_currency():
        """Select the currency for which you want to perform the operation"""
        print("""
            Select the currency for which you want to open an account: 
            1. GBP
            2. USD
            3. CHF
            4. EUR
            """)
        chosen_operation = get_answer(
            validation_chosen_operation,
            'Enter chosen operation: ',
            'Entered data contains illegal characters. Try again: ',
            (1, 4))
        match chosen_operation:
            case '1':
                return 'GBP'
            case '2':
                return 'USD'
            case '3':
                return 'CHF'
            case '4':
                return 'EUR'

    @staticmethod
    def add_money(engine, used_account: namedtuple):
        """Add money to your account"""
        transfer_title = get_answer(
            validation_space_or_alpha_not_digit,
            'Enter the transfer title: ',
            'Entered data contains illegal characters. Try again: ')
        amount = get_answer(
            validation_decimal,
            'Enter the amount: ',
            'Entered data contains illegal characters. Try again: ')
        payer_name = get_answer(
            validation_alpha,
            'Enter the payer name: ',
            'Entered data contains illegal characters. Try again: ')
        payer_acc_number = get_answer(
            validation_digit,
            'Enter the payer account number: ',
            'Entered data is not correct. The number should contain between 20 - 26 digits. Try again: ',
            (20, 26))
        balance = used_account.balance + Decimal(amount)
        CrudRepo(engine, UserAccountTable).update_by_id(
            used_account.id,
            id=used_account.id,
            id_user_data=used_account.id_user_data,
            account_number=used_account.account_number,
            currency=used_account.currency,
            balance=balance)
        CrudRepo(engine, TransactionTable).add(
            id_user_account=used_account.id,
            payment='YES',
            payout='NO',
            transfer_title=transfer_title,
            transaction_time=datetime.now(),
            amount=Decimal(amount),
            balance=balance,
            payer_name=payer_name,
            payer_account_number=payer_acc_number)

    @staticmethod
    def transfer_money(engine, used_account: namedtuple):
        """Transfer money to another account"""
        transfer_title = get_answer(
            validation_space_or_alpha_not_digit,
            'Enter the transfer title: ',
            'Entered data contains illegal characters. Try again: ')
        amount = get_answer(
            validation_decimal,
            'Enter the amount: ',
            'Entered data contains illegal characters. Try again: ')
        payer_name = get_answer(
            validation_alpha,
            'Enter the payer name: ',
            'Entered data contains illegal characters. Try again: ')
        payer_acc_number = get_answer(
            validation_digit,
            'Enter the payer account number: ',
            'Entered data is not correct. The number should contain between 20 - 26 digits. Try again: ',
            (20, 26))
        balance = used_account.balance - Decimal(amount)
        if balance < 0:
            print(f"\n{' ' * 12}You do not have sufficient funds in your account")
        else:
            CrudRepo(engine, UserAccountTable).update_by_id(
                used_account.id,
                id=used_account.id,
                id_user_data=used_account.id_user_data,
                account_number=used_account.account_number,
                currency=used_account.currency,
                balance=balance)
            CrudRepo(engine, TransactionTable).add(
                id_user_account=used_account.id,
                payment='NO',
                payout='YES',
                transfer_title=transfer_title,
                transaction_time=datetime.now(),
                amount=Decimal(amount),
                balance=balance,
                payer_name=payer_name,
                payer_account_number=payer_acc_number)
