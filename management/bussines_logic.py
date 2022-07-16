from sqlalchemy import create_engine
from management.services.login_service import Login
from management.services.account_service import AccountService
from management.services.currency_exchange_service import CurrencyExchangeService
from management.services.transactions_service import TransactionService
from data_base.repository.crud_repo import CrudRepo
from data_base.model.tables import ServiceTable, UserDataTable, UserAccountTable
from management.validation import *
from management.conversions import *


class BussinesLogic:
    def __init__(self):
        self.username = 'user' #wprowadzic dane z pliku yml?
        self.password = 'user1234'
        self.database = 'currency_exchange_app'
        self.port = 3309
        self.url = f'mysql://{self.username}:{self.password}@localhost:{self.port}/{self.database}'
        self.engine = create_engine(self.url, future=True)  #echo=True,
        self._logged_in_user = None
        self._used_account = None
        self._sequence = 0

    def _login(self):
        if not Login.does_account_exist():
            Login.create_account(self.engine)
        self._logged_in_user = user_data_named_tuple(Login.login(self.engine))
        self._sequence = 5

    def _user_without_account(self):
        print(f"{' ' * 12}You don't have any open account in the internet exchange currency. "
              f"Would you like to open a new account?")
        response = get_answer(
            validation_of_answer,
            "Enter Y or N: ",
            'Entered value is not correct. Enter Y or N: ')
        if response == 'Y':
            AccountService.add_account(self.engine, self._logged_in_user.id)
            AccountService.add_service(self.engine, self._logged_in_user.id)

    def _get_last_used_account(self):
        last_used = self._check_service()
        if last_used:
            self._used_account = user_account_named_tuple(
                CrudRepo(self.engine, UserAccountTable).find_by_id(last_used[0][0]))
            print(f'\n{" " * 12}{self._used_account.currency} {self._used_account.balance}')

    def _check_service(self):
        return CrudRepo(self.engine, ServiceTable).join_where_equal(
            UserDataTable,
            ServiceTable.user_account_id,
            (UserDataTable.login, self._logged_in_user.login))

    def _get_all_cards(self):
        pass

    def _choose_operation(self):
        print("""
            Select an operation: 
            1. Operations for accounts
            2. Operations for card
            3. Log out
            """)
        chosen_operation = get_answer(
            validation_chosen_operation,
            'Enter chosen operation: ',
            'Entered data contains illegal characters. Try again: ',
            (1, 3))
        match chosen_operation:
            case '1':
                if not self._check_service():
                    self._user_without_account()
                self._account_operations()
                self._sequence = 10
            case '2':
                self._card_operations()
                self._sequence = 15
            case '3':
                raise SystemExit(0)

    def _account_operations(self):
        self._get_last_used_account()
        print("""
            Select operation for your account: 
            1. Switch to another account
            2. Add a new foreign currency account
            3. Convert money
            4. Add money
            5. Make a transfer
            6. Show the account details
            7. Show last transactions
            8. Generate an account statement
            9. Remove the account
           10. Go back
            """)
        chosen_operation = get_answer(
            validation_chosen_operation,
            'Enter chosen operation: ',
            'Entered data contains illegal characters. Try again: ',
            (1, 10))
        match chosen_operation:
            case '1':
                if self._used_account:
                    AccountService.switch_accounts(self.engine, self._logged_in_user.id)
                else:
                    print(f"\n{' ' * 12}You cannot switch account because you don't have any account. "
                          f"Open a foreign currency account.")
            case '2':
                if not self._used_account:
                    AccountService.add_account(self.engine, self._logged_in_user.id)
                    AccountService.add_service(self.engine, self._logged_in_user.id)
                else:
                    if AccountService.add_account(self.engine, self._logged_in_user.id):
                        print(f"\n{' ' * 12}Account has not been created. An account for this currency already exists.")
                    else:
                        AccountService.update_service(self.engine, self._logged_in_user.id)
            case '3':
                if self._used_account:
                    CurrencyExchangeService().transaction(self.engine, self._logged_in_user.id, self._used_account)
                else:
                    print(f"\n{' ' * 12}You cannot make transactions because you don't have any account. "
                          f"Open a foreign currency account.")
            case '4':
                if self._used_account:
                    AccountService.add_money(self.engine, self._used_account)
                else:
                    print(f"\n{' ' * 12}You cannot add money because you don't have any account. "
                          f"Open a foreign currency account.")
            case '5':
                if self._used_account:
                    AccountService.transfer_money(self.engine, self._used_account)
                else:
                    print(f"\n{' ' * 12}You cannot transfer money because you don't have any account. "
                          f"Open a foreign currency account.")
            case '6':
                if self._used_account:
                    print(f"\n{' ' * 12}Account_number:{self._used_account.account_number} "
                          f"Currency:{self._used_account.currency} Balance:{self._used_account.balance} ")
                else:
                    print(f"\n{' ' * 12}You cannot see your account details because you don't have any account. "
                          f"Open a foreign currency account.")
            case '7':
                if self._used_account:
                    TransactionService().last_transactions(self.engine, self._used_account)
                else:
                    print(f"\n{' ' * 12}You cannot see last transactions because you don't have any account. "
                          f"Open a foreign currency account.")
            case '8':
                pass
            case '9':
                pass
            case '10':
                self._choose_operation()

    def _card_operations(self):
        print("""
            Select operation for your card: 
            1. View card details
            2. Block the card
            3. Set the card limit
            4. Show PIN
            5. Security
            6. Go back
            """)
        chosen_operation = get_answer(
            validation_chosen_operation,
            'Enter chosen operation: ',
            'Entered data contains illegal characters. Try again: ',
            (1, 6))
        match chosen_operation:
            case '1':
                pass
            case '2':
                pass
            case '3':
                pass
            case '4':
                pass
            case '5':
                pass
            case '6':
                self._choose_operation()

    def cycle(self):
        match self._sequence:
            case 0:
                self._login()
            case 5:
                self._choose_operation()
            case 10:
                self._account_operations()
            case 15:
                self._card_operations()
