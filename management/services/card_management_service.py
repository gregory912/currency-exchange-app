from database.repository.crud_repo import CrudRepo
from database.repository.card_repo import CardRepo
from database.model.tables import *
from management.conversions import used_card_named_tuple, card_named_tuple
from management.services.answers import *
from management.services.common import *
from decimal import Decimal


class CardManagementService:
    def __init__(self, engine):
        self.engine = engine

        self.user_account_crud_repo = CrudRepo(self.engine, UserAccountTable)
        self.user_data_crud_repo = CrudRepo(self.engine, UserDataTable)
        self.card_crud_repo = CardRepo(self.engine, CardTable)
        self.service_crud_repo = CrudRepo(self.engine, ServiceTable)

    def _get_service(self, id_user_data: int):
        """Get the user's service information from the database"""
        return self.service_crud_repo.find_first_with_condition((ServiceTable.id_user_data, id_user_data))

    def _update_service(self, service_row, id_user_data: int, value: int | None):
        """Update the user service in the database"""
        return self.service_crud_repo.update_by_id(
            service_row[0],
            id_user_data=id_user_data,
            user_account_id=service_row[2],
            card_id=value)

    def _get_all_cards(self, id_user_data: int):
        """Get all user cards"""
        return self.card_crud_repo.find_all_cards(id_user_data)

    def _get_card_details(self, used_card: namedtuple) -> namedtuple:
        """The function returns all card data"""
        return card_named_tuple(self.card_crud_repo.find_by_id(used_card.id))

    def _update_card(self, card_dict: dict, card: namedtuple):
        """Update the card"""
        return self.card_crud_repo.update_by_id(card.id, **card_dict)


class CardManagement(CardManagementService):
    def user_without_card(self, logged_in_user: namedtuple):
        """Create an account for the new logged_in_user and then update the service"""

        if GetReplyCard().get_value() == 'Y':
            if AddCard(self.engine).add_card_type(logged_in_user):
                self.update_service_after_adding_card(logged_in_user.id)

    def update_service_after_adding_card(self, id_user_data: int):
        """Update an existing row in the service table"""
        card_id = self._get_id_of_the_last_card_added()
        service_row = self._get_service(id_user_data)

        self._update_service(service_row, id_user_data, card_id)

    def _get_id_of_the_last_card_added(self):
        """Get the id of the last card added"""
        return self.card_crud_repo.get_last_row()[0]

    def switch_cards(self, id_user_data: int):
        """Show all available cards and select the card for which you want to make the t"""
        cards = self._get_all_cards(id_user_data)
        cards_named_tuple = self._get_cards_as_named_tuple(cards)

        self._print_all_available_cards(cards_named_tuple)

        chosen_operation = GetReplyWithValueChosenAcc().get_value(cards_named_tuple)

        chosen_account = self._get_id_of_chosen_card(cards_named_tuple, chosen_operation)
        service_row = self._get_service(id_user_data)

        self._update_service(service_row, id_user_data, chosen_account)

    def check_service(self, logged_in_user: namedtuple):
        """Check if there is a service in the database for the given account"""
        return self.service_crud_repo.join_with_condition(
            UserDataTable,
            ServiceTable.card_id,
            (UserDataTable.login, logged_in_user.login))

    def card_expired(self, used_card: namedtuple, logged_in_user: namedtuple):
        """Check if the card is not expired. If so, delete it and display the message"""
        if used_card:
            if used_card.valid_thru < date.today():
                DeleteCard(self.engine).delete_card(used_card, logged_in_user)
                print(f"\n{' ' * 12}The following card has been removed due to expiration. Please add a new card.")
                print(f"{' ' * 12}Card name: {used_card.card_name} Card type: {used_card.card_type}")

    @staticmethod
    def _print_all_available_cards(cards: namedtuple):
        """Print all available user cards"""
        for x, item in enumerate(cards):
            print(f"{' ' * 12}", x + 1, ' ', item.card_name, ' ', item.card_type)

    @staticmethod
    def _get_cards_as_named_tuple(cards: list) -> list[namedtuple]:
        """Get a single card as Namedtuple"""
        return [used_card_named_tuple(card) for card in cards]

    @staticmethod
    def _get_id_of_chosen_card(cards: namedtuple, chosen_operation: str) -> int:
        """Return the id of the selected card"""
        return cards[int(chosen_operation) - 1].id


