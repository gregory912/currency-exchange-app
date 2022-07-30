from data_base.repository.crud_repo import CrudRepo
from data_base.repository.card_repo import CardRepo
from data_base.model.tables import *
from management.conversions import used_card_named_tuple, card_named_tuple
from management.security.security import Security
from management.services.common import *
from datetime import date
from decimal import Decimal


class CardManagementService:
    @staticmethod
    def user_without_card(engine, logged_in_user: namedtuple):
        """Create an account for the new logged_in_user and then update the service"""
        print(f"{' ' * 12}You don't have any card for your account. "
              f"Would you like to open a new account?")
        response = get_answer(
            validation_of_answer,
            "Enter Y or N: ",
            'Entered value is not correct. Enter Y or N: ')
        if response == 'Y':
            if CardManagementService.add_card_type(engine, logged_in_user.id):
                CardManagementService.update_service_after_adding_card(engine, logged_in_user.id)

    @staticmethod
    def add_card_type(engine, id_user_data: int) -> bool:
        """Check which card the logged_in_user wants to add and whether the card can be added"""
        card_name = get_answer(
            validation_space_or_alpha_not_digit,
            'Enter the name of the card: ',
            'Entered data contains illegal characters. Try again: ')
        card_type = choose_card_type()
        if card_type == 'STANDARD':
            if CardRepo(engine, CardTable).join_cards(
                    UserDataTable,
                    card_type,
                    id_user_data):
                print(f"\n{' ' * 12}We cannot add a new card. You cannot have two standard cards on one account.")
                return False
            else:
                CardManagementService.add_card(engine, id_user_data, card_type, card_name)
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
                CardManagementService.add_card(engine, id_user_data, card_type, card_name)
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
                CardManagementService.add_card(engine, id_user_data, card_type, card_name)
                return True

    @staticmethod
    def update_service_after_adding_card(engine, id_user_data: int):
        """Update an existing row in the service table"""
        card_id = CrudRepo(engine, CardTable).get_last_row()[0]
        service_row = CrudRepo(engine, ServiceTable).find_first_with_condition(
            (ServiceTable.id_user_data, id_user_data))
        CrudRepo(engine, ServiceTable).update_by_id(
            service_row[0],
            id_user_data=id_user_data,
            user_account_id=service_row[2],
            card_id=card_id)

    @staticmethod
    def switch_cards(engine, id_user_data: int):
        """Show all available cards and select the card for which you want to make the transaction"""
        cards = CardRepo(engine, CardTable).find_all_cards(id_user_data)
        cards_named_tuple = [used_card_named_tuple(card) for card in cards]
        for x, item in enumerate(cards_named_tuple):
            print(f"{' ' * 12}", x + 1, ' ', item.card_name, ' ', item.card_type)
        chosen_operation = get_answer(
            validation_chosen_operation,
            'Enter chosen operation: ',
            'Entered data contains illegal characters. Try again: ',
            (1, len(cards_named_tuple)))
        chosen_account = cards_named_tuple[int(chosen_operation) - 1].id
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
    def block_card(engine, used_card: namedtuple):
        """Lock or unlock a given card"""
        def block_or_unlock(word_1: str, value: bool, word_2):
            print(f"{' ' * 12}Would you like to {word_1} your card?")
            response = get_answer(
                validation_of_answer,
                "Enter Y or N: ",
                'Entered value is not correct. Enter Y or N: ')
            if response == "Y":
                card_dict = card._asdict()
                card_dict["blocked"] = value
                CrudRepo(engine, CardTable).update_by_id(card.id, **card_dict)
                print(f"{' ' * 12}Your card has been {word_2}.")
        card = card_named_tuple(CrudRepo(engine, CardTable).find_by_id(used_card.id))
        if used_card.card_type != "SINGLE-USE VIRTUAL":
            if not card.blocked:
                block_or_unlock("block", True, "blocked")
            else:
                block_or_unlock("unlock", False, "unlocked")
        else:
            print(f"{' ' * 12}You cannot block SINGLE-USE VIRTUAL")

    @staticmethod
    def set_card_limit(engine, used_card: namedtuple):
        """Set limits for the chosen card"""
        def set_limit(limit_type: str, limit: Decimal):
            print(f"{' ' * 12}Your current limit is: {limit}")
            print(f"{' ' * 12}Would you like to change your limit?")
            response = get_answer(
                validation_of_answer,
                "Enter Y or N: ",
                'Entered value is not correct. Enter Y or N: ')
            if response == "Y":
                new_limit = get_answer(
                    validation_decimal,
                    'Enter the new limit: ',
                    'Entered data contains illegal characters. Try again: ')
                if Decimal(new_limit) < 10:
                    print(f"{' ' * 12}The entered limit is too small.")
                else:
                    card_dict = card._asdict()
                    card_dict[limit_type] = Decimal(new_limit)
                    CrudRepo(engine, CardTable).update_by_id(card.id, **card_dict)
                    print(f"{' ' * 12}Your limit has been updated.")
        if used_card.card_type == "STANDARD":
            chosen_type = choose_limit_card(used_card, 0, 3)
        else:
            chosen_type = choose_limit_card(used_card, 100, 1)
        card = card_named_tuple(CrudRepo(engine, CardTable).find_by_id(used_card.id))
        if chosen_type == "Daily limit":
            set_limit("daily_limit", card.daily_limit)
        elif chosen_type == "Internet limit":
            set_limit("internet_limit", card.internet_limit)
        else:
            set_limit("contactless_limit", card.contactless_limit)

    @staticmethod
    def show_pin(engine, used_card: namedtuple, logged_in_user: namedtuple):
        """Show PIN for a standard card"""
        if used_card.card_type == "STANDARD":
            login = input('Enter your login: ')
            if login == logged_in_user.login:
                password = input('Enter your password: ')
                logged_in_user = CrudRepo(engine, UserDataTable).find_first_with_condition((UserDataTable.login, login))
                if logged_in_user and Security.check_password(password, logged_in_user.password):
                    card = card_named_tuple(CrudRepo(engine, CardTable).find_by_id(used_card.id))
                    print(f"\n{' ' * 12}The pin for your card is: {card.card_pin}")
                else:
                    print(f"\n{' ' * 12}The entered data is incorrect.")
            else:
                print(f"\n{' ' * 12}The entered login differs from the login of the logged in user.")
        else:
            print(f"\n{' ' * 12}The pin is not required for internet cards.")

    @staticmethod
    def delete_card(engine, used_card: namedtuple, logged_in_user: namedtuple):
        """Remove card from the database. Show another card in the service or
        if you do not have any card, block access to card options by setting card_id to None."""
        CrudRepo(engine, CardTable).delete_by_id(used_card.id)
        cards = CardRepo(engine, CardTable).find_all_cards(logged_in_user.id)
        if cards:
            card = [used_card_named_tuple(account) for account in cards][0]
            service_row = CrudRepo(engine, ServiceTable).find_first_with_condition(
                (ServiceTable.id_user_data, logged_in_user.id))
            CrudRepo(engine, ServiceTable).update_by_id(
                service_row[0],
                id_user_data=logged_in_user.id,
                user_account_id=service_row[2],
                card_id=card.id)
        else:
            service_row = CrudRepo(engine, ServiceTable).find_first_with_condition(
                (ServiceTable.id_user_data, logged_in_user.id))
            CrudRepo(engine, ServiceTable).update_by_id(
                service_row[0],
                id_user_data=logged_in_user.id,
                user_account_id=service_row[2],
                card_id=None)

    @staticmethod
    def add_card(engine, id_user_data: int, card_type: str, card_name: str):
        """Add default card settings based on its type"""
        CrudRepo(engine, CardTable).add(
            id_user_data=id_user_data,
            card_number=CardManagementService.generate_card_number(engine),
            valid_thru=CardManagementService.get_date_with_first_day_of_month(3),
            cvv=generate_random_number(0, 3),
            blocked=False if card_type != "SINGLE-USE VIRTUAL" else None,
            daily_limit=Decimal(2000),
            internet_limit=Decimal(1000) if card_type == "STANDARD" else None,
            contactless_limit=Decimal(100) if card_type == "STANDARD" else None,
            card_pin=generate_random_number(0, 4) if card_type == "STANDARD" else None,
            sec_online_transactions=True,
            sec_location=True,
            sec_magnetic_strip=True if card_type == "STANDARD" else None,
            sec_withdrawals_atm=True if card_type == "STANDARD" else None,
            sec_contactless=True if card_type == "STANDARD" else None,
            card_name=card_name,
            card_type=card_type,
            main_currency=choose_currency('Choose the main currency for your card')
        )
        print(f"\n{' ' * 12}Your card has been added.")

    @staticmethod
    def generate_card_number(engine) -> str:
        """Generate a card number and check if it is unique"""
        while True:
            account_number = ''.join([str(randint(0, 9)) for _ in range(16)])
            if not CrudRepo(engine, CardTable).find_all_with_condition((CardTable.card_number, account_number)):
                return account_number

    @staticmethod
    def get_date_with_first_day_of_month(years: int) -> date:
        """Create an expiration date for the card. Add the indicated number of years"""
        today_date = date.today()
        return date(today_date.year + years, today_date.month, 1)
