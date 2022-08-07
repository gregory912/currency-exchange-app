from tests.database.common import *
from database.repository.crud_repo import CrudRepo
from database.repository.card_repo import CardRepo
from database.repository.user_account_repo import UserAccountRepo
from database.model.tables import *
from sqlalchemy import create_engine
from datetime import datetime, date
from unittest.mock import patch
import unittest


class MyTestCase(unittest.TestCase):
    username = 'user'
    password = 'user1234'
    database = 'currency_exchange_app_test'
    port = 3310
    url = f'mysql://{username}:{password}@localhost:{port}/{database}'
    engine = create_engine(url, future=True)
    user_account_crud_repo = UserAccountRepo(engine, UserAccountTable)
    user_data_crud_repo = CrudRepo(engine, UserDataTable)
    card_card_repo = CardRepo(engine, CardTable)
    card_trans_card_repo = CardRepo(engine, CardTransactionTable)
    currency_exchange_crud_repo = CrudRepo(engine, CurrencyExchangeTable)

    def test_check_if_account_exist(self):
        """Create a new user and add a row to the user_account table based on the id.
        Check if the check_if_account_exist function returns the entered row."""
        user_data_data = get_user_data(f"{draw_letters(10)}@op.pl", 9, 10)
        user_data_lastrow = self.user_data_crud_repo.add(**user_data_data)

        user_account_data = get_user_account(user_data_lastrow, draw_numbers(26), 800.00) | {"currency": "CHF"}
        self.user_account_crud_repo.add(**user_account_data)

        data_from_db = self.user_account_crud_repo.check_if_account_exist(user_data_lastrow, "CHF")
        self.assertEqual(data_from_db[3], "CHF", 'Method test_check_if_account_exist return wrong values')

    def test_find_btwn_dates(self):
        """Create a new user and based on the id add a line in user_account and card.
        Based on card_id and user_account_id, add 3 rows in card_transaction.
        Based on the find_btwn_dates function, check if the items with the correct dates were returned."""
        user_data_data = get_user_data(f"{draw_letters(10)}@op.pl", 9, 10)
        user_data_lastrow = self.user_data_crud_repo.add(**user_data_data)

        user_account_data = get_user_account(user_data_lastrow, draw_numbers(26), 800.00)
        user_account_lastrow = self.user_account_crud_repo.add(**user_account_data)

        card_data = get_cards(draw_numbers(16)) | {"id_user_data": user_data_lastrow}
        card_lastrow = self.card_card_repo.add(**card_data)

        card_transactions = get_card_transaction(int(draw_numbers(4))) | {
            "id_user_account": user_account_lastrow, "id_card": card_lastrow,
            "transaction_time": datetime.strptime("2022 08 10 20 08 05", "%Y %m %d %H %M %S")}
        card_transactions_2 = get_card_transaction(int(draw_numbers(4))) | {
            "id_user_account": user_account_lastrow, "id_card": card_lastrow,
            "transaction_time": datetime.strptime("2022 08 02 20 08 05", "%Y %m %d %H %M %S")}
        card_transactions_3 = get_card_transaction(int(draw_numbers(4))) | {
            "id_user_account": user_account_lastrow, "id_card": card_lastrow,
            "transaction_time": datetime.strptime("2022 08 20 20 08 05", "%Y %m %d %H %M %S")}

        self.card_trans_card_repo.add(**card_transactions)
        self.card_trans_card_repo.add(**card_transactions_2)
        self.card_trans_card_repo.add(**card_transactions_3)

        data_from_db = UserAccountRepo(self.engine, CardTransactionTable).find_btwn_dates((
            CardTransactionTable.transaction_time,
            date.fromisoformat('2022-08-08'),
            date.fromisoformat('2022-08-21'),
            CardTransactionTable.id_user_account,
            user_account_lastrow
        ))
        self.assertEqual(data_from_db[0][1], user_account_lastrow, 'Method test_find_btwn_dates return wrong values')
        self.assertEqual(data_from_db[0][2], datetime.strptime("2022 08 10 20 08 05", "%Y %m %d %H %M %S"),
                         'Method test_find_btwn_dates return wrong values')
        self.assertEqual(len(data_from_db), 2, 'Method test_find_btwn_dates return wrong values')

    @patch('management.services.common.fst_day_of_this_month', return_value=date.fromisoformat('2022-08-06'))
    @patch('management.services.common.fst_day_of_next_month', return_value=date.fromisoformat('2022-08-01'))
    def test_get_monthly_exchanges_for_user(self, fst_day, last_day):
        """Create a new user and based on the id add a line in user_account and card.
        Based on card_id and user_account_id, add 3 rows in currency_exchange with different dates.
        Functions fst_day_of_this_month and fst_day_of_next_month have been mocked
        to check if returned values are valid"""
        user_data_data = get_user_data(f"{draw_letters(10)}@op.pl", 9, 10)
        user_data_lastrow = self.user_data_crud_repo.add(**user_data_data)

        user_account_data_1 = get_user_account(user_data_lastrow, draw_numbers(26), 800.00)
        user_account_lastrow_1 = self.user_account_crud_repo.add(**user_account_data_1)

        user_account_data_2 = get_user_account(user_data_lastrow, draw_numbers(26), 800.00)
        user_account_lastrow_2 = self.user_account_crud_repo.add(**user_account_data_2)

        currency_exchange_1 = get_currency_exchange(user_account_lastrow_1, user_account_lastrow_2,
                                                    datetime.strptime("2022 07 01 20 08 05", "%Y %m %d %H %M %S"))
        currency_exchange_2 = get_currency_exchange(user_account_lastrow_1, user_account_lastrow_2,
                                                    datetime.strptime("2022 08 05 20 08 05", "%Y %m %d %H %M %S"))
        currency_exchange_3 = get_currency_exchange(user_account_lastrow_1, user_account_lastrow_2,
                                                    datetime.strptime("2022 08 10 20 08 05", "%Y %m %d %H %M %S"))

        self.currency_exchange_crud_repo.add(**currency_exchange_1)
        self.currency_exchange_crud_repo.add(**currency_exchange_2)
        self.currency_exchange_crud_repo.add(**currency_exchange_3)

        data_from_db = UserAccountRepo(self.engine, CurrencyExchangeTable).get_monthly_exchanges_for_user(
            user_data_lastrow, fst_day(), last_day())
        self.assertEqual(len(data_from_db), 1, 'Method test_find_btwn_dates return wrong values')


if __name__ == '__main__':
    unittest.main()
