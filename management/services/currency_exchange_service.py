from management.conversions import user_account_named_tuple
from management.services.common import *
from database.model.tables import UserAccountTable, CurrencyExchangeTable, UserDataTable
from database.repository.crud_repo import CrudRepo
from database.repository.user_account_repo import UserAccountRepo
from management.services.utils import GetReplyAmount, GetReplyWithValueChosenAccCurExch
from datetime import datetime
from requests import request
from json import loads
from decimal import Decimal


class CurrencyExchangeService:
    def __init__(self, engine):
        self.engine = engine

        self.cur_exch_obj = CurrencyExchange()
        self.user_account_crud_repo = CrudRepo(self.engine, UserAccountTable)

        self.accounts = list()
        self.amount = Decimal
        self.transaction_account = None
        self.used_account = None

    def transaction(self, logged_in_user: namedtuple, used_account: namedtuple) -> int:
        """Perform currency exchange transactions. Take account of account availability and account balance.
        Get commissions if required. Transfer money from one account to another with information about the rate
        and balance after the operation.
        amount_out ---> amount in main user currency - commission ---> amount in"""
        self.used_account = used_account
        self.accounts = self._available_accounts(logged_in_user.id)

        if self._check_number_of_accounts():

            if self._check_funds_in_your_account():
                chosen_operation = GetReplyWithValueChosenAccCurExch().get_value(self.accounts)
                self.amount = Decimal(GetReplyAmount().get_value())

                if self._check_balance_after_transaction():
                    self.transaction_account = self.accounts[int(chosen_operation) - 1]

                    amount_in_main_user_currency = self._get_amount_in_main_user_currency(logged_in_user)

                    amt_after_checking, commission_after_checking = self._check_commission(
                        amount_in_main_user_currency, logged_in_user.id, logged_in_user.main_currency)

                    exchanged_amount = self.cur_exch_obj.get_result(
                        logged_in_user.main_currency, self.transaction_account.currency,
                        str(amt_after_checking))['result']
                    rate_acc_to_trans = self.cur_exch_obj.get_result(
                        self.used_account.currency, self.transaction_account.currency, str(1))['info']['rate']
                    rate_trans_to_acc = self.cur_exch_obj.get_result(
                        self.transaction_account.currency, self.used_account.currency, str(1))['info']['rate']

                    exch_cur_out = self._get_exch_cur_dict(
                        rate_acc_to_trans, self.amount, self.used_account.balance - Decimal(self.amount))
                    exch_cur_in = self._get_exch_cur_dict(
                        rate_trans_to_acc, exchanged_amount,
                        round(self.transaction_account.balance + Decimal(exchanged_amount), 3))

                    self._update_account_from_which_money_is_going_out(exch_cur_out)
                    self._update_account_where_money_is_coming_in(exch_cur_in)
                    performed_transaction = self._add_performed_transaction_to_database(
                        exch_cur_out, exch_cur_in, amount_in_main_user_currency, commission_after_checking)

                    print(f"\n{' ' * 12}The transaction was successful.")
                    return performed_transaction

    def _update_account_from_which_money_is_going_out(self, exch_cur_out: dict):
        """Update the account from which the money is withdrawn"""
        return self.user_account_crud_repo.update_by_id(
            self.used_account.id,
            id=self.used_account.id,
            id_user_data=self.used_account.id_user_data,
            account_number=self.used_account.account_number,
            currency=self.used_account.currency,
            balance=exch_cur_out['balance'])

    def _update_account_where_money_is_coming_in(self, exch_cur_in: dict):
        """Update the account for the account that is being credited"""
        return self.user_account_crud_repo.update_by_id(
            self.transaction_account.id,
            id=self.transaction_account.id,
            id_user_data=self.transaction_account.id_user_data,
            account_number=self.transaction_account.account_number,
            currency=self.transaction_account.currency,
            balance=exch_cur_in['balance'])

    def _add_performed_transaction_to_database(
            self, exch_cur_out: dict, exch_cur_in: dict,
            amount_in_main_user_currency: Decimal, commission_after_checking: Decimal):
        """Add information about the performed transaction to the database"""
        return CrudRepo(self.engine, CurrencyExchangeTable).add(
            id_user_account_out=self.used_account.id,
            transfer_amount_out=exch_cur_out['amount'],
            exchange_rate_out=exch_cur_out['rate'],
            balance_out=exch_cur_out['balance'],
            id_user_account_in=self.transaction_account.id,
            transfer_amount_in=exch_cur_in['amount'],
            exchange_rate_in=exch_cur_in['rate'],
            balance_in=exch_cur_in['balance'],
            transaction_time=datetime.now(),
            amount_in_main_user_currency=amount_in_main_user_currency,
            commission_in_main_user_currency=commission_after_checking
        )

    def _check_number_of_accounts(self) -> bool:
        """Check if you have any accounts to perform the exchange"""
        if not self.accounts:
            print(f"\n{' ' * 12}You don't have any account other than your main account. "
                  f"Create a new account to be able to exchange currencies")
            return False
        return True

    def _check_funds_in_your_account(self) -> bool:
        """Check if you have any funds on your account"""
        if self.used_account.balance == 0:
            print(f"\n{' ' * 12}You do not have enough funds on your account to perform this operation.")
            return False
        return True

    def _check_balance_after_transaction(self) -> bool:
        """Check that the balance is positive after the transaction is completed"""
        if self.amount > self.used_account.balance:
            print(f"\n{' ' * 12}You do not have enough funds on your account to perform this operation.")
            return False
        return True

    def _get_amount_in_main_user_currency(self, logged_in_user: namedtuple):
        """Return the value in the user's primary currency"""
        if logged_in_user.main_currency != self.used_account.currency:
            return Decimal(self.cur_exch_obj.get_result(
                self.used_account.currency, logged_in_user.main_currency, str(self.amount))['result'])
        return self.amount

    def _available_accounts(self, id_user_data: int) -> list:
        """Get all accounts that can be used for currency exchange"""
        accounts = self._get_all_available_accounts(id_user_data)
        accounts_named_tuple = self._get_namedtuple_accounts(accounts)

        self._print_available_accounts(accounts_named_tuple)
        return accounts_named_tuple

    def _get_all_available_accounts(self, id_user_data: int) -> list[tuple]:
        """Get all available user accounts"""
        return self.user_account_crud_repo.find_all_with_condition((UserAccountTable.id_user_data, id_user_data))

    def _get_namedtuple_accounts(self, accounts: list[tuple]) -> namedtuple:
        """Swap accounts from tuple to namedtuple"""
        return [user_account_named_tuple(account) for account in accounts if account[3] != self.used_account.currency]

    def _check_commission(self, amount: Decimal, id_user_data: int, currency: str) -> tuple:
        """Check if a commission is required. The amount and commission are stated in the user's primary currency."""
        all_exchanges = self._get_all_monthly_exchanges(id_user_data)
        transaction_sum = self._get_sum_of_all_exchanges(all_exchanges)

        if transaction_sum + amount > 1000:
            print(f"\n{' ' * 12}You have exceeded the monthly exchange limit of 1000 {currency}. "
                  f"A commission of 0.5% of the entered amount has been charged.")

            return amount - (amount * Decimal(0.005)), amount * Decimal(0.005)
        return amount, 0

    def _get_all_monthly_exchanges(self, id_user_data: int) -> list[tuple]:
        """Get all monthly currency exchange transactions for one user"""
        return UserAccountRepo(self.engine, UserDataTable).get_monthly_exchanges_for_user(
            id_user_data, fst_day_of_this_month(), fst_day_of_next_month())

    @staticmethod
    def _get_exch_cur_dict(rate: str, amount: Decimal, balance: Decimal) -> dict:
        """Return the elements as a dict"""
        return {'rate': rate, 'amount': amount, 'balance': balance}

    @staticmethod
    def _print_available_accounts(accounts_named_tuple: namedtuple):
        """Print all available accounts"""
        for x, item in enumerate(accounts_named_tuple):
            print(f"{' ' * 12}", x + 1, ' ', item.currency)

    @staticmethod
    def _get_sum_of_all_exchanges(all_exchanges: list[tuple]) -> Decimal:
        """Get a total of all currency exchanges"""
        return sum([item[2] for item in all_exchanges])


