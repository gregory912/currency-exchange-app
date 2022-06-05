from sqlalchemy import create_engine
from management.login_service import Login
from management.account_service import AccountManagement
from data_base.repository.crud_repo import CrudRepo
from data_base.repository.user_data_repo import UserDataRepo
from data_base.model.tables import ServiceTable, UserDataTable, UserAccountTable
from management.validation import Validation
from management.conversions import *


class BussinesLogic:
    def __init__(self):
        self.username = 'user'
        self.password = 'user1234'
        self.database = 'currency_exchange_app'
        self.port = 3309
        self.url = f'mysql://{self.username}:{self.password}@localhost:{self.port}/{self.database}'
        self.engine = create_engine(self.url, future=True)  #echo=True,
        self._logged_in_user = None
        self._logged_in_user_data = None
        self._used_account = None
        self._sequence = 0

    def _login(self):
        if not Login.does_account_exist():
            Login.create_account(self.engine)
        self._logged_in_user = user_named_tuple(Login.login(self.engine))
        self._logged_in_user_data = user_data_named_tuple(
            UserDataRepo(self.engine, UserDataTable).find_user_data(self._logged_in_user.id))
        self._sequence = 5

    def _get_last_used_account(self):
        while True:
            last_used = CrudRepo(self.engine, ServiceTable).join_where_equal(
                UserDataTable,
                (ServiceTable.user_account_id,),
                (UserDataTable.id_user, self._logged_in_user.id))
            if last_used:
                self._used_account = user_account_named_tuple(
                    CrudRepo(self.engine, UserAccountTable).find_by_id(last_used[0][0]))
                print(f'\n{" " * 12}{self._used_account.currency} {self._used_account.amount}')
                break
            else:
                print(f"{' ' * 12}You don't have any open account in the internet exchange currency. "
                      f"Would you like to open a new account?")
                response = Validation.get_answer(
                    Validation.validation_of_answer,
                    "Enter Y or N: ",
                    'Entered value is not correct. Enter Y or N: ')
                if response == 'Y':
                    AccountManagement.add_account(self.engine, self._logged_in_user_data.id)
                    AccountManagement.add_service(self.engine, self._logged_in_user_data.id)
                else:
                    break

    def _get_all_cards(self):
        pass

    def _choose_operation(self):
        print("""
            Select an operation: 
            1. Operations for accounts
            2. Operations for card
            3. Log out
            """)
        chosen_operation = Validation.get_answer(
            Validation.validation_chosen_operation,
            'Enter chosen operation: ',
            'Entered data contains illegal characters. Try again: ',
            (1, 3))
        match chosen_operation:
            case '1':
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
        chosen_operation = Validation.get_answer(
            Validation.validation_chosen_operation,
            'Enter chosen operation: ',
            'Entered data contains illegal characters. Try again: ',
            (1, 10))
        match chosen_operation:
            case '1':
                AccountManagement.switch_accounts(self.engine, self._logged_in_user_data.id)
            case '2':
                if AccountManagement.add_account(self.engine, self._logged_in_user_data.id):
                    print(f"\n{' ' * 12}Account has not been created. An account for this currency already exists.")
                else:
                    AccountManagement.update_service(self.engine, self._logged_in_user_data.id)
            case '3':
                pass
            case '4':
                pass
            case '5':
                pass
            case '6':
                pass
            case '7':
                pass
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
        chosen_operation = Validation.get_answer(
            Validation.validation_chosen_operation,
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
