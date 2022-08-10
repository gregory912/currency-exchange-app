from sqlalchemy import create_engine
from management.services.currency_exchange_service import *
from management.conversions import user_data_named_tuple
from datetime import datetime
from unittest.mock import patch
import unittest


class MyTestCase(unittest.TestCase):
    username = 'user'
    password = 'user1234'
    database = 'currency_exchange_app_test'
    port = 3310
    url = f'mysql://{username}:{password}@localhost:{port}/{database}'
    engine = create_engine(url, future=True)
    currency_exchange_crud_repo = CrudRepo(engine, CurrencyExchangeTable)

    @patch('builtins.print', return_value=None)
    @patch('management.services.currency_exchange_service.CurrencyExchangeService._available_accounts')
    def test_transaction_not_accounts(self, mock_avl_acc, mock_print):
        """Check that False will be returned for any unavailable transactions"""
        mock_avl_acc.return_value = None
        logged_in_user = user_data_named_tuple((
            1, "name", "surname", "country", "address", "email@op.pl",
            "510610710", "login", "password", datetime.today(), "GBP"))
        used_account = user_account_named_tuple((1, 1, "78123431691696655147299212", "GBP", Decimal(1000)))
        cur_exch_obj = CurrencyExchangeService()
        self.assertFalse(cur_exch_obj.transaction(1, logged_in_user, used_account),
                         'Method test_transaction_not_accounts return wrong values.')

    @patch('builtins.print', return_value=None)
    @patch('management.services.currency_exchange_service.CurrencyExchangeService._available_accounts')
    def test_transaction_balance_0(self, mock_avl_acc, mock_print):
        """Check that for balance 0 False will be returned"""
        mock_avl_acc.return_value = True
        logged_in_user = user_data_named_tuple((
            1, "name", "surname", "country", "address", "email@op.pl",
            "510610710", "login", "password", datetime.today(), "GBP"))
        used_account = user_account_named_tuple((1, 1, "78123431691696655147299212", "GBP", Decimal(0)))
        cur_exch_obj = CurrencyExchangeService()
        self.assertFalse(cur_exch_obj.transaction(1, logged_in_user, used_account),
                         'Method test_transaction_balance_0 return wrong values.')

    @patch('management.services.currency_exchange_service.get_answer')
    @patch('builtins.print', return_value=None)
    @patch('management.services.currency_exchange_service.CurrencyExchangeService._available_accounts')
    def test_transaction_amount_higher_than_balance(self, mock_avl_acc, mock_print, mock_chosen_op):
        """Check if a transaction greater than the balance will be returned to 0"""
        mock_avl_acc.return_value = [1, 2]
        mock_chosen_op.return_value = Decimal(10)
        logged_in_user = user_data_named_tuple((
            1, "name", "surname", "country", "address", "email@op.pl",
            "510610710", "login", "password", datetime.today(), "GBP"))
        used_account = user_account_named_tuple((1, 1, "78123431691696655147299212", "GBP", Decimal(5)))
        cur_exch_obj = CurrencyExchangeService()
        self.assertFalse(cur_exch_obj.transaction(1, logged_in_user, used_account),
                         'Method test_transaction_amount_higher_than_balance return wrong values.')

    @patch('management.services.currency_exchange_service.CrudRepo.update_by_id', return_value=None)
    @patch('management.services.currency_exchange_service.CurrencyExchangeService._check_commission')
    @patch('management.services.currency_exchange_service.get_answer')
    @patch('builtins.print', return_value=None)
    @patch('management.services.currency_exchange_service.CurrencyExchangeService._available_accounts')
    def test_transaction_in_main_user_currency(self, mock_avl_acc, mock_print, mock_get_answer,
                                               mock_commission, mock_update):
        """Check if the currency exchange operation enters the correct data into the database"""
        mock_avl_acc.return_value = user_account_named_tuple((1, 1, "781234316916966551472992", "USD", Decimal(1000))),
        mock_get_answer.side_effect = [1, Decimal(100)]
        mock_commission.return_value = Decimal(100), 0

        logged_in_user = user_data_named_tuple((
            1, "name", "surname", "country", "address", "email@op.pl",
            "510610710", "login", "password", datetime.today(), "GBP"))
        used_account = user_account_named_tuple((2, 1, "92146997371581537734955888", "GBP", Decimal(2000)))

        current_rate_GBP_USD = Decimal(CurrencyExchange().get_result("GBP", "USD", "1")['info']['rate'])
        current_rate_USD_GBP = Decimal(CurrencyExchange().get_result("USD", "GBP", "1")['info']['rate'])

        cur_exch_obj = CurrencyExchangeService()
        lastrow = cur_exch_obj.transaction(self.engine, logged_in_user, used_account)

        result = self.currency_exchange_crud_repo.find_by_id(lastrow)

        self.assertEqual(result[1], 2,
                         'Method test_transaction_in_main_user_currency return wrong values. '
                         'Different values for id_user_account_out')
        self.assertEqual(result[2], Decimal(100),
                         'Method test_transaction_in_main_user_currency return wrong values. '
                         'Different values for transfer_amount_out')
        self.assertEqual(result[3], round(current_rate_GBP_USD, 2),
                         'Method test_transaction_in_main_user_currency return wrong values. '
                         'Different values for exchange_rate_out')
        self.assertEqual(result[4], Decimal(1900),
                         'Method test_transaction_in_main_user_currency return wrong values. '
                         'Different values for balance_out')
        self.assertEqual(result[5], 1,
                         'Method test_transaction_in_main_user_currency return wrong values. '
                         'Different values for id_user_account_in')
        self.assertEqual(result[6], round(Decimal(100) * current_rate_GBP_USD, 2),
                         'Method test_transaction_in_main_user_currency return wrong values. '
                         'Different values for transfer_amount_in')
        self.assertEqual(result[7], round(current_rate_USD_GBP, 2),
                         'Method test_transaction_in_main_user_currency return wrong values. '
                         'Different values for exchange_rate_in')
        self.assertEqual(result[8], Decimal(1000) + (round(current_rate_GBP_USD * Decimal(100), 2)),
                         'Method test_transaction_in_main_user_currency return wrong values. '
                         'Different values for balance_in')
        self.assertEqual(result[10], Decimal(100),
                         'Method test_transaction_in_main_user_currency return wrong values. '
                         'Different values for amount_in_main_user_currency')
        self.assertEqual(result[11], 0,
                         'Method test_transaction_in_main_user_currency return wrong values. '
                         'Different values for commission_in_main_user_currency')
