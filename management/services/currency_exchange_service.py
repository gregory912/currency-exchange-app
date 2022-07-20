import requests
import json
from management.validation import *
from management.conversions import *
from data_base.model.tables import UserAccountTable, CurrencyExchangeTable, ApiRequestTable
from decimal import Decimal
from data_base.repository.crud_repo import CrudRepo
from datetime import datetime


class CurrencyExchangeService:
    def __init__(self):
        self.cur_exch_obj = CurrencyExchange()

    def transaction(self, engine, id_user_data: int, used_account: namedtuple):
        accounts = self.available_accounts(engine, id_user_data, used_account)
        if not accounts:
            print(f"\n{' ' * 12}You don't have any account other than your main account. "
                  f"Create a new account to be able to exchange currencies")
        else:
            chosen_operation = get_answer(
                validation_chosen_operation,
                'Select the currency for which you want to perform currency exchange: ',
                'Entered data contains illegal characters. Try again: ',
                (1, len(accounts)))
            amount = get_answer(
                validation_decimal,
                'Enter the amount: ',
                'Entered data contains illegal characters. Try again: ')
            if Decimal(amount) > used_account.balance:
                print(f"\n{' ' * 12}You do not have enough funds on your account to perform this operation.")
            else:
                if self.check_number_of_api_queries(engine):
                    transaction_account = accounts[int(chosen_operation)-1]
                    self.cur_exch_obj.get_result(used_account.currency, transaction_account.currency, amount)
                    exchange = self.cur_exch_obj.unpack_data()
                    exch_cur_out = {
                        'rate': exchange['rate'],
                        'amount': amount,
                        'balance': used_account.balance-Decimal(amount)}
                    exch_cur_in = {
                        'rate': round(float(amount)/float(exchange['amount']), 5),
                        'amount': round(exchange['amount'], 3),
                        'balance': round(transaction_account.balance+Decimal(exchange['amount']), 3)}
                    CrudRepo(engine, UserAccountTable).update_by_id(
                        used_account.id,
                        id=used_account.id,
                        id_user_data=used_account.id_user_data,
                        account_number=used_account.account_number,
                        currency=used_account.currency,
                        balance=exch_cur_out['balance'])
                    CrudRepo(engine, UserAccountTable).update_by_id(
                        transaction_account.id,
                        id=transaction_account.id,
                        id_user_data=transaction_account.id_user_data,
                        account_number=transaction_account.account_number,
                        currency=transaction_account.currency,
                        balance=exch_cur_in['balance'])
                    CrudRepo(engine, CurrencyExchangeTable).add(
                        id_user_account_out=used_account.id,
                        transfer_amount_out=exch_cur_out['amount'],
                        exchange_rate_out=exch_cur_out['rate'],
                        balance_out=exch_cur_out['balance'],
                        id_user_account_in=transaction_account.id,
                        transfer_amount_in=exch_cur_in['amount'],
                        exchange_rate_in=exch_cur_in['rate'],
                        balance_in=exch_cur_in['balance'],
                        transaction_time=datetime.now()
                    )
                else:
                    print(f'\n{" " * 12}Unfortunately we are unable to make an exchange. '
                          'Query limit for today has been exhausted. Please try again tomorrow.')

    @staticmethod
    def check_number_of_api_queries(engine):
        """Check if the number of inquiries for a given day has not been exceeded"""
        api_queries = CrudRepo(engine, ApiRequestTable).find_by_id(1)
        if not api_queries:
            CrudRepo(engine, ApiRequestTable).add(transactions_a_day=1, transactions_date=datetime.now())
            return True
        else:
            if api_queries.transactions_date.strftime('%Y-%m-%d') != datetime.now().strftime('%Y-%m-%d'):
                CrudRepo(engine, ApiRequestTable).update_by_id(
                    1,
                    transactions_a_day=1,
                    transactions_date=datetime.now())
                return True
            elif api_queries.transactions_a_day == 250:
                return False
            else:
                CrudRepo(engine, ApiRequestTable).update_by_id(
                    1,
                    transactions_a_day=api_queries.transactions_a_day + 1,
                    transactions_date=api_queries.transactions_date)
                return True

    @staticmethod
    def available_accounts(engine, id_user_data: int, used_account: namedtuple) -> list:
        """Get all accounts that can be used for currency exchange"""
        # accounts = UserAccountRepo(engine, UserAccountTable).find_all_accounts(id_user_data)
        accounts = CrudRepo(engine, UserAccountTable).find_all_with_condition((
                UserAccountTable.id_user_data, id_user_data))
        accounts_named_tuple = [user_account_named_tuple(acc) for acc in accounts if acc[3] != used_account.currency]
        for x in range(0, len(accounts_named_tuple)):
            print(f"{' ' * 12}", x + 1, ' ', accounts_named_tuple[x].currency)
        return accounts_named_tuple


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
        return requests.request("GET", self.url, headers=self.headers, data=self.payload)

    def unpack_data(self) -> dict:
        """Return the data in the appropriate form"""
        if not self._response:
            raise Exception('You cannot unpack the data until you get the query')
        return {'rate': self._response['info']['rate'], 'amount': self._response['result']}

    @staticmethod
    def get_url(cur_1: str, cur_2: str, amount: str) -> str:
        """Get url to API for entered data"""
        return f"https://api.apilayer.com/exchangerates_data/convert?to={cur_2}&from={cur_1}&amount={amount}"

    @staticmethod
    def loads(string_: str) -> dict:
        """Parse string to dict"""
        return json.loads(string_)
