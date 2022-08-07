from tests.database.generate_data_for_tests import GenerateData
from tests.database.common import *
from database.repository.crud_repo import CrudRepo
from database.repository.card_repo import CardRepo
from database.model.tables import UserAccountTable, UserDataTable, CardTable, CardTransactionTable
from management.services.common import fst_day_of_this_month, fst_day_of_next_month
from sqlalchemy import create_engine
from decimal import Decimal
import unittest


class MyTestCase(unittest.TestCase):
    username = 'user'
    password = 'user1234'
    database = 'currency_exchange_app_test'
    port = 3310
    url = f'mysql://{username}:{password}@localhost:{port}/{database}'
    engine = create_engine(url, future=True)
    user_account_crud_repo = CrudRepo(engine, UserAccountTable)
    user_data_crud_repo = CrudRepo(engine, UserDataTable)
    card_card_repo = CardRepo(engine, CardTable)
    card_trans_card_repo = CardRepo(engine, CardTransactionTable)

    def setUp(self) -> None:
        if not GenerateData.check_data(self.engine):
            GenerateData.generate_data(self.engine)

    def test_join_cards_and_find_all_cards(self):
        """Get the last rows from the user_data and cards tables,
        then add 1 row to the user_data table and 2 to the cards table.
        Check if the elements match. Use the find_all_cards method to check if the downloaded
        cards have the same card number as the created numbers"""
        user_data_id_before_adding = self.user_data_crud_repo.get_last_row()[0]
        cards_id_before_adding = self.card_card_repo.get_last_row()[0]

        card_number = draw_numbers(16)
        card_number2 = draw_numbers(16)
        user_data = get_user_data(f"{draw_letters(10)}@op.pl", 9, 10)

        user = UserDataTable(**user_data)
        cards = [CardTable(**get_cards(card_number)), CardTable(**get_cards(card_number2))]

        cards[0].user_data_to_cards = user
        cards[1].user_data_to_cards = user
        self.user_data_crud_repo.add_join_many(cards)

        user_data_id_after_adding = self.user_data_crud_repo.get_last_row()[0]
        cards_id_after_adding = self.card_card_repo.get_last_row()[0]

        cards_ids_from_db = self.card_card_repo.join_cards(UserDataTable, "STANDARD", user_data_id_after_adding)
        cards_data_from_db = self.card_card_repo.find_all_cards(user_data_id_after_adding)

        self.assertEqual(user_data_id_before_adding, user_data_id_after_adding - 1,
                         'Method test_join_cards_and_find_all_cards return wrong values')
        self.assertEqual(cards_id_before_adding, cards_id_after_adding - 2,
                         'Method test_join_cards_and_find_all_cards return wrong values')
        self.assertEqual(cards_ids_from_db[0][0], cards_id_after_adding - 1,
                         'Method test_join_cards_and_find_all_cards return wrong values')
        self.assertEqual(cards_ids_from_db[1][0], cards_id_after_adding,
                         'Method test_join_cards_and_find_all_cards return wrong values')

        self.assertEqual(cards_data_from_db[0][1], card_number,
                         'Method test_join_cards_and_find_all_cards return wrong values')
        self.assertEqual(cards_data_from_db[1][1], card_number2,
                         'Method test_join_cards_and_find_all_cards return wrong values')

    def test_get_monthly_card_trans_for_user(self):
        """Create a new user and based on the id add a row in user_account and card.
        Based on card_id and user_account_id, add 2 rows in card_transaction. Using the id from the user_data table,
        add download recently added transactions and check if they match."""
        user_data_data = get_user_data(f"{draw_letters(10)}@op.pl", 9, 10)
        user_data_lastrow = self.user_data_crud_repo.add(**user_data_data)

        user_account_data = get_user_account(user_data_lastrow, draw_numbers(26), 800.00)
        user_account_lastrow = self.user_account_crud_repo.add(**user_account_data)

        card_data = get_cards(draw_numbers(16)) | {"id_user_data": user_data_lastrow}
        card_lastrow = self.card_card_repo.add(**card_data)

        card_transactions = get_card_transaction(int(draw_numbers(4))) | {
            "id_user_account": user_account_lastrow, "id_card": card_lastrow,
            "transaction_type": "Withdrawals ATM", "amount_in_main_user_currency": Decimal(625.00)}
        card_transactions_2 = get_card_transaction(int(draw_numbers(4))) | {
            "id_user_account": user_account_lastrow, "id_card": card_lastrow,
            "transaction_type": "Withdrawals ATM", "amount_in_main_user_currency": Decimal(525.00)}

        self.card_trans_card_repo.add(**card_transactions)
        self.card_trans_card_repo.add(**card_transactions_2)

        monthly_cards_trans = CardRepo(self.engine, CardTable).get_monthly_card_trans_for_user(
            user_data_lastrow, fst_day_of_this_month(), fst_day_of_next_month())
        all_trans = self.card_trans_card_repo.find_all()

        self.assertEqual(monthly_cards_trans[0][0], Decimal(625.00),
                         'Method test_get_monthly_card_trans_for_user return wrong values')
        self.assertEqual(monthly_cards_trans[1][0], Decimal(525.00),
                         'Method test_get_monthly_card_trans_for_user return wrong values')
        self.assertNotEqual(len(monthly_cards_trans), len(all_trans),
                            'Method test_get_monthly_card_trans_for_user return wrong values')


if __name__ == '__main__':
    unittest.main()
