from management.validation import *
from data_base.repository.crud_repo import CrudRepo
from data_base.repository.card_repo import CardRepo
from data_base.repository.user_account_repo import UserAccountRepo
from data_base.model.tables import *
from random import randint
from decimal import Decimal
from management.conversions import *
from management.services.currency_exchange_service import CurrencyExchange
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
                CardService.add_card(engine, id_user_data, card_type, card_name)
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
                CardService.add_card(engine, id_user_data, card_type, card_name)
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
                CardService.add_card(engine, id_user_data, card_type, card_name)
                return True

    @staticmethod
    def add_card(engine, id_user_data: int, card_type: str, card_name: str):
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
            card_type=card_type,
            main_currency=CardService.choose_currency('Choose the main currency for your card')
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
        cards_named_tuple = [card_named_tuple(account) for account in cards]
        for x in range(0, len(cards_named_tuple)):
            print(f"{' ' * 12}", x + 1, ' ', cards_named_tuple[x].card_name, ' ', cards_named_tuple[x].card_type)
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
    def pay_by_card(engine, used_card: namedtuple, logged_in_user: namedtuple):
        """Perform card payments taking into account all currency conversions and the correct calculation of the
        account balance after the operation.
        Perform card payments taking into account all currency conversions and the correct
        calculation of the account balance after the operation."""
        def update_account():
            CrudRepo(engine, UserAccountTable).update_by_id(
                used_account.id,
                account_number=used_account.account_number,
                currency=used_account.currency,
                balance=used_account.balance - (amount_exched if amount_exched else entered_amount))

        def add_card_transaction(commission: int, balance: Decimal, payout: str, payment: str,
                                 rate_to_main_currency: int, transaction_type: str):
            CrudRepo(engine, CardTransactionTable).add(
                id_user_account=used_account.id,
                id_card=used_card.id,
                transaction_time=datetime.now(),
                amount=(amount_exched if amount_exched else entered_amount),
                commission=commission,
                balance=balance,
                payer_name=get_answer(
                    validation_alpha,
                    'Enter the payer name: ',
                    'Entered data contains illegal characters. Try again: '),
                payout=payout,
                payment=payment,
                rate_to_main_currency=Decimal(rate_to_main_currency),
                transaction_type=transaction_type,
                rate=rate
            )
            print(f"\n{' ' * 12}The transaction was successful.")

        card = card_all_named_tuple(CrudRepo(engine, CardTable).find_by_id(used_card.id))
        if not card.blocked:
            type_of_payment = CardService.choose_payment_type()
            if CardService.check_security(type_of_payment, card):
                entered_amount = Decimal(get_answer(
                    validation_decimal,
                    'Enter the amount: ',
                    'Entered data contains illegal characters. Try again: '))
                currency = CardService.choose_currency('Choose the currency you want to pay in: ')
                accounts = CrudRepo(engine, UserAccountTable).find_all_with_condition(
                    (UserAccountTable.id_user_data, logged_in_user.id))
                used_account, amount_exched, rate = CardService.find_the_best_account_for_transaction(
                    accounts, currency, entered_amount)
                if not used_account:
                    return False
                if card.main_currency != currency:
                    exchanged_amount_for_limit_checking = CurrencyExchange().get_result(
                        currency, card.main_currency, str(entered_amount))
                else:
                    exchanged_amount_for_limit_checking = {"result": entered_amount, "info": {"rate": 1}}
                if CardService.check_daily_limit(engine, used_account, card, exchanged_amount_for_limit_checking):
                    if type_of_payment == "Contactless payment":
                        if exchanged_amount_for_limit_checking["result"] < card.contactless_limit:
                            add_card_transaction(
                                0, used_account.balance - (amount_exched if amount_exched else entered_amount),
                                "YES", "NO", exchanged_amount_for_limit_checking["info"]["rate"],
                                "Contactless payment")
                            update_account()
                        else:
                            print(f"\n{' ' * 12}Your contactless transaction limit does not allow you to "
                                  f"complete the transaction. Change your limit..")
                    elif type_of_payment == "Internet payment":
                        if exchanged_amount_for_limit_checking["result"] < card.internet_limit:
                            add_card_transaction(
                                0, used_account.balance - (amount_exched if amount_exched else entered_amount),
                                "YES", "NO", exchanged_amount_for_limit_checking["info"]["rate"],
                                "Internet payment")
                            update_account()
                        else:
                            print(f"\n{' ' * 12}Your internet transaction limits do not allow you to "
                                  f"complete the transaction. Change your limit.")
                    else:
                        add_card_transaction(
                            0, used_account.balance - (amount_exched if amount_exched else entered_amount),
                            "YES", "NO", exchanged_amount_for_limit_checking["info"]["rate"],
                            "Magnetic stripe payment")
                        update_account()
                else:
                    print(
                        f"\n{' ' * 12}We are unable to complete your transaction because the daily limit has "
                        f"been exceeded. Change your daily limit to be able to make transactions..")

    @staticmethod
    def find_the_best_account_for_transaction(
            accounts_named_tuple: namedtuple, currency: str, entered_amount: Decimal) -> tuple:
        """If it is possible, use an account with the same currency in which you want to make transactions.
        If you do not have such an account, or you have insufficient funds on this account,
        use another account that has the appropriate funds.
        If no account is found that meets these requirements, return None"""
        accounts_named_tuple = [user_account_named_tuple(item) for item in accounts_named_tuple]
        account_number = [x for x in accounts_named_tuple if x.currency == currency and x.balance > entered_amount]
        account_number = accounts_named_tuple.index(account_number[0]) if account_number else None
        account_with_main_currency = accounts_named_tuple[account_number] if account_number != None else None
        used_account = None
        amount_exched = None
        rate_exched = 1
        if account_number:
            del accounts_named_tuple[account_number]
        if account_with_main_currency:
            used_account = account_with_main_currency
        elif accounts_named_tuple:
            for x in accounts_named_tuple:
                response = CurrencyExchange().get_result(currency, x.currency, str(entered_amount))
                amount_exched = Decimal(response["result"])
                rate_exched = Decimal(response['info']['rate'])
                if amount_exched < x.balance:
                    used_account = x
                    break
            else:
                print(f"\n{' ' * 12}You do not have sufficient funds in your account. "
                      f"Deposit money into your account.")
        else:
            print(f"\n{' ' * 12}You do not have sufficient funds in your account. "
                  f"Deposit money into your account.")
        return used_account, amount_exched, rate_exched

    @staticmethod
    def check_daily_limit(engine, used_account: namedtuple, card: namedtuple, exchanged_amount: dict) -> bool:
        """Check if the limit of daily transactions for a given card has not been exceeded"""
        today_date = date.today()
        transactions_one_day = UserAccountRepo(engine, CardTransactionTable).find_btwn_dates(
            (
                CardTransactionTable.transaction_time,
                today_date,
                date(today_date.year, today_date.month, today_date.day + 1),
                CardTransactionTable.id_user_account,
                used_account.id
            )
        )
        transactions_one_day = [card_transactions_named_tuple(x) for x in transactions_one_day]
        sum_transactions_one_day = 0
        for x in transactions_one_day:
            sum_transactions_one_day = x.amount * x.rate_to_main_currency
        if sum_transactions_one_day + Decimal(exchanged_amount["result"]) >= card.daily_limit:
            return False
        else:
            return True

    @staticmethod
    def check_security(type_of_payment: str, card: namedtuple) -> bool:
        """Check if the card has a blocked transaction you want to make"""
        if type_of_payment == 'Contactless payment':
            if card.sec_contactless:
                return True
            else:
                print(f"\n{' ' * 12}You cannot pay with your card because contactless transactions have been blocked.")
                return False
        elif type_of_payment == 'Magnetic stripe payment':
            if card.sec_magnetic_strip:
                return True
            else:
                print(f"\n{' ' * 12}You cannot pay with your card because magnetic stripe payments have been blocked.")
                return False
        else:
            if card.sec_online_transactions:
                return True
            else:
                print(f"\n{' ' * 12}You cannot pay with your card because online payments have been blocked.")
                return False

    @staticmethod
    def choose_payment_type() -> str:
        """Select the type of card you want to get"""
        print("""
            Choose the type of payment: 
            1. Contactless payment
            2. Magnetic stripe payment
            3. Internet payment
            """)
        chosen_operation = get_answer(
            validation_chosen_operation,
            'Enter chosen card type: ',
            'Entered data contains illegal characters. Try again: ',
            (1, 3))
        match chosen_operation:
            case '1':
                return 'Contactless payment'
            case '2':
                return 'Magnetic stripe payment'
            case '3':
                return 'Internet payment'

    @staticmethod
    def choose_currency(text: str) -> str:
        """Select the currency for which you want to perform the operation"""
        print(f"""
            {text}: 
            1. GBP
            2. USD
            3. CHF
            4. EUR
            """)
        chosen_operation = get_answer(
            validation_chosen_operation,
            'Enter chosen operation: ',
            'Entered data contains illegal characters. Try again: ',
            (1, 4))
        match chosen_operation:
            case '1':
                return 'GBP'
            case '2':
                return 'USD'
            case '3':
                return 'CHF'
            case '4':
                return 'EUR'

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
