from management.validation import *
from data_base.repository.crud_repo import CrudRepo
from data_base.repository.card_repo import CardRepo
from data_base.model.tables import *
from random import randint
from decimal import Decimal
from management.conversions import *
from datetime import date


class CardService:
    @staticmethod
    def user_without_card(engine, logged_in_user: namedtuple):
        """Create an account for the new user and then update the service"""
        print(f"{' ' * 12}You don't have any card for your account. "
              f"Would you like to open a new account?")
        response = get_answer(
            validation_of_answer,
            "Enter Y or N: ",
            'Entered value is not correct. Enter Y or N: ')
        if response == 'Y':
            if CardService.add_card_type(engine, logged_in_user.id):
                CardService.update_service_after_adding_card(engine, logged_in_user.id)

    @staticmethod
    def add_card_type(engine, id_user_data: int) -> bool:
        """Check which card the user wants to add and whether the card can be added"""
        card_name = get_answer(
                validation_space_or_alpha_not_digit,
                'Enter the name of the card: ',
                'Entered data contains illegal characters. Try again: ')
        card_type = CardService.choose_card_type()
        if card_type == 'STANDARD':
            if CardRepo(engine, CardTable).join_cards(
                    UserDataTable,
                    card_type,
                    id_user_data):
                print(f"\n{' ' * 12}We cannot add a new card. You cannot have two standard cards on one account.")
                return False
            else:
                CardService.add(engine, id_user_data, card_type, card_name)
                return True
        elif card_type == 'SINGLE-USE VIRTUAL':
            if CardRepo(engine, CardTable).join_cards(
                    UserDataTable,
                    card_type,
                    id_user_data):
                print(f"\n{' ' * 12}We cannot add a new card. "
                      f"You cannot have two SINGLE-USE VIRTUAL cards on one account.")
                return False
            else:
                CardService.add(engine, id_user_data, card_type, card_name)
                return True
        else:
            if len(CardRepo(engine, CardTable).join_cards(
                    UserDataTable,
                    card_type,
                    id_user_data)) >= 10:
                print(f"\n{' ' * 12}We cannot add a new card. "
                      f"You cannot have more than 10 MULTI-USE VIRTUAL cards on one account.")
                return False
            else:
                CardService.add(engine, id_user_data, card_type, card_name)
                return True

    @staticmethod
    def add(engine, id_user_data: int, card_type: str, card_name: str):
        """Add cards with default limits"""
        CrudRepo(engine, CardTable).add(
            id_user_data=id_user_data,
            card_number=CardService.generate_card_number(engine),
            valid_thru=CardService.get_new_date(3),
            cvv=Decimal(0),
            blocked=False,
            daily_limit=Decimal(2000),
            internet_limit=Decimal(1000),
            contactless_limit=Decimal(100),
            card_pin=CardService.generate_random_number(0, 4),
            sec_online_transactions=True,
            sec_location=True,
            sec_magnetic_strip=True,
            sec_withdrawals_atm=True,
            sec_contactless=True,
            card_name=card_name,
            card_type=card_type
        )
        print(f"\n{' ' * 12}Your card has been added.")

    @staticmethod
    def choose_card_type() -> str:
        """Select the type of card you want to get"""
        print("""
            Select the type of card you want to create: 
            1. STANDARD
            2. SINGLE-USE VIRTUAL
            3. MULTI-USE VIRTUAL
            """)
        chosen_operation = get_answer(
            validation_chosen_operation,
            'Enter chosen card type: ',
            'Entered data contains illegal characters. Try again: ',
            (1, 3))
        match chosen_operation:
            case '1':
                return 'STANDARD'
            case '2':
                return 'SINGLE-USE VIRTUAL'
            case '3':
                return 'MULTI-USE VIRTUAL'

    @staticmethod
    def update_service_after_adding_card(engine, id_user_data: int):
        """Update an existing row in the service table"""
        card_id = CrudRepo(engine, CardTable).get_last_row()[0]
        service_row = CrudRepo(engine, ServiceTable).find_first_with_condition((ServiceTable.id_user_data, id_user_data))
        CrudRepo(engine, ServiceTable).update_by_id(
            service_row[0],
            id_user_data=id_user_data,
            user_account_id=service_row[2],
            card_id=card_id)

    @staticmethod
    def switch_cards(engine, id_user_data: int):
        """Show all available cards and select the card for which you want to make the transaction"""
        cards = CardRepo(engine, CardTable).find_all_cards(id_user_data)
        cards_named_tuple = [card_named_tuple(account) for account in cards]
        for x in range(0, len(cards_named_tuple)):
            print(f"{' ' * 12}", x+1, ' ', cards_named_tuple[x].card_name, ' ', cards_named_tuple[x].card_type)
        chosen_operation = get_answer(
            validation_chosen_operation,
            'Enter chosen operation: ',
            'Entered data contains illegal characters. Try again: ',
            (1, len(cards_named_tuple)))
        chosen_account = cards_named_tuple[int(chosen_operation)-1].id
        service_row = CrudRepo(engine, ServiceTable).find_first_with_condition(
            (ServiceTable.id_user_data, id_user_data))
        CrudRepo(engine, ServiceTable).update_by_id(
            service_row[0],
            id_user_data=id_user_data,
            user_account_id=service_row[2],
            card_id=chosen_account)

    @staticmethod
    def check_service(engine, logged_in_user: namedtuple):
        """Check if there is a service in the database for the given account"""
        return CrudRepo(engine, ServiceTable).join_with_condition(
            UserDataTable,
            ServiceTable.card_id,
            (UserDataTable.login, logged_in_user.login))

    @staticmethod
    def generate_random_number(range_min: int, range_max: int) -> str:
        """Generate a random number that can be used to simulate some number"""
        return ''.join([str(randint(0, 9)) for _ in range(range_min, range_max)])

    @staticmethod
    def generate_card_number(engine) -> str:
        """Generate a card number and check if it is unique"""
        while True:
            account_number = ''.join([str(randint(0, 9)) for _ in range(16)])
            if not CrudRepo(engine, CardTable).find_all_with_condition((CardTable.card_number, account_number)):
                return account_number

    @staticmethod
    def get_new_date(years: int) -> date:
        """Create an expiration date for the card. Add the indicated number of years"""
        today_date = date.today()
        return date(today_date.year + years, today_date.month, 1)
