from database.repository.crud_repo import CrudRepo
from database.repository.card_repo import CardRepo
from database.model.tables import *
from management.conversions import used_card_named_tuple, card_named_tuple
from management.security.security import Security
from management.services.common import *
from datetime import date
from decimal import Decimal


class CardManagementService:
    def __init__(self, engine):
        self.engine = engine

        self.user_account_crud_repo = CrudRepo(self.engine, UserAccountTable)
        self.user_data_crud_repo = CrudRepo(self.engine, UserDataTable)
        self.card_crud_repo = CardRepo(self.engine, CardTable)
        self.service_crud_repo = CrudRepo(self.engine, ServiceTable)

    def user_without_card(self, logged_in_user: namedtuple):
        """Create an account for the new logged_in_user and then update the service"""
        print(f"{' ' * 12}You don't have any card for your account. "
              f"Would you like to open a new account?")
        response = get_answer(
            validation_of_answer,
            "Enter Y or N: ",
            'Entered value is not correct. Enter Y or N: ')
        if response == 'Y':
            if self.add_card_type(logged_in_user):
                self.update_service_after_adding_card(logged_in_user.id)

    def add_card_type(self, logged_in_user: namedtuple) -> bool:
        """Check which card the user wants to add and whether the card can be added"""
        card_name = get_answer(
            validation_space_or_alpha_not_digit,
            'Enter the name of the card: ',
            'Entered data contains illegal characters. Try again: ')
        chosen_currency = choose_currency('Choose the main currency for your card')
        accounts = self.user_account_crud_repo.find_all_with_condition(
            (logged_in_user.id, UserAccountTable.id_user_data))
        available_accounts = [item[3] for item in accounts]
        card_type = choose_card_type()
        if chosen_currency not in available_accounts:
            print(f"\n{' ' * 12}You cannot add a card for a currency other than your accounts.")
            return False
        if card_type == 'STANDARD':
            if self.card_crud_repo.join_cards(
                    UserDataTable,
                    card_type,
                    logged_in_user.id):
                print(f"\n{' ' * 12}We cannot add a new card. You cannot have two standard cards on one account.")
                return False
            else:
                self.add_card(logged_in_user.id, card_type, card_name, chosen_currency)
                return True
        elif card_type == 'SINGLE-USE VIRTUAL':
            if self.card_crud_repo.join_cards(
                    UserDataTable,
                    card_type,
                    logged_in_user.id):
                print(f"\n{' ' * 12}We cannot add a new card. "
                      f"You cannot have two SINGLE-USE VIRTUAL cards on one account.")
                return False
            else:
                self.add_card(logged_in_user.id, card_type, card_name, chosen_currency)
                return True
        else:
            if len(self.card_crud_repo.join_cards(
                    UserDataTable,
                    card_type,
                    logged_in_user.id)) >= 10:
                print(f"\n{' ' * 12}We cannot add a new card. "
                      f"You cannot have more than 10 MULTI-USE VIRTUAL cards on one account.")
                return False
            else:
                self.add_card(logged_in_user.id, card_type, card_name, chosen_currency)
                return True

    def update_service_after_adding_card(self, id_user_data: int):
        """Update an existing row in the service table"""
        card_id = self.card_crud_repo.get_last_row()[0]
        service_row = self.service_crud_repo.find_first_with_condition(
            (ServiceTable.id_user_data, id_user_data))
        self.service_crud_repo.update_by_id(
            service_row[0],
            id_user_data=id_user_data,
            user_account_id=service_row[2],
            card_id=card_id)

    def switch_cards(self, id_user_data: int):
        """Show all available cards and select the card for which you want to make the transaction"""
        cards = self.card_crud_repo.find_all_cards(id_user_data)
        cards_named_tuple = [used_card_named_tuple(card) for card in cards]
        for x, item in enumerate(cards_named_tuple):
            print(f"{' ' * 12}", x + 1, ' ', item.card_name, ' ', item.card_type)
        chosen_operation = get_answer(
            validation_chosen_operation,
            'Enter chosen operation: ',
            'Entered data contains illegal characters. Try again: ',
            (1, len(cards_named_tuple)))
        chosen_account = cards_named_tuple[int(chosen_operation) - 1].id
        service_row = self.service_crud_repo.find_first_with_condition(
            (ServiceTable.id_user_data, id_user_data))
        self.service_crud_repo.update_by_id(
            service_row[0],
            id_user_data=id_user_data,
            user_account_id=service_row[2],
            card_id=chosen_account)

    def check_service(self, logged_in_user: namedtuple):
        """Check if there is a service in the database for the given account"""
        return self.service_crud_repo.join_with_condition(
            UserDataTable,
            ServiceTable.card_id,
            (UserDataTable.login, logged_in_user.login))

    def block_card(self, used_card: namedtuple):
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
                self.card_crud_repo.update_by_id(card.id, **card_dict)
                print(f"{' ' * 12}Your card has been {word_2}.")
        card = card_named_tuple(self.card_crud_repo.find_by_id(used_card.id))
        if used_card.card_type != "SINGLE-USE VIRTUAL":
            if not card.blocked:
                block_or_unlock("block", True, "blocked")
            else:
                block_or_unlock("unlock", False, "unlocked")
        else:
            print(f"{' ' * 12}You cannot block SINGLE-USE VIRTUAL")

    def set_card_limit(self, used_card: namedtuple):
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
                    self.card_crud_repo.update_by_id(card.id, **card_dict)
                    print(f"{' ' * 12}Your limit has been updated.")
        if used_card.card_type == "STANDARD":
            chosen_type = choose_limit_card(used_card, 0, 3)
        else:
            chosen_type = choose_limit_card(used_card, 100, 1)
        card = card_named_tuple(self.card_crud_repo.find_by_id(used_card.id))
        if chosen_type == "Daily limit":
            set_limit("daily_limit", card.daily_limit)
        elif chosen_type == "Internet limit":
            set_limit("internet_limit", card.internet_limit)
        else:
            set_limit("contactless_limit", card.contactless_limit)

    def card_security(self, used_card: namedtuple):
        """Change the security settings for the card"""
        def set_limit(sec_type: str, security: bool):
            if security:
                print(f"{' ' * 12}Currently, these transactions are not blocked.")
                print(f"{' ' * 12}Do you want to block it?")
            else:
                print(f"{' ' * 12}Currently, these transactions are blocked.")
                print(f"{' ' * 12}Do you want to unblock it?")
            response = get_answer(
                validation_of_answer,
                "Enter Y or N: ",
                'Entered value is not correct. Enter Y or N: ')
            if response == "Y":
                if security:
                    new_sec = False
                else:
                    new_sec = True
                card_dict = card._asdict()
                card_dict[sec_type] = new_sec
                self.card_crud_repo.update_by_id(card.id, **card_dict)
                print(f"{' ' * 12}Security settings for your account have been changed.")
        if used_card.card_type == "STANDARD":
            chosen_type = choose_security(used_card, 0, 5)
        else:
            chosen_type = choose_security(used_card, 100, 2)
        card = card_named_tuple(self.card_crud_repo.find_by_id(used_card.id))
        if chosen_type == "Online transactions":
            set_limit("sec_online_transactions", card.sec_online_transactions)
        elif chosen_type == "Location":
            set_limit("sec_location", card.sec_location)
        elif chosen_type == "Contactless transactions":
            set_limit("sec_contactless", card.sec_contactless)
        elif chosen_type == "Magnetic stripe transactions":
            set_limit("sec_magnetic_strip", card.sec_magnetic_strip)
        elif chosen_type == "ATM transactions":
            set_limit("sec_withdrawals_atm", card.sec_withdrawals_atm)

    def show_pin(self, used_card: namedtuple, logged_in_user: namedtuple):
        """Show PIN for a standard card"""
        if used_card.card_type == "STANDARD":
            login = input('Enter your login: ')
            if login == logged_in_user.login:
                password = input('Enter your password: ')
                logged_in_user = self.user_data_crud_repo.find_first_with_condition((UserDataTable.login, login))
                if logged_in_user and Security.check_password(password, logged_in_user.password):
                    card = card_named_tuple(self.card_crud_repo.find_by_id(used_card.id))
                    print(f"\n{' ' * 12}The pin for your card is: {card.card_pin}")
                else:
                    print(f"\n{' ' * 12}The entered data is incorrect.")
            else:
                print(f"\n{' ' * 12}The entered login differs from the login of the logged in user.")
        else:
            print(f"\n{' ' * 12}The pin is not required for internet cards.")

    def delete_card(self, used_card: namedtuple, logged_in_user: namedtuple):
        """Remove card from the database. Show another card in the service or
        if you do not have any card, block access to card options by setting card_id to None."""
        self.card_crud_repo.delete_by_id(used_card.id)
        cards = self.card_crud_repo.find_all_cards(logged_in_user.id)
        if cards:
            card = [used_card_named_tuple(account) for account in cards][0]
            service_row = self.service_crud_repo.find_first_with_condition(
                (ServiceTable.id_user_data, logged_in_user.id))
            self.service_crud_repo.update_by_id(
                service_row[0],
                id_user_data=logged_in_user.id,
                user_account_id=service_row[2],
                card_id=card.id)
        else:
            service_row = self.service_crud_repo.find_first_with_condition(
                (ServiceTable.id_user_data, logged_in_user.id))
            self.service_crud_repo.update_by_id(
                service_row[0],
                id_user_data=logged_in_user.id,
                user_account_id=service_row[2],
                card_id=None)

    def card_expired(self, used_card: namedtuple, logged_in_user: namedtuple):
        """Check if the card is not expired. If so, delete it and display the message"""
        if used_card:
            if used_card.valid_thru < date.today():
                self.delete_card(used_card, logged_in_user)
                print(f"\n{' ' * 12}The following card has been removed due to expiration. Please add a new card.")
                print(f"{' ' * 12}Card name: {used_card.card_name} Card type: {used_card.card_type}")

    def add_card(self, id_user_data: int, card_type: str, card_name: str, main_currency: str):
        """Add default card settings based on its type"""
        self.card_crud_repo.add(
            id_user_data=id_user_data,
            card_number=self.generate_card_number(),
            valid_thru=get_date_with_first_day_of_month(3),
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
            main_currency=main_currency
        )
        print(f"\n{' ' * 12}Your card has been added.")

    def generate_card_number(self) -> str:
        """Generate a card number and check if it is unique"""
        while True:
            account_number = ''.join([str(randint(0, 9)) for _ in range(16)])
            if not self.card_crud_repo.find_all_with_condition((CardTable.card_number, account_number)):
                return account_number
