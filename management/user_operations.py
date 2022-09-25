from management.services.login_service import CreateAccount, Login
from management.services.account_service import *
from management.services.currency_exchange_service import CurrencyExchangeService
from management.services.transaction_service import TransactionService
from management.services.card_transaction_service import *
from management.services.card_management_service import *
from management.services.data_saving_service import SavingService
from management.validation import get_answer, validation_chosen_operation
from management.conversions import user_account_named_tuple, used_card_named_tuple, user_data_named_tuple
from management.services.common import get_dates
from database.repository.crud_repo import CrudRepo
from database.model.tables import UserAccountTable, CardTable
from sqlalchemy import create_engine


class UserOperations:
    def __init__(self):
        self.username = 'user'
        self.password = 'user1234'
        self.database = 'currency_exchange_app'
        self.port = 3309
        self.url = f'mysql://{self.username}:{self.password}@localhost:{self.port}/{self.database}'
        self.engine = create_engine(self.url, future=True)
        self._logged_in_user = None
        self._used_account = None
        self._used_card = None
        self._sequence = 0

        self.account_op_obj = AccountOperations(self.engine)
        self.service_op_obj = ServiceOperations(self.engine)
        self.card_mgmt_service_obj = CardManagement(self.engine)
        self.login_obj = Login(self.engine)
        self.transaction_service_obj = TransactionService(self.engine)

        self.user_account_crud_repo = CrudRepo(self.engine, UserAccountTable)
        self.card_crud_repo = CrudRepo(self.engine, CardTable)

    def _get_last_used_account(self, print_account: bool = True):
        """Check the last used account.
        Assign to a variable for display at the top in the main application window"""
        last_used_account = self.service_op_obj.check_service(self._logged_in_user)
        if last_used_account:
            self._used_account = user_account_named_tuple(
                self.user_account_crud_repo.find_by_id(last_used_account[0][0]))
            if print_account:
                print(f'\n{" " * 12}{self._used_account.currency} {self._used_account.balance}')

    def _get_last_used_card(self, print_card: bool = True):
        """Check the last used account.
        Assign to a variable for display at the top in the main application window"""
        self.card_mgmt_service_obj.card_expired(self._used_card, self._logged_in_user)
        last_used_card = self.card_mgmt_service_obj.check_service(self._logged_in_user)
        if last_used_card[0][0]:
            self._used_card = used_card_named_tuple(self.card_crud_repo.find_by_id_choose_columns(
                last_used_card[0][0],
                (CardTable.id, CardTable.card_number, CardTable.valid_thru,
                 CardTable.card_name, CardTable.card_type, CardTable.main_currency)))
            if print_card:
                print(f'\n{" " * 12}{self._used_card.card_name} Type: {self._used_card.card_type} '
                      f'Number: *{self._used_card.card_number[-4:]}')
        else:
            self._used_card = None

    def _choose_operation(self):
        """Choose whether you want to make transactions using
        a foreign currency account or transactions using a card."""
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
                if not self.service_op_obj.check_service(self._logged_in_user):
                    self.account_op_obj.user_without_account(self._logged_in_user)
                self._sequence = 10
            case '2':
                if self.service_op_obj.check_service(self._logged_in_user):
                    if not self.card_mgmt_service_obj.check_service(self._logged_in_user)[0][0]:
                        self.card_mgmt_service_obj.user_without_card(self._logged_in_user)
                        self._sequence = 15
                    else:
                        self._sequence = 15
                else:
                    self.account_op_obj.user_without_account(self._logged_in_user)
            case '3':
                raise SystemExit(0)

    def _account_operations(self):
        """Select operations for your account from the console"""
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
            9. Go back
            """)
        chosen_operation = get_answer(
            validation_chosen_operation,
            'Enter chosen operation: ',
            'Entered data contains illegal characters. Try again: ',
            (1, 9))
        match chosen_operation:
            case '1':
                if self._used_account:
                    SwitchAccount(self.engine).switch_accounts(self._logged_in_user.id)
                else:
                    print(f"\n{' ' * 12}You cannot switch account because you don't have any account. "
                          f"Open a foreign currency account.")
            case '2':
                if not self._used_account:
                    self.account_op_obj.add_account(self._logged_in_user.id)
                    self.service_op_obj.add_service(self._logged_in_user.id)
                else:
                    if self.account_op_obj.add_account(self._logged_in_user.id):
                        print(f"\n{' ' * 12}Account has not been created. An account for this currency already exists.")
                    else:
                        self.service_op_obj.update_service(self._logged_in_user.id)
            case '3':
                if self._used_account:
                    CurrencyExchangeService(self.engine).transaction(self._logged_in_user, self._used_account)
                else:
                    print(f"\n{' ' * 12}You cannot make transactions because you don't have any account. "
                          f"Open a foreign currency account.")
            case '4':
                if self._used_account:
                    AccountAddMoney(self.engine).add_money(self._used_account)
                else:
                    print(f"\n{' ' * 12}You cannot add money because you don't have any account. "
                          f"Open a foreign currency account.")
            case '5':
                if self._used_account:
                    AccountTransferMoney(self.engine).transfer_money(self._used_account)
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
                    self.transaction_service_obj.last_transactions(self._used_account, self._logged_in_user)
                else:
                    print(f"\n{' ' * 12}You cannot see last transactions because you don't have any account. "
                          f"Open a foreign currency account.")
            case '8':
                if self._used_account:
                    dates = get_dates()
                    data = self.transaction_service_obj.transactions_between_dates(self._used_account, dates)
                    SavingService().generate_statement(data, self._logged_in_user, self._used_account, dates)
                else:
                    print(f"\n{' ' * 12}You cannot generate a statement because you don't have any account. "
                          f"Open a foreign currency account.")
            case '9':
                self._choose_operation()

    def _card_operations(self):
        """Select operations for your card from the console"""
        self._get_last_used_account(False)
        self._get_last_used_card()
        print("""
            Select operation for your card:
            1. Switch to another card
            2. Pay by card
            3. Get a new card
            4. Withdraw the money
            5. Deposit money on the card
            6. View card details
            7. Block the card
            8. Set the card limit
            9. Show PIN
           10. Security
           11. Remove the card
           12. Go back
            """)
        chosen_operation = get_answer(
            validation_chosen_operation,
            'Enter chosen operation: ',
            'Entered data contains illegal characters. Try again: ',
            (1, 12))
        match chosen_operation:
            case '1':
                if self._used_card:
                    self.card_mgmt_service_obj.switch_cards(self._logged_in_user.id)
                else:
                    print(f"\n{' ' * 12}You cannot switch cards. "
                          f"Open a card for currency transactions to be able to perform operations.")
            case '2':
                if self._used_card:
                    PayByCard(self.engine).pay_by_card(self._used_card, self._logged_in_user)
                else:
                    print(f"\n{' ' * 12}You cannot pay by card. "
                          f"Open a card for currency transactions to be able to perform operations.")
            case '3':
                if AddCard(self.engine).add_card_type(self._logged_in_user):
                    self.card_mgmt_service_obj.update_service_after_adding_card(self._logged_in_user.id)
            case '4':
                if self._used_card:
                    WithdrawMoneyByCard(self.engine).withdraw_money(self._used_card, self._logged_in_user)
                else:
                    print(f"\n{' ' * 12}You cannot withdraw the money. "
                          f"Open a card for currency transactions to be able to perform operations.")
            case '5':
                if self._used_card:
                    CardDepositMoney(self.engine).deposit_money(self._used_card, self._logged_in_user)
                else:
                    print(f"\n{' ' * 12}You cannot withdraw the money. "
                          f"Open a card for currency transactions to be able to perform operations.")
            case '6':
                if self._used_card:
                    print(f"\n{' ' * 12}Card number:{self._used_card.card_number} "
                          f"Valid thru: {self._used_card.valid_thru} Card name: {self._used_card.card_name} "
                          f"Card type: {self._used_card.card_type} Main currency: {self._used_card.main_currency}")
                else:
                    print(f"\n{' ' * 12}You don't have any card. Get a card to see the details.")
            case '7':
                if self._used_card:
                    BlockCard(self.engine).block_card(self._used_card)
                else:
                    print(f"\n{' ' * 12}You don't have any card.")
            case '8':
                if self._used_card:
                    CardLimit(self.engine).set_card_limit(self._used_card)
                else:
                    print(f"\n{' ' * 12}You don't have any card.")
            case '9':
                if self._used_card:
                    ShowCardPin(self.engine).show_pin(self._used_card, self._logged_in_user)
                else:
                    print(f"\n{' ' * 12}You don't have any card.")
            case '10':
                if self._used_card:
                    CardSecurity(self.engine).card_security(self._used_card)
                else:
                    print(f"\n{' ' * 12}You don't have any card.")
            case '11':
                if self._used_card:
                    DeleteCard(self.engine).delete_card(self._used_card, self._logged_in_user)
                    print(f"\n{' ' * 12}Your card has been removed.")
                else:
                    print(f"\n{' ' * 12}You don't have any card.")
            case '12':
                self._choose_operation()

    def cycle(self):
        """The cycle of a program to perform the proper operation"""
        match self._sequence:
            case 0:
                if not self.login_obj.does_account_exist():
                    CreateAccount(self.engine).create_account()
                self._logged_in_user = user_data_named_tuple(self.login_obj.get_user())
                self._sequence = 5
            case 5:
                self._choose_operation()
            case 10:
                self._account_operations()
            case 15:
                self._get_last_used_card(False)
                self._card_operations()