class DeleteCard(CardManagementService):
    def delete_card(self, used_card: namedtuple, logged_in_user: namedtuple):
        """Remove card from the database. Show another card in the service or
        if you do not have any card, block access to card options by setting card_id to None."""
        self._delete_card_from_db(used_card)

        cards = self._get_all_cards(logged_in_user.id)

        service_row = self._get_service(logged_in_user.id)

        if cards:
            card = self._get_single_card(cards)
            self._update_service(service_row, logged_in_user.id, card.id)
        else:
            self._update_service(service_row, logged_in_user.id, None)

    def _delete_card_from_db(self, used_card: namedtuple):
        """Remove the indicated card from the database"""
        return self.card_crud_repo.delete_by_id(used_card.id)

    @staticmethod
    def _get_single_card(cards):
        """Get a single card as Namedtuple"""
        return [used_card_named_tuple(card) for card in cards][0]


class AddCard(CardManagementService):
    def add_card_type(self, logged_in_user: namedtuple) -> bool:
        """Check which card the user wants to add and whether the card can be added"""
        card_name = GetReplyCardName().get_value()
        chosen_currency = choose_currency('Choose the main currency for your card')
        accounts = self._find_all_accounts(logged_in_user)
        available_account_currencies = self._get_currencies_from_available_accounts(accounts)
        card_type = choose_card_type()

        if self._card_can_be_added(chosen_currency, available_account_currencies, card_type, logged_in_user):
            self._add_card(logged_in_user.id, card_type, card_name, chosen_currency)
            print(f"\n{' ' * 12}Your card has been added.")
            return True

    def _card_can_be_added(self, chosen_currency: str, available_account_currencies: list,
                           card_type: str, logged_in_user: namedtuple) -> bool:
        """Check if the card can be added.
        The user must have an account for the given currency card.
        Check if the limit of the number of cards is met."""
        if not self._has_account_for_selected_currency(chosen_currency, available_account_currencies):
            return False

        if card_type == 'STANDARD':
            if self._get_all_user_cards(card_type, logged_in_user):
                print(f"\n{' ' * 12}We cannot add a new card. You cannot have two standard cards on one account.")
                return False
        elif card_type == 'SINGLE-USE VIRTUAL':
            if self._get_all_user_cards(card_type, logged_in_user):
                print(f"\n{' ' * 12}We cannot add a new card. "
                      f"You cannot have two SINGLE-USE VIRTUAL cards on one account.")
                return False
        else:
            if len(self._get_all_user_cards(card_type, logged_in_user)) >= 10:
                print(f"\n{' ' * 12}We cannot add a new card. "
                      f"You cannot have more than 10 MULTI-USE VIRTUAL cards on one account.")
                return False
        return True

    def _get_all_user_cards(self, card_type: str, logged_in_user: namedtuple) -> list:
        """Get all user cards"""
        return self.card_crud_repo.join_cards(UserDataTable, card_type, logged_in_user.id)

    def _find_all_accounts(self, logged_in_user: namedtuple) -> list[tuple]:
        """Find all user accounts"""
        return self.user_account_crud_repo.find_all_with_condition((logged_in_user.id, UserAccountTable.id_user_data))

    def _generate_card_number(self) -> str:
        """Generate a card number and check if it is unique"""
        while True:
            account_number = generate_random_number(16)
            if not self.card_crud_repo.find_all_with_condition((CardTable.card_number, account_number)):
                return account_number

    def _add_card(self, id_user_data: int, card_type: str, card_name: str, main_currency: str):
        """Add default card settings based on its type"""
        return self.card_crud_repo.add(
            id_user_data=id_user_data,
            card_number=self._generate_card_number(),
            valid_thru=get_date_with_first_day_of_month(3),
            cvv=generate_random_number(3),
            blocked=False if card_type != "SINGLE-USE VIRTUAL" else None,
            daily_limit=Decimal('2000'),
            internet_limit=Decimal('1000') if card_type == "STANDARD" else None,
            contactless_limit=Decimal('100') if card_type == "STANDARD" else None,
            card_pin=generate_random_number(4) if card_type == "STANDARD" else None,
            sec_online_transactions=True,
            sec_location=True,
            sec_magnetic_strip=True if card_type == "STANDARD" else None,
            sec_withdrawals_atm=True if card_type == "STANDARD" else None,
            sec_contactless=True if card_type == "STANDARD" else None,
            card_name=card_name,
            card_type=card_type,
            main_currency=main_currency
        )

    @staticmethod
    def _has_account_for_selected_currency(chosen_currency: str, available_acc_currencies: list) -> bool:
        """Check you have an account for the selected currency"""
        if chosen_currency not in available_acc_currencies:
            print(f"\n{' ' * 12}You cannot add a card for a currency other than your accounts.")
            return False
        return True

    @staticmethod
    def _get_currencies_from_available_accounts(accounts: list) -> list:
        """Get currencies from all available user accounts"""
        return [account[3] for account in accounts]


