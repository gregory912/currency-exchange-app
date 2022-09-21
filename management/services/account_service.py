from database.repository.crud_repo import CrudRepo
from database.repository.user_account_repo import UserAccountRepo
from database.model.tables import *
from management.conversions import *
from management.services.utils import *
from datetime import datetime
from decimal import Decimal


class AccountOperations:
    def __init__(self, engine):
        self.engine = engine

        self.service_op = ServiceOperations(self.engine)
        self.user_account_crud_repo = UserAccountRepo(self.engine, UserAccountTable)

    def user_without_account(self, logged_in_user: namedtuple):
        """Open an account for a new user"""
        if GetReplyUserWithoutAcc().get_value() == 'Y':
            self.add_account(logged_in_user.id)
            self.service_op.add_service(logged_in_user.id)

    def add_account(self, id_user_data: int) -> bool:
        """Add a new currency account. Check if the account already not exists"""
        currency = choose_currency("Select the currency for which you want to open an account:")
        if self.user_account_crud_repo.check_if_account_exist(id_user_data, currency):
            return True
        else:
            self._add_new_account(id_user_data, currency)
            return False

    def _add_new_account(self, id_user_data: int, currency: str):
        """Add a new currency account"""
        self.user_account_crud_repo.add(
            id_user_data=id_user_data,
            account_number=self._generate_account_number(),
            currency=currency,
            balance=Decimal(0))

    def _generate_account_number(self) -> str:
        """Generate an account number and check that it has not been used before"""
        while True:
            account_number = generate_random_number(25)
            if not self._check_if_account_number_exists(account_number):
                return account_number

    def _check_if_account_number_exists(self, account_number: str) -> tuple:
        """Check if the account is in the database"""
        return self.user_account_crud_repo.find_first_with_condition((UserAccountTable.account_number, account_number))


class AddMoneyService:
    def __init__(self, engine):
        self.engine = engine

        self.user_account_crud_repo = UserAccountRepo(self.engine, UserAccountTable)
        self.transaction_crud_repo = CrudRepo(self.engine, TransactionTable)

    def add_money(self, used_account: namedtuple):
        """Add money to your account"""
        amount = Decimal(GetReplyAmount().get_value())
        balance = used_account.balance + amount

        self._update_account_after_adding_money(used_account, balance)
        self._add_transaction_after_adding_money(used_account, balance, amount)

    def _update_account_after_adding_money(self, used_account, balance):
        self.user_account_crud_repo.update_by_id(
            used_account.id,
            id=used_account.id,
            id_user_data=used_account.id_user_data,
            account_number=used_account.account_number,
            currency=used_account.currency,
            balance=balance)

    def _add_transaction_after_adding_money(self, used_account, balance, amount):
        self.transaction_crud_repo.add(
            id_user_account=used_account.id,
            payment='YES',
            payout='NO',
            transfer_title=GetReplyUserTransferTitle().get_value(),
            transaction_time=datetime.now(),
            amount=amount,
            balance=balance,
            payer_name=GetReplyPayerName().get_value(),
            payer_account_number=GetReplyPayerAccNumber().get_value())


