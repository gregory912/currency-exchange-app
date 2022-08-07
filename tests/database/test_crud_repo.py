from tests.database.generate_data_for_tests import GenerateData
from database.repository.crud_repo import CrudRepo
from database.model.tables import *
from sqlalchemy import create_engine
from datetime import datetime, date
from decimal import Decimal
import unittest
import random


class MyTestCase(unittest.TestCase):
    username = 'user'
    password = 'user1234'
    database = 'currency_exchange_app_test'
    port = 3310
    url = f'mysql://{username}:{password}@localhost:{port}/{database}'
    engine = create_engine(url, future=True)
    metadata = base.metadata
    metadata.create_all(engine)
    user_account_crud_repo = CrudRepo(engine, UserAccountTable)
    user_data_crud_repo = CrudRepo(engine, UserDataTable)
    card_crud_repo = CrudRepo(engine, CardTable)

    def setUp(self) -> None:
        if not GenerateData.check_data(self.engine):
            GenerateData.generate_data(self.engine)

    def test_add_and_get_last_row(self):
        """The function tests add and get_last_row methods from crud_repo file"""
        data = {"id_user_data": 1, "account_number": self.draw_numbers(26),
                "currency": "USD", "balance": Decimal(800.00)}
        self.user_account_crud_repo.add(**data)
        received_data = self.user_account_crud_repo.get_last_row()
        self.assertEqual(self.dict_to_tuple(data), received_data[1:],
                         'Method test_add_and_get_last_row return wrong values')

    def test_add_join(self):
        """The function tests add_join method from crud_repo file"""
        user_data = {
            "name": "name", "surname": "surname", "country": "country", "address": "address",
            "email": f"{self.draw_letters(10)}@op.pl", "phone": self.draw_numbers(9),
            "login": self.draw_letters(10), "password": self.draw_letters(10),
            "creation_date": self.get_current_time(), "main_currency": "GBP"}
        cards_data = {
            "card_number": self.draw_letters(10),
            "valid_thru": date.today(),
            "cvv": "123",
            "blocked": False,
            "daily_limit": 2000,
            "internet_limit": 1000,
            "contactless_limit": 100,
            "card_pin": "1234",
            "sec_online_transactions": True,
            "sec_location": False,
            "sec_magnetic_strip": False,
            "sec_withdrawals_atm": True,
            "sec_contactless": True,
            "card_name": "card name",
            "card_type": "STANDARD",
            "main_currency": "GBP"}
        user = UserDataTable(**user_data)
        card = CardTable(**cards_data)
        user.cards_to_user_data = card
        self.user_data_crud_repo.add_join(user)
        last_row_user_data = self.user_data_crud_repo.get_last_row()
        last_row_card = self.card_crud_repo.get_last_row()
        self.assertEqual(self.dict_to_tuple(user_data), last_row_user_data[1:],
                         'Method test_add_join return wrong values')
        self.assertEqual(self.dict_to_tuple(cards_data), last_row_card[2:],
                         'Method test_add_join return wrong values')

    def test_find_by_id_and_update_by_id(self):
        """The function takes a given row from the table, modifies it and
        checks if the modified row differs from the one taken at the beginning"""
        user_account_before_update = self.user_account_crud_repo.find_by_id(1)
        CrudRepo(self.engine, UserAccountTable).update_by_id(
            user_account_before_update[0],
            id_user_data=user_account_before_update[1],
            account_number=self.draw_numbers(26),
            currency=user_account_before_update[3],
            balance=user_account_before_update[4])
        user_account_after_update = self.user_account_crud_repo.find_by_id(1)
        self.assertNotEqual(user_account_before_update, user_account_after_update,
                            'Methods test_find_by_id_and_update_by_id return wrong values')

    def test_add_and_get_last_row_and_find_by_id_choose_columns(self):
        """Enter the row with the randomly selected account number. Get last added row to have id information.
        On the basis of the id, take only the account number and compare
        it with the randomly selected account number."""
        account_number = self.draw_numbers(26)
        data = {"id_user_data": 1, "account_number": account_number,
                "currency": "USD", "balance": Decimal(800.00)}
        self.user_account_crud_repo.add(**data)
        user_account = self.user_account_crud_repo.get_last_row()
        user_account_only_column = self.user_account_crud_repo.find_by_id_choose_columns(
            user_account[0],
            (UserAccountTable.account_number, ))
        self.assertEqual(account_number, user_account_only_column[0],
                         'Method test_add_and_get_last_row_and_find_by_id_choose_columns return wrong values')

    def test_add_and_get_last_row_and_find_all_by_id(self):
        """Enter a row in the database, then use this function find_all_by_id
         to retrieve items from the database and check if the items are the same"""
        data = {"id_user_data": 1, "account_number": self.draw_numbers(26),
                "currency": "USD", "balance": Decimal(800.00)}
        self.user_account_crud_repo.add(**data)
        user_account = self.user_account_crud_repo.get_last_row()
        user_account_from_db = self.user_account_crud_repo.find_all_by_id([user_account[0]])
        self.assertEqual(self.dict_to_tuple(data), user_account_from_db[0][1:],
                         'Method test_add_and_get_last_row_and_find_all_by_id return wrong values')

    def test_add_and_find_all(self):
        """Get all elements from user_accounts table,
        calculate how many items have been downloaded from the database.
        Add a new row to the table, then get all the elements and check
        if there is one more element in the table than before."""
        data_before_adding = len(self.user_account_crud_repo.find_all())
        data = {"id_user_data": 1, "account_number": self.draw_numbers(26),
                "currency": "USD", "balance": Decimal(800.00)}
        self.user_account_crud_repo.add(**data)
        data_after_adding = len(self.user_account_crud_repo.find_all())
        self.assertEqual(data_before_adding + 1, data_after_adding, 'Method test_add_and_find_all return wrong values')

    def test_find_all_with_condition(self):
        """Get the first row from the database.
        Check if the fetched line has id = 1"""
        data = self.user_account_crud_repo.find_first_with_condition((UserAccountTable.id, 1))
        self.assertEqual(data[0], 1, 'Method test_find_all_with_condition return wrong values')

    def test_find_first_with_condition(self):
        """Using find_first_with_condition check if the element is returned as in the entered condition and
        if the element has the same id as the previously entered element with the same condition"""
        data = self.user_account_crud_repo.find_first_with_condition((UserAccountTable.currency, "USD"))
        self.assertEqual(data[3], "USD", 'Method test_find_first_with_condition return wrong values')
        self.assertEqual(data[0], 2, 'Method test_find_first_with_condition return wrong values')

    def test_find_between(self):
        """Check that the find between function is returning the correct data"""
        data = self.user_data_crud_repo.find_between((UserDataTable.id, 1, 2))
        self.assertEqual(len(data), 2, 'Method test_find_between return wrong values')
        self.assertEqual(data[0][0], 1, 'Method test_find_between return wrong values')
        self.assertEqual(data[1][0], 2, 'Method test_find_between return wrong values')

    def test_get_last_row_and_delete_by_id(self):
        """Check the number of the last row, delete it and check if the values match"""
        user_account_before_deleting = self.user_account_crud_repo.get_last_row()
        self.user_account_crud_repo.delete_by_id(user_account_before_deleting[0])
        user_account_after_deleting = self.user_account_crud_repo.get_last_row()
        self.assertEqual(user_account_before_deleting[0], user_account_after_deleting[0] + 1,
                         'Method test_find_between return wrong values')

    def test_delete_all_by_id(self):
        """Check the number of the last row, delete 2 rows and check if the values match"""
        user_account_before_deleting = self.user_account_crud_repo.get_last_row()
        self.user_account_crud_repo.delete_all_by_id([user_account_before_deleting[0] - 1,
                                                     user_account_before_deleting[0]])
        user_account_after_deleting = self.user_account_crud_repo.get_last_row()
        self.assertEqual(user_account_before_deleting[0], user_account_after_deleting[0] + 2,
                         'Method test_find_between return wrong values')

    def test_add_join_and_join_with_condition(self):
        """Add data to the user_data and user_accounts tables,
        then download the data using join_with_condition and check if they match"""
        email = f"{self.draw_letters(10)}@op.pl"
        card_number = self.draw_letters(10)
        user_data = {
            "name": "name", "surname": "surname", "country": "country", "address": "address",
            "email": email, "phone": self.draw_numbers(9),
            "login": self.draw_letters(10), "password": self.draw_letters(10),
            "creation_date": self.get_current_time(), "main_currency": "GBP"}
        cards_data = {
            "card_number": card_number,
            "valid_thru": date.today(),
            "cvv": "123",
            "blocked": False,
            "daily_limit": 2000,
            "internet_limit": 1000,
            "contactless_limit": 100,
            "card_pin": "1234",
            "sec_online_transactions": True,
            "sec_location": False,
            "sec_magnetic_strip": False,
            "sec_withdrawals_atm": True,
            "sec_contactless": True,
            "card_name": "card name",
            "card_type": "STANDARD",
            "main_currency": "GBP"}
        user = UserDataTable(**user_data)
        card = CardTable(**cards_data)
        user.cards_to_user_data = card
        self.user_data_crud_repo.add_join(user)
        data = self.user_data_crud_repo.join_with_condition(
            CardTable,
            (UserDataTable.email, CardTable.card_number),
            (UserDataTable.email, email))
        self.assertEqual(len(data), 1, 'Method test_add_join_and_join_with_condition return wrong values')
        self.assertEqual(email, data[0][0], 'Method test_add_join_and_join_with_condition return wrong values')
        self.assertEqual(card_number, data[0][1], 'Method test_add_join_and_join_with_condition return wrong values')
        self.assertEqual(len(data[0]), 2, 'Method test_add_join_and_join_with_condition return wrong values')

    def test_find_all_and_join(self):
        """There is a one-to-many relationship between the user_data and cards tables,
        check whether the returned number of elements from the join method
        will be the same as the number of elements in the cards table"""
        data_all = self.card_crud_repo.find_all()
        data = self.user_data_crud_repo.join(
            CardTable,
            (UserDataTable.email, CardTable.card_number))
        self.assertEqual(len(data_all), len(data), 'Method test_add_join_and_join_with_condition return wrong values')
        self.assertEqual(len(data[0]), 2, 'Method test_add_join_and_join_with_condition return wrong values')

    @staticmethod
    def dict_to_tuple(dict_: dict) -> tuple:
        """Convert dict to tuple"""
        return tuple([x for x in dict_.values()])

    @staticmethod
    def draw_numbers(elements: int) -> str:
        """The method randomizes the numbers and returns a string"""
        return ''.join([str(random.randint(1, 9)) for _ in range(elements)])

    @staticmethod
    def draw_letters(elements: int) -> str:
        """The method randomizes the numbers and returns a string"""
        return ''.join([chr(random.randint(97, 122)) for _ in range(elements)])

    @staticmethod
    def get_current_time() -> datetime:
        """Get today's date without milliseconds"""
        current_time = datetime.now().strftime("%Y %m %d %H %M %S")
        return datetime.strptime(current_time, "%Y %m %d %H %M %S")


if __name__ == '__main__':
    unittest.main()