class BlockCard(CardManagementService):
    def __init__(self, engine):
        super().__init__(engine)

        self.card = None

    def block_card(self, used_card: namedtuple):
        """Lock or unlock a given card"""
        self.card = card_named_tuple(self.card_crud_repo.find_by_id(used_card.id))

        if self._card_not_single_use_virtual:
            if not self.card.blocked:
                self._block()
            else:
                self._unlock()

    def _block(self):
        """Block the card"""
        print(f"{' ' * 12}Would you like to block your card?")
        if GetReplyAnswer().get_value() == "Y":
            card_dict = self._update_security(True)
            self._update_card(card_dict, self.card)

            print(f"{' ' * 12}Your card has been blocked.")

    def _unlock(self):
        """Unlock the card"""
        print(f"{' ' * 12}Would you like to unlock your card?")
        if GetReplyAnswer().get_value() == "Y":
            card_dict = self._update_security(False)
            self._update_card(card_dict, self.card)

            print(f"{' ' * 12}Your card has been unlocked.")

    def _update_security(self, value: bool) -> dict:
        """Update the security on the card"""
        card_dict = self.card._asdict()
        card_dict["blocked"] = value
        return card_dict

    @staticmethod
    def _card_not_single_use_virtual(used_card: namedtuple) -> bool:
        """Check that the card is not SINGLE-USE VIRTUAL"""
        if used_card.card_type != "SINGLE-USE VIRTUAL":
            print(f"{' ' * 12}You cannot block SINGLE-USE VIRTUAL")
            return False
        return True


class ShowCardPin(CardManagementService):
    def show_pin(self, used_card: namedtuple, logged_in_user: namedtuple):
        """Show PIN for a standard card"""
        if self._card_has_standard_type(used_card):
            login = input('Enter your login: ')

            if self._entered_login_is_the_same_as_user_login(login, logged_in_user):
                password = input('Enter your password: ')
                logged_in_user = self._get_user_data(login)

                if logged_in_user and self._check_security(password, logged_in_user):
                    card = self._get_card_details(used_card)
                    print(f"\n{' ' * 12}The pin for your card is: {card.card_pin}")
                else:
                    print(f"\n{' ' * 12}The entered data is incorrect.")

    def _get_user_data(self, login: str):
        """Get user data"""
        return self.user_data_crud_repo.find_first_with_condition((UserDataTable.login, login))

    @staticmethod
    def _check_security(password: str, logged_in_user: namedtuple) -> bool:
        """Check that the password you entered is correct"""
        return Security.check_password(password, logged_in_user.password)

    @staticmethod
    def _card_has_standard_type(used_card: namedtuple) -> bool:
        """Check that the card is of the standard type"""
        if used_card.card_type == "STANDARD":
            return True
        print(f"\n{' ' * 12}The pin is not required for internet cards.")
        return False

    @staticmethod
    def _entered_login_is_the_same_as_user_login(login: str, logged_in_user: namedtuple) -> bool:
        """Check that the login you entered is the same as the login of the user who is logged in"""
        if login == logged_in_user.login:
            return True
        print(f"\n{' ' * 12}The entered login differs from the login of the logged in user.")
        return False