class TransferMoneyService:
    def __init__(self, engine):
        self.engine = engine

        self.user_account_crud_repo = UserAccountRepo(self.engine, UserAccountTable)
        self.transaction_crud_repo = CrudRepo(self.engine, TransactionTable)

    def transfer_money(self, used_account: namedtuple):
        """Transfer money to another account"""
        if self._check_user_account_balance(used_account):
            amount = Decimal(GetReplyAmount().get_value())
            balance = used_account.balance - amount

            if self._check_balance_after_transaction(balance):
                self._update_account_after_transfer_money(used_account, balance)
                self._add_transaction_after_transfer_money(used_account, amount, balance)

    def _update_account_after_transfer_money(self, used_account: namedtuple, balance: Decimal):
        """Update the account after performing the operation"""
        self.user_account_crud_repo.update_by_id(
            used_account.id,
            id=used_account.id,
            id_user_data=used_account.id_user_data,
            account_number=used_account.account_number,
            currency=used_account.currency,
            balance=balance)

    def _add_transaction_after_transfer_money(self, used_account: namedtuple, amount: Decimal, balance: Decimal):
        """Add transactions after completing the operation"""
        self.transaction_crud_repo.add(
            id_user_account=used_account.id,
            payment='NO',
            payout='YES',
            transfer_title=GetReplyUserTransferTitle().get_value(),
            transaction_time=datetime.now(),
            amount=amount,
            balance=balance,
            payer_name=GetReplyPayerName().get_value(),
            payer_account_number=GetReplyPayerAccNumber().get_value())

    @staticmethod
    def _check_user_account_balance(used_account: namedtuple) -> bool:
        """Check if the user has any funds on the account"""
        if used_account.balance == 0:
            print(f"\n{' ' * 12}You do not have sufficient funds in your account")
            return False
        return True

    @staticmethod
    def _check_balance_after_transaction(balance: Decimal) -> bool:
        """Check that the amount after the t is not negative"""
        if balance < 0:
            print(f"\n{' ' * 12}You do not have sufficient funds in your account")
            return False
        return True


class ServiceOperations:
    def __init__(self, engine):
        self.engine = engine

        self.user_account_crud_repo = UserAccountRepo(self.engine, UserAccountTable)
        self.service_crud_repo = CrudRepo(self.engine, ServiceTable)

    def add_service(self, id_user_data: int):
        """Add a new row to the service table"""
        self.service_crud_repo.add(id_user_data=id_user_data, user_account_id=self._get_user_account_lastrow())

    def update_service(self, id_user_data: int, user_account_id: int = None):
        """Update an existing row in the service table"""
        if not user_account_id:
            user_account_id = self._get_user_account_lastrow()

        service_row = self._get_service_row_for_user(id_user_data)

        self.service_crud_repo.update_by_id(
            service_row[0],
            id_user_data=id_user_data,
            user_account_id=user_account_id,
            card_id=service_row[3])

    def _get_user_account_lastrow(self):
        """Return the last user account added"""
        return self.user_account_crud_repo.get_last_row()[0]

    def _get_service_row_for_user(self, id_user_data: int):
        """Return a service for the user"""
        return self.service_crud_repo.find_first_with_condition((ServiceTable.id_user_data, id_user_data))

    def check_service(self, logged_in_user: namedtuple) -> list:
        """Check if there is a service in the database for the given account"""
        return self.service_crud_repo.join_with_condition(
            UserDataTable,
            ServiceTable.user_account_id,
            (UserDataTable.login, logged_in_user.login))


class SwitchAccount:
    def __init__(self, engine):
        self.engine = engine

        self.update_service = ServiceOperations(self.engine)
        self.user_account_crud_repo = UserAccountRepo(self.engine, UserAccountTable)

        self.accounts = []
        self.accounts_named_tuple = tuple()

    def switch_accounts(self, id_user_data: int):
        """Change the account for which the operations will be performed"""
        self.accounts = self._get_all_accounts_for_user(id_user_data)
        self.accounts_named_tuple = self._get_accounts_as_namedtuple()

        self._print_available_accounts()

        chosen_operation = GetReplyWithValueChosenAcc().get_value(self.accounts_named_tuple)

        self.update_service.update_service(
            id_user_data, self._get_id_of_chosen_account(chosen_operation))

    def _get_all_accounts_for_user(self, id_user_data: int) -> list[tuple]:
        """Get all user accounts from the database"""
        return self.user_account_crud_repo.find_all_with_condition((UserAccountTable.id_user_data, id_user_data))

    def _get_accounts_as_namedtuple(self) -> list[namedtuple]:
        """Replace all accounts as tuple with namedtuple"""
        return [user_account_named_tuple(account) for account in self.accounts]

    def _get_id_of_chosen_account(self, chosen_operation: str) -> namedtuple:
        """Return the id of the selected account"""
        return self.accounts_named_tuple[int(chosen_operation) - 1].id

    def _print_available_accounts(self):
        """Print all available user accounts"""
        for x, item in enumerate(self.accounts_named_tuple):
            print(f"{' ' * 12}", x + 1, ' ', item.currency, ' ', item.balance)