class CurrencyExchange:
    def __init__(self):
        self.payload = {}
        self.headers = {"apikey": "b49pOzy85MBws0V8CMMHc0hQGdRw8Fll"}
        self._response = {}
        self._server_response = ''
        self.url = ''

    def get_result(self, cur_1: str, cur_2: str, amount: str) -> dict:
        """Send a query to the server and return the result"""
        self.url = self.get_url(cur_1, cur_2, amount)
        self._server_response = self.get_request()
        self._response = self.loads(self._server_response.text)
        if self._server_response.status_code != 200:
            raise Exception('Incorrect data received. Check if the entered data is correct')
        return self._response

    def get_request(self):
        """Send the query to the server"""
        return request("GET", self.url, headers=self.headers, data=self.payload)

    def unpack_data(self) -> dict:
        """Return the data in the appropriate form"""
        if not self._response:
            raise Exception('You cannot unpack the data until you get the query')
        return {'rate': self._response['info']['rate'], 'amount': self._response['result']}

    @staticmethod
    def get_url(cur_1: str, cur_2: str, amount: str) -> str:
        """Get url to API for entered data"""
        return f"https://api.exchangerate.host/convert?from={cur_1}&to={cur_2}&amount={amount}"

    @staticmethod
    def loads(string_: str) -> dict:
        """Parse string to dict"""
        return loads(string_)
