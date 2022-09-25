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

    cur_exch_obj = CurrencyExchangeService(engine)

    @patch('builtins.print', return_value=None)
    def test__check_number_of_accounts_not_available_accounts(self, mock_print):
        """Check if the check_number_of_accounts method returns False for no accounts"""
        self.cur_exch_obj.accounts = False

        self.assertFalse(self.cur_exch_obj._check_number_of_accounts(),
                         'Method test__check_number_of_accounts_not_available_accounts return wrong values')

    @patch('builtins.print', return_value=None)
    def test__check_number_of_accounts_available_accounts(self, mock_print):
        """Check if the check_number_of_accounts method returns True for available accounts"""
        self.cur_exch_obj.accounts = True

        self.assertTrue(self.cur_exch_obj._check_number_of_accounts(),
                        'Method test__check_number_of_accounts_available_accounts return wrong values')

    @patch('builtins.print', return_value=None)
    def test__check_funds_in_your_account_false(self, mock_print):
        """Check if the check_funds_in_your_account method returns False if there are no funds available"""
        self.cur_exch_obj.used_account = user_account_named_tuple((1, 1, "78123447299212", "GBP", Decimal(0)))

        self.assertFalse(self.cur_exch_obj._check_funds_in_your_account(),
                         'Method test__check_funds_in_your_account_false return wrong values')

    @patch('builtins.print', return_value=None)
    def test__check_funds_in_your_account_true(self, mock_print):
        """Check if the check_funds_in_your_account method returns False for the available funds"""
        self.cur_exch_obj.used_account = user_account_named_tuple((1, 1, "78123447299212", "GBP", Decimal(5)))

        self.assertTrue(self.cur_exch_obj._check_funds_in_your_account(),
                        'Method test__check_funds_in_your_account_true return wrong values')

    @patch('builtins.print', return_value=None)
    def test__check_balance_after_transaction_false(self, mock_print):
        """Check if the check_balance_after transaction false method returns False
        for insufficient funds on the account to perform the transaction"""
        self.cur_exch_obj.used_account = user_account_named_tuple((1, 1, "78123447299212", "GBP", Decimal(5)))
        self.cur_exch_obj.amount = Decimal(10)

        self.assertFalse(self.cur_exch_obj._check_balance_after_transaction(),
                         'Method test__check_balance_after_transaction_false return wrong values')

    @patch('builtins.print', return_value=None)
    def test__check_balance_after_transaction_true(self, mock_print):
        """Check if the check_balance_after transaction false method returns False
        for sufficient funds on the account to perform the transaction"""
        self.cur_exch_obj.used_account = user_account_named_tuple((1, 1, "78123447299212", "GBP", Decimal(15)))
        self.cur_exch_obj.amount = Decimal(10)

        self.assertTrue(self.cur_exch_obj._check_balance_after_transaction(),
                        'Method test__check_balance_after_transaction_true return wrong values')

    @patch('builtins.print', return_value=None)
    def test__get_amount_in_main_user_currency_with_the_same_currency(self, mock_print):
        """Check if the get_amount_in_main_user_currency_with_the_same_currency
        method returns the same amount if the currencies are the same"""
        logged_in_user = user_data_named_tuple((
            1, "name", "surname", "country", "address", "email@op.pl",
            "510610710", "login", "password", datetime.today(), "GBP"))

        self.cur_exch_obj.amount = 10
        self.cur_exch_obj.used_account = user_account_named_tuple((1, 1, "78123447299212", "GBP", Decimal(15)))

        self.assertEqual(self.cur_exch_obj._get_amount_in_main_user_currency(logged_in_user), 10,
                         'Method test__get_amount_in_main_user_currency_with_the_same_currency return wrong values')

    @patch('builtins.print', return_value=None)
    def test__get_amount_in_main_user_currency_with_exchanged_currency(self, mock_print):
        """Check if the get_amount_in_main_user_currency_with_the_same_currency
        method returns different amounts if the currencies are different"""
        logged_in_user = user_data_named_tuple((
            1, "name", "surname", "country", "address", "email@op.pl",
            "510610710", "login", "password", datetime.today(), "CHF"))

        self.cur_exch_obj.amount = 10
        self.cur_exch_obj.used_account = user_account_named_tuple((1, 1, "78123447299212", "GBP", Decimal(15)))

        self.assertNotEqual(self.cur_exch_obj._get_amount_in_main_user_currency(logged_in_user), 10,
                            'Method test__get_amount_in_main_user_currency_with_exchanged_currency return wrong values')

    @patch('management.services.currency_exchange_service.CurrencyExchangeService._get_all_available_accounts')
    @patch('builtins.print', return_value=None)
    def test__available_accounts_one_available(self, mock_print, mock_avl_acc):
        """Check if the available accounts method returns available accounts"""
        accounts = [(1, 1, "78123431691696655147299212", "USD", Decimal(20))]
        mock_avl_acc.return_value = accounts

        self.cur_exch_obj.used_account = user_account_named_tuple((1, 1, "78123447299212", "GBP", Decimal(15)))

        self.assertEqual(self.cur_exch_obj._available_accounts(1), [user_account_named_tuple(accounts[0])],
                         'Method test__available_accounts_one_available return wrong values')

    @patch('management.services.currency_exchange_service.CurrencyExchangeService._get_all_available_accounts')
    @patch('builtins.print', return_value=None)
    def test__available_accounts_many_available(self, mock_print, mock_avl_acc):
        """Check if the available accounts method returns available accounts"""
        accounts = [(1, 1, "78123431691696655147299212", "USD", Decimal(20)),
                    (2, 1, "78123431691696655147299212", "CHF", Decimal(20)),
                    (3, 1, "78123431691696655147299212", "EUR", Decimal(20))]
        mock_avl_acc.return_value = accounts

        self.cur_exch_obj.used_account = user_account_named_tuple((1, 1, "78123447299212", "GBP", Decimal(15)))

        accounts_result = [user_account_named_tuple(account) for account in accounts]

        self.assertEqual(self.cur_exch_obj._available_accounts(1), accounts_result,
                         'Method test__available_accounts_many_available return wrong values')

    @patch('management.services.currency_exchange_service.CurrencyExchangeService._get_sum_of_all_exchanges')
    @patch('management.services.currency_exchange_service.CurrencyExchangeService._get_all_monthly_exchanges')
    @patch('builtins.print', return_value=None)
    def test__check_commission_not_charged(self, mock_print, mock_all_exch, mock_sum_exch):
        """Check if the check_commission_not_charged method will not charge
        a commission if the condition is not met in terms of the sum and number of transactions"""
        mock_all_exch.return_value = None
        mock_sum_exch.return_value = Decimal(100)

        self.assertEqual(self.cur_exch_obj._check_commission(Decimal(300), 1, "GBP"), (300, 0),
                         'Method test__check_commission_not_charged return wrong values')

    @patch('management.services.currency_exchange_service.CurrencyExchangeService._get_sum_of_all_exchanges')
    @patch('management.services.currency_exchange_service.CurrencyExchangeService._get_all_monthly_exchanges')
    @patch('builtins.print', return_value=None)
    def test__check_commission_charged(self, mock_print, mock_all_exch, mock_sum_exch):
        """Check if the check_commission_not_charged method will charge
        a commission if the condition is met in terms of the sum or number of transactions"""
        mock_all_exch.return_value = None
        mock_sum_exch.return_value = Decimal(900)

        self.assertEqual(self.cur_exch_obj._check_commission(Decimal(300), 1, "GBP"),
                         (Decimal('298.5000'), Decimal('1.5000')),
                         'Method test__check_commission_charged return wrong values')

    @patch('builtins.print', return_value=None)
    def test__get_sum_of_all_exchanges(self, mock_print):
        """Check if get_sum_of_all_exchanges method sums items correctly"""
        items = [(0, 0, Decimal(10)), (0, 0, Decimal(20)), (0, 0, Decimal(30)), (0, 0, Decimal(40))]

        self.assertEqual(self.cur_exch_obj._get_sum_of_all_exchanges(items), 100,
                         'Method test__get_sum_of_all_exchanges return wrong values')

    @patch('management.services.currency_exchange_service.GetReplyAmount.get_value')
    @patch('management.services.currency_exchange_service.CrudRepo.update_by_id', return_value=None)
    @patch('management.services.currency_exchange_service.CurrencyExchangeService._check_commission')
    @patch('management.services.currency_exchange_service.GetReplyWithValueChosenAccCurExch.get_value')
    @patch('builtins.print', return_value=None)
    @patch('management.services.currency_exchange_service.CurrencyExchangeService._available_accounts')
    def test_transaction(self, mock_avl_acc, mock_print, mock_acc_cur, mock_commission, mock_update, mock_amount):
        """Check if the currency exchange operation enters the correct data into the database"""
        mock_avl_acc.return_value = user_account_named_tuple((1, 1, "781234316916966551472992", "USD", Decimal(1000))),
        mock_acc_cur.return_value = 1
        mock_commission.return_value = Decimal(100), 0
        mock_amount.return_value = 100

        logged_in_user = user_data_named_tuple((
            1, "name", "surname", "country", "address", "email@op.pl",
            "510610710", "login", "password", datetime.today(), "GBP"))
        used_account = user_account_named_tuple((2, 1, "92146997371581537734955888", "GBP", Decimal(2000)))

        current_rate_GBP_USD = Decimal(CurrencyExchange().get_result("GBP", "USD", "1")['info']['rate'])
        current_rate_USD_GBP = Decimal(CurrencyExchange().get_result("USD", "GBP", "1")['info']['rate'])

        cur_exch_obj = CurrencyExchangeService(self.engine)
        lastrow = cur_exch_obj.transaction(logged_in_user, used_account)

        result = self.currency_exchange_crud_repo.find_by_id(lastrow)

        self.assertEqual(result[1], 2, 'Different values for id_user_account_out')
        self.assertEqual(result[2], Decimal(100), 'Different values for transfer_amount_out')
        self.assertEqual(result[3], round(current_rate_GBP_USD, 2), 'Different values for exchange_rate_out')
        self.assertEqual(result[4], Decimal(1900), 'Different values for balance_out')
        self.assertEqual(result[5], 1, 'Different values for id_user_account_in')
        self.assertEqual(result[6], round(Decimal(100) * current_rate_GBP_USD, 2),
                         'Different values for transfer_amount_in')
        self.assertEqual(result[7], round(current_rate_USD_GBP, 2), 'Different values for exchange_rate_in')
        self.assertEqual(result[8], Decimal(1000) + (round(current_rate_GBP_USD * Decimal(100), 2)),
                         'Different values for balance_in')
        self.assertEqual(result[10], Decimal(100), 'Different values for amount_in_main_user_currency')
        self.assertEqual(result[11], 0, 'Different values for commission_in_main_user_currency')


if __name__ == '__main__':
    unittest.main()