class CardSecurity(CardManagementService):
    def __init__(self, engine):
        super().__init__(engine)

        self.card = None

    def card_security(self, used_card: namedtuple):
        """Change the security settings for the card"""

        self.card = self._get_card_details(used_card)

        if used_card.card_type == "STANDARD":
            chosen_type = self._choose_security_standard()
        else:
            chosen_type = self._choose_security_other()

        self._choose_security_type(chosen_type)

    def _choose_security_type(self, chosen_type: str):
        """Security selection to be updated"""
        match chosen_type:
            case "Online transactions":
                self._set_security("sec_online_transactions", self.card.sec_online_transactions)
            case "Location":
                self._set_security("sec_location", self.card.sec_location)
            case "Contactless transactions":
                self._set_security("sec_contactless", self.card.sec_contactless)
            case "Magnetic stripe transactions":
                self._set_security("sec_magnetic_strip", self.card.sec_magnetic_strip)
            case "ATM transactions":
                self._set_security("sec_withdrawals_atm", self.card.sec_withdrawals_atm)

    def _set_security(self, sec_type: str, security: bool):
        """Ask the user for security updates. Change security if required"""
        if security:
            print(f"{' ' * 12}Currently, these transactions are not blocked.")
            print(f"{' ' * 12}Do you want to block it?")
        else:
            print(f"{' ' * 12}Currently, these transactions are blocked.")
            print(f"{' ' * 12}Do you want to unlock it?")

        if GetReplyAnswer().get_value() == "Y":
            new_sec = False if security else True

            card_dict = self._update_limit(sec_type, new_sec)
            self._update_card(card_dict, self.card)

            print(f"{' ' * 12}Security settings for your account have been changed.")

    def _update_limit(self, sec_type: str, new_sec: bool) -> dict:
        """Update the security on the card"""
        card_dict = self.card._asdict()
        card_dict[sec_type] = new_sec
        return card_dict

    @staticmethod
    def _choose_security_standard() -> str:
        """Select the currency for which you want to perform the operation for standard card"""
        print("""
            Select the security you want to change: 
            1. Online transactions
            2. Location
            3. Contactless transactions
            4. Magnetic stripe transactions
            5. ATM transactions
            """)
        chosen_operation = GetReplyWithValueChosenCur().get_value(5)
        match chosen_operation:
            case '1':
                return 'Online transactions'
            case '2':
                return 'Location'
            case '3':
                return 'Contactless transactions'
            case '4':
                return 'Magnetic stripe transactions'
            case '5':
                return 'ATM transactions'

    @staticmethod
    def _choose_security_other() -> str:
        """Select the currency for which you want to perform the operation for other cards"""
        print("""
            Select the security you want to change: 
            1. Online transactions
            2. Location
            """)
        chosen_operation = GetReplyWithValueChosenCur().get_value(2)
        match chosen_operation:
            case '1':
                return 'Online transactions'
            case '2':
                return 'Location'


class CardLimit(CardManagementService):
    def __init__(self, engine):
        super().__init__(engine)

        self.card = None

    def set_card_limit(self, used_card: namedtuple):
        """Set limits for the chosen card"""

        self.card = card_named_tuple(self.card_crud_repo.find_by_id(used_card.id))

        if used_card.card_type == "STANDARD":
            chosen_type = self._choose_limit_card_standard()
        else:
            chosen_type = self._choose_limit_card_other()

        self._choose_limit_type(chosen_type)

    def _choose_limit_type(self, chosen_type: str):
        """Security selection to be updated"""
        match chosen_type:
            case "Daily limit":
                self.set_limit("daily_limit", self.card.daily_limit)
            case "Internet limit":
                self.set_limit("internet_limit", self.card.internet_limit)
            case "Contactless limit":
                self.set_limit("contactless_limit", self.card.contactless_limit)

    def set_limit(self, limit_type: str, limit: Decimal):
        """Set a limit for your card"""
        print(f"{' ' * 12}Your current limit is: {limit}")
        print(f"{' ' * 12}Would you like to change your limit?")

        if GetReplyAnswer().get_value() == "Y":
            new_limit = Decimal(GetReplyLimit().get_value())

            if self._entered_limit_too_small(new_limit):

                card_dict = self._update_limit(limit_type, new_limit)
                self._update_card(card_dict, self.card)

                print(f"{' ' * 12}Your limit has been updated.")

    def _update_limit(self, limit_type: str, new_limit: Decimal) -> dict:
        """Update the limit on the card"""
        card_dict = self.card._asdict()
        card_dict[limit_type] = new_limit
        return card_dict

    @staticmethod
    def _entered_limit_too_small(new_limit: Decimal) -> bool:
        """The entered limit is too low"""
        if new_limit < 10:
            print(f"{' ' * 12}The entered limit is too small.")
            return False
        return True

    @staticmethod
    def _choose_limit_card_standard() -> str:
        """Select the type of limit you want to perform"""
        print("""
                Select the type of card limit you want to change: 
                1. Daily limit
                2. Internet limit
                3. Contactless limit
                """)
        chosen_operation = GetReplyWithValueChosenLimit().get_value(3)
        match chosen_operation:
            case '1':
                return 'Daily limit'
            case '2':
                return 'Internet limit'
            case '3':
                return 'Contactless limit'

    @staticmethod
    def _choose_limit_card_other() -> str:
        """Select the type of limit you want to perform"""
        print("""
                Select the type of card limit you want to change: 
                1. Daily limit
                """)
        chosen_operation = GetReplyWithValueChosenLimit().get_value(1)
        match chosen_operation:
            case '1':
                return 'Daily limit'
