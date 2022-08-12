from management.conversions import user_account_named_tuple
from management.services.common import *
from database.model.tables import UserAccountTable, CurrencyExchangeTable, UserDataTable
from database.repository.crud_repo import CrudRepo
from database.repository.user_account_repo import UserAccountRepo
from datetime import datetime
from requests import request
from json import loads
from decimal import Decimal


class CurrencyExchangeService:
    def __init__(self, engine):
        self.engine = engine

        self.cur_exch_obj = CurrencyExchange()
        self.user_account_crud_repo = CrudRepo(self.engine, UserAccountTable)

    def transaction(self, logged_in_user: namedtuple, used_account: namedtuple):
        """Perform currency exchange transactions. Take account of account availability and account balance.
        Get commissions if required. Transfer money from one account to another with information about the rate
        and balance after the operation.
        amount_out ---> amount in main user currency - commission ---> amount in"""
        accounts = self._available_accounts(logged_in_user.id, used_account)
        if not accounts:
            print(f"\n{' ' * 12}You don't have any account other than your main account. "
                  f"Create a new account to be able to exchange currencies")
            return False
        else:
            if used_account.balance == 0:
                print(f"\n{' ' * 12}You do not have enough funds on your account to perform this operation.")
                return False
            else:
                chosen_operation = get_answer(
                    validation_chosen_operation,
                    'Select the currency for which you want to perform currency exchange: ',
                    'Entered data contains illegal characters. Try again: ',
                    (1, len(accounts)))
                amount = Decimal(get_answer(
                    validation_decimal,
                    'Enter the amount: ',
                    'Entered data contains illegal characters. Try again: '))
                if amount > used_account.balance:
                    print(f"\n{' ' * 12}You do not have enough funds on your account to perform this operation.")
                    return False
                else:
                    transaction_account = accounts[int(chosen_operation) - 1]
                    if logged_in_user.main_currency != used_account.currency:
                        amount_in_main_user_currency = Decimal(self.cur_exch_obj.get_result(
                            used_account.currency, logged_in_user.main_currency, str(amount))['result'])
                    else:
                        amount_in_main_user_currency = amount
                    amt_after_checking, commission_after_checking = CurrencyExchangeService._check_commission(
                        self.engine, amount_in_main_user_currency, logged_in_user.id, logged_in_user.main_currency)
                    exchanged_amount = self.cur_exch_obj.get_result(
                        logged_in_user.main_currency, transaction_account.currency, str(amt_after_checking))['result']
                    rate_acc_to_trans = self.cur_exch_obj.get_result(
                        used_account.currency, transaction_account.currency, str(1))['info']['rate']
                    rate_trans_to_acc = self.cur_exch_obj.get_result(
                        transaction_account.currency, used_account.currency, str(1))['info']['rate']
                    exch_cur_out = {
                        'rate': rate_acc_to_trans,
                        'amount': amount,
                        'balance': used_account.balance-Decimal(amount)}
                    exch_cur_in = {
                        'rate': rate_trans_to_acc,
                        'amount': exchanged_amount,
                        'balance': round(transaction_account.balance+Decimal(exchanged_amount), 3)}
                    self.user_account_crud_repo.update_by_id(
                        used_account.id,
                        id=used_account.id,
                        id_user_data=used_account.id_user_data,
                        account_number=used_account.account_number,
                        currency=used_account.currency,
                        balance=exch_cur_out['balance'])
                    self.user_account_crud_repo.update_by_id(
                        transaction_account.id,
                        id=transaction_account.id,
                        id_user_data=transaction_account.id_user_data,
                        account_number=transaction_account.account_number,
                        currency=transaction_account.currency,
                        balance=exch_cur_in['balance'])
                    lastrow = CrudRepo(self.engine, CurrencyExchangeTable).add(
                        id_user_account_out=used_account.id,
                        transfer_amount_out=exch_cur_out['amount'],
                        exchange_rate_out=exch_cur_out['rate'],
                        balance_out=exch_cur_out['balance'],
                        id_user_account_in=transaction_account.id,
                        transfer_amount_in=exch_cur_in['amount'],
                        exchange_rate_in=exch_cur_in['rate'],
                        balance_in=exch_cur_in['balance'],
                        transaction_time=datetime.now(),
                        amount_in_main_user_currency=amount_in_main_user_currency,
                        commission_in_main_user_currency=commission_after_checking
                    )
                    print(f"\n{' ' * 12}The transaction was successful.")
                    return lastrow

    def _available_accounts(self, id_user_data: int, used_account: namedtuple) -> list:
        """Get all accounts that can be used for currency exchange"""
        accounts = self.user_account_crud_repo.find_all_with_condition((
                UserAccountTable.id_user_data, id_user_data))
        accounts_named_tuple = [user_account_named_tuple(acc) for acc in accounts if acc[3] != used_account.currency]
        for x, item in enumerate(accounts_named_tuple):
            print(f"{' ' * 12}", x + 1, ' ', item.currency)
        return accounts_named_tuple

    def _check_commission(self, amount: Decimal, id_user_data: int, currency: str) -> tuple:
        """Check if a commission is required. The amount and commission are stated in the user's primary currency."""
        all_exchanges = UserAccountRepo(self.engine, UserDataTable).get_monthly_exchanges_for_user(
            id_user_data, fst_day_of_this_month(), fst_day_of_next_month())
        transaction_sum = sum([item[2] for item in all_exchanges])
        if transaction_sum + amount > 1000:
            print(f"\n{' ' * 12}You have exceeded the monthly exchange limit of 1000 {currency}. "
                  f"A commission of 0.5% of the entered amount has been charged.")
            return amount - (amount * Decimal(0.005)), amount * Decimal(0.005)
        return amount, 0


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
