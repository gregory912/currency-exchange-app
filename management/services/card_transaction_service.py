from database.repository.crud_repo import CrudRepo
from database.repository.user_account_repo import UserAccountRepo
from database.repository.card_repo import CardRepo
from database.model.tables import *
from management.services.currency_exchange_service import CurrencyExchange
from management.services.card_management_service import DeleteCard
from management.conversions import *
from management.services.answers import *
from decimal import Decimal
from management.services.common import *


class CardTransactionService:
    def __init__(self, engine):
        self.engine = engine

        self.user_account_crud_repo = CrudRepo(self.engine, UserAccountTable)
        self.user_data_crud_repo = CrudRepo(self.engine, UserDataTable)
        self.card_crud_repo = CardRepo(self.engine, CardTable)
        self.service_crud_repo = CrudRepo(self.engine, ServiceTable)

    def add_card_transaction(
            self, used_account: namedtuple, used_card: namedtuple, amount: Decimal,
            commission: int, balance: Decimal, payout: str, payment: str,
            rate_to_main_currency: int, transaction_type: str, rate: Decimal, payer_acc: str | None,
            amount_in_main_user_currency: Decimal):
        """Add payment by card to the database"""
        CrudRepo(self.engine, CardTransactionTable).add(
            id_user_account=used_account.id,
            id_card=used_card.id,
            transaction_time=datetime.now(),
            amount=amount,
            commission_in_main_user_currency=commission,
            balance=balance,
            payer_name=GetReplyPayerName().get_value(),
            payout=payout,
            payment=payment,
            rate_to_main_card_currency=Decimal(str(rate_to_main_currency)),
            transaction_type=transaction_type,
            rate_tu_used_account=rate,
            payer_account_number=payer_acc,
            amount_in_main_user_currency=amount_in_main_user_currency
        )
        print(f"\n{' ' * 12}The payment was successful.")

    def update_account(self, used_account: namedtuple, amount: Decimal):
        """Update the user account after the transaction is completed"""
        return self.user_account_crud_repo.update_by_id(
            used_account.id,
            account_number=used_account.account_number,
            currency=used_account.currency,
            balance=amount)

    def _get_all_card_details(self, used_card: namedtuple) -> namedtuple:
        """Get all your card information from the database"""
        return card_named_tuple(self.card_crud_repo.find_by_id(used_card.id))


class Security:
    def check_security(self, type_of_payment: str, card: namedtuple) -> bool:
        """Check if the card hasn't a blocked transaction you want to make"""
        if type_of_payment == 'Contactless payment':

            if self._card_is_standard_for_contactless_payment(card):
                if self._contactless_payment_not_blocked(card):
                    return True
                return False

        elif type_of_payment == 'Magnetic stripe payment':

            if self._card_is_standard_for_magnetic_payment(card):
                if self._magnetic_payment_not_blocked(card):
                    return True
                return False

        elif type_of_payment == 'Internet payment':

            if self._internet_payment_not_blocked(card):
                return True
            return False

        elif type_of_payment == 'Withdrawals ATM':

            if self._card_is_standard_for_atm_withdrawal(card):
                if self._atm_withdrawal_not_blocked(card):
                    return True
                return False

    @staticmethod
    def _card_is_standard_for_contactless_payment(card: namedtuple) -> bool:
        """Check that the card for contactless payment is standard"""
        if card.card_type == "STANDARD":
            return True
        print(f"\n{' ' * 12}You cannot pay with a virtual card contactless. Change card.")
        return False

    @staticmethod
    def _card_is_standard_for_magnetic_payment(card: namedtuple) -> bool:
        """Check that the card for magnetic stripe payment is standard"""
        if card.card_type == "STANDARD":
            return True
        print(f"\n{' ' * 12}You cannot pay with a virtual card by magnetic stripe. Change card.")
        return False

    @staticmethod
    def _card_is_standard_for_atm_withdrawal(card: namedtuple) -> bool:
        """Check that the card for ATM withdrawal is standard"""
        if card.card_type == "STANDARD":
            return True
        print(f"\n{' ' * 12}You cannot withdraw money from a virtual card. Change card.")
        return False

    @staticmethod
    def _contactless_payment_not_blocked(card: namedtuple) -> bool:
        """Check that the contactless payments for this card are not blocked"""
        if card.sec_contactless:
            return True
        print(f"\n{' ' * 12}You cannot pay with your card because contactless transactions have been blocked.")
        return False

    @staticmethod
    def _magnetic_payment_not_blocked(card: namedtuple) -> bool:
        """Check that the magnetic stripe payments for this card are not blocked"""
        if card.sec_magnetic_strip:
            return True
        print(f"\n{' ' * 12}You cannot pay with your card because magnetic stripe payments have been blocked.")
        return False

    @staticmethod
    def _internet_payment_not_blocked(card: namedtuple) -> bool:
        """Check that the internet payments for this card are not blocked"""
        if card.sec_online_transactions:
            return True
        print(f"\n{' ' * 12}You cannot pay with your card because online payments have been blocked.")
        return False

    @staticmethod
    def _atm_withdrawal_not_blocked(card: namedtuple) -> bool:
        """Check that the atm withdrawals for this card are not blocked"""
        if card.sec_withdrawals_atm:
            return True
        print(f"\n{' ' * 12}You cannot withdraw money from an ATM because your withdrawals are blocked.")
        return False


class CardDailyLimit(CardTransactionService):
    def check_daily_limit(self, used_account: namedtuple, card: namedtuple, exchanged_amount: dict) -> bool:
        """Check if the limit of daily transactions for a given card has not been exceeded"""
        transactions_one_day = self._get_all_transactions_for_one_day(used_account)
        transactions_one_day = self._get_all_transactions_as_namedtuple(transactions_one_day)

        sum_transactions_one_day = self._get_sum_of_all_transactions(transactions_one_day)

        if sum_transactions_one_day + Decimal(exchanged_amount["result"]) >= card.daily_limit:
            return False
        return True

    def _get_all_transactions_for_one_day(self, used_account: namedtuple):
        """Get all transactions from the current day"""
        return UserAccountRepo(self.engine, CardTransactionTable).find_btwn_dates(
            (
                CardTransactionTable.transaction_time,
                date.today(),
                date.today() + timedelta(days=1),
                CardTransactionTable.id_user_account,
                used_account.id
            )
        )

    def _get_sum_of_all_transactions(self, transactions_one_day: list[namedtuple]) -> Decimal:
        """Calculate the sum of all transactions in one day"""
        sum_transactions_one_day = Decimal('0')
        for transaction in transactions_one_day:
            sum_transactions_one_day += self._get_calculated_amount_for_payout(transaction)
        return sum_transactions_one_day

    @staticmethod
    def _get_all_transactions_as_namedtuple(transactions_one_day: list[tuple]) -> list[namedtuple]:
        """Get transaction as namedtuple"""
        return [card_transaction_named_tuple(x) for x in transactions_one_day]

    @staticmethod
    def _get_calculated_amount_for_payout(transaction: namedtuple) -> Decimal:
        """Check if the transaction is payout, if so,
        calculate the transaction amount to the main currency of the card"""
        if transaction.payout == "YES":
            return Decimal(str(round(transaction.amount * transaction.rate_to_main_card_currency, 2)))
        return Decimal('0')


class CardComission(CardTransactionService):
    def check_and_get_commission(self, logged_in_user, currency_for_transaction, entered_amount) -> tuple:
        """The entered amount in a given currency is converted to the main currency
        (if a currency other than the main currency of the account has been entered) for the account to check
        if any transactions should be collected. The transaction is charged in
        case of exceeding 200 (assumed for all 4 currencies) or exceeding 5 monthly transactions.
        The function returns the amount in the same currency as was entered,
        but after deducting the commission if it was required."""
        converted_amount = self._convert_entered_amount(logged_in_user, currency_for_transaction, entered_amount)

        amount, commission = self._get_amount_and_commision_for_monthly_transactions(converted_amount, logged_in_user)

        result = CurrencyExchange().get_result(logged_in_user.main_currency, currency_for_transaction, str(amount))

        return Decimal(result["result"]), amount, commission

    @staticmethod
    def _convert_entered_amount(logged_in_user, currency_for_transaction, entered_amount) -> Decimal:
        """Convert currency if it is different from user's main currency"""
        if logged_in_user.main_currency != currency_for_transaction:
            exchanged_data = CurrencyExchange().get_result(
                currency_for_transaction, logged_in_user.main_currency, str(entered_amount))
            return Decimal(exchanged_data["result"])
        return entered_amount

    def _get_amount_and_commision_for_monthly_transactions(self, amount: Decimal, logged_in_user) -> tuple:
        """Check if a commission is required.
        The amount and commission are stated in the user's primary currency."""
        all_exchanges = self.card_crud_repo.get_monthly_card_trans_for_user(
            logged_in_user.id, fst_day_of_this_month(), fst_day_of_next_month())

        transactions = self._get_all_transactions(all_exchanges)

        if self._amount_and_qty_of_transaction_appropriate(transactions, amount):
            return self._get_amount_with_comission(amount), self._get_comission(amount)
        return amount, 0

    def _get_amount_with_comission(self, amount: Decimal) -> Decimal:
        """Get the amount with added commission"""
        return amount + self._get_comission(amount)

    @staticmethod
    def _get_comission(amount: Decimal) -> Decimal:
        """Get commission on a given amount"""
        return amount * Decimal('0.02')

    @staticmethod
    def _amount_and_qty_of_transaction_appropriate(transactions: list, amount: Decimal) -> bool:
        """Check that the sum of monthly transactions or the number has not been exceeded"""
        return sum(transactions) + amount > 200 or len(transactions) > 5

    @staticmethod
    def _get_all_transactions(all_exchanges: list) -> list:
        """Return all transactions. In the case of None, return 0"""
        return [(item[0] if item[0] else 0) for item in all_exchanges]


class CardDepositMoney(CardTransactionService):
    def deposit_money(self, used_card: namedtuple, logged_in_user: namedtuple):
        """Deposit money by card. Make a deposit to the appropriate account, if necessary, convert the amount."""
        amount = Decimal(GetReplyAmount().get_value())

        currency = choose_currency('Choose the currency in which you want to deposit money: ')

        accounts = self._find_all_user_accounts(logged_in_user)
        accounts = self._get_accounts_as_namedtuple(accounts)

        payer_acc_number = GetReplyPayerAccNb().get_value()

        used_account = self._check_if_user_has_account_with_chosen_currency(accounts, currency)

        if used_account.currency != currency:
            amount, rate = self._exchange_currency_for_chosen_account(currency, used_account, amount)
        else:
            rate = 1

        self.add_card_transaction(
            used_account, used_card, amount, 0, used_account.balance + amount,
            "NO", "YES", 0, "Deposit money", rate, payer_acc_number, Decimal('0'))
        self.update_account(used_account, used_account.balance + amount)

    def _find_all_user_accounts(self, logged_in_user: namedtuple):
        """Find all user accounts"""
        return self.user_account_crud_repo.find_all_with_condition((UserAccountTable.id_user_data, logged_in_user.id))

    @staticmethod
    def _exchange_currency_for_chosen_account(currency: str, used_account: namedtuple, amount: Decimal) -> tuple:
        """If the user does not have an account in the currency in which the money is deposited,
        the money must be converted into the currency of the account that the user has"""
        response = CurrencyExchange().get_result(currency, used_account.currency, str(amount))
        amount = Decimal(response["result"])
        rate = Decimal(response['info']['rate'])
        return amount, rate

    @staticmethod
    def _get_accounts_as_namedtuple(accounts: list[tuple]) -> list[namedtuple]:
        """Convert tuple to namedtuple"""
        return [user_account_named_tuple(account) for account in accounts]

    @staticmethod
    def _check_if_user_has_account_with_chosen_currency(accounts: namedtuple, currency: str) -> namedtuple:
        """Check that the user has an account for the currency in which the money is being deposited.
        If yes, then use that account, if not then use the first account on the list"""
        for account in accounts:
            if account.currency == currency:
                return account
        return accounts[0]


class GetAccountForTransaction(CardComission):
    def __init__(self, engine, logged_in_user: namedtuple, card: namedtuple, entered_amount, currency):
        super().__init__(engine)
        self.accounts = None
        self.logged_in_user = logged_in_user
        self.card = card
        self.entered_amount = entered_amount
        self.currency = currency
        self.used_account = None
        self.amount_exched = None
        self.rate = Decimal('1')
        self.amt_for_limit_checking = None

    def find_the_best_account_for_transaction(self):
        """If it is possible, use an account with the same currency in which you want to make transactions.
        If you do not have such an account, or you have insufficient funds on this account,
        use another account that has the appropriate funds"""

        self.accounts = self._get_all_accounts_as_namedtuple(self._get_all_accounts())

        account_in_main_currency = self._get_account_with_same_currency_as_transaction()

        if account_in_main_currency:
            self.used_account = account_in_main_currency
        else:
            self.used_account = self._find_any_account()

        self.amt_for_limit_checking = self._get_amount_for_limit_checking()

        return self

    def _get_account_with_same_currency_as_transaction(self) -> tuple | None:
        """Find an account with the same currency as the t"""
        account = self._find_account_with_same_currency()
        return account[0] if account else None

    def _find_account_with_same_currency(self) -> list:
        """Find a user account in the same currency as the transaction currency"""
        return [i for i in self.accounts if i.currency == self.currency and i.balance > self.entered_amount]

    def _get_all_accounts(self):
        """Get all user accounts"""
        return self.user_account_crud_repo.find_all_with_condition((UserAccountTable.id_user_data, self.logged_in_user.id))

    def _find_any_account(self) -> namedtuple:
        """Find any account from which transactions can be made"""
        for item in self.accounts:
            response = CurrencyExchange().get_result(self.currency, item.currency, str(self.entered_amount))
            self.amount_exched = Decimal(response["result"])
            self.rate = Decimal(response['info']['rate'])
            if self.amount_exched < item.balance:
                return item
        else:
            print(f"\n{' ' * 12}You do not have sufficient funds in your account. Deposit money into your account.")

    def _get_amount_for_limit_checking(self) -> dict:
        """Get the amount to check your limits"""
        if self.card.main_currency != self.currency:
            return CurrencyExchange().get_result(self.currency, self.card.main_currency, str(self.entered_amount))
        return {"result": self.entered_amount, "info": {"rate": 1}}

    @staticmethod
    def _get_all_accounts_as_namedtuple(accounts: list[tuple]) -> list[namedtuple]:
        """Convert tuple namedtuple"""
        return [user_account_named_tuple(item) for item in accounts]


class WithdrawMoneyByCard(Security, CardDailyLimit, CardComission):
    def withdraw_money(self, used_card: namedtuple, logged_in_user: namedtuple):
        """Perform card payment operations. Check that the card is not blocked and that
        it has sufficient funds. If possible, select the account with the currency you want to select from the ATM."""
        card = self._get_all_card_details(used_card)

        if self._card_is_not_blocked(card):

            if self.check_security('Withdrawals ATM', card):

                entered_amount = Decimal(GetReplyAmount().get_value())
                currency = choose_currency('Choose the currency you want to pay in: ')
                entered_amount, amount, commission = self.check_and_get_commission(logged_in_user, currency, entered_amount)

                account_obj = GetAccountForTransaction(
                    self.engine, logged_in_user, card, entered_amount, currency).find_the_best_account_for_transaction()

                if not account_obj.used_account:
                    return False

                if self.check_daily_limit(account_obj.used_account, card, account_obj.amt_for_limit_checking):
                    if commission:
                        self._display_information_about_commission(used_card)

                    self.add_card_transaction(
                        account_obj.used_account, used_card,
                        self._get_exchanged_amount_if_exists(account_obj.amount_exched, account_obj.entered_amount),
                        commission,
                        account_obj.used_account.balance - self._get_exchanged_amount_if_exists(
                            account_obj.amount_exched, account_obj.entered_amount),
                        "YES", "NO", account_obj.amt_for_limit_checking["info"]["rate"],
                        "Withdrawals ATM", account_obj.rate, None, amount)

                    self.update_account(
                        account_obj.used_account,
                        self._get_balance_after_transaction(
                            account_obj.used_account, account_obj.amount_exched, entered_amount))

    @staticmethod
    def _get_balance_after_transaction(used_account, amount_exchanged, entred_amount):
        """Get the balance after completing the t"""
        return used_account.balance - amount_exchanged if amount_exchanged else used_account.balance - entred_amount

    @staticmethod
    def _get_exchanged_amount_if_exists(amount_exchanged, entred_amount):
        return amount_exchanged if amount_exchanged else entred_amount

    @staticmethod
    def _display_information_about_commission(used_card: namedtuple):
        """Display information about commision which has been taken"""
        print(f"\n{' ' * 12}You've exceeded the monthly exchange limit of 200 {used_card.main_currency}."
              f"A commission of 2% of the entered amount has been charged.")

    @staticmethod
    def _card_is_not_blocked(card: namedtuple) -> bool:
        """Check if the card from which the transaction is made is not blocked"""
        if card.blocked:
            print(f"\n{' ' * 12}Your card is blocked. We cannot complete your t.")
            return False
        return True


class PayByCard(Security, CardDailyLimit):
    def pay_by_card(self, used_card: namedtuple, logged_in_user: namedtuple):
        """Perform card payments taking into account all currency conversions and the correct calculation of the
        account balance after the operation."""
        card = self._get_all_card_details(used_card)

        if self._card_not_blocked(card):
            type_of_payment = choose_payment_type()
            if self.check_security(type_of_payment, card):

                amount = Decimal(GetReplyAmount().get_value())
                currency = choose_currency('Choose the currency you want to pay in: ')

                account_obj = GetAccountForTransaction(
                    self.engine, logged_in_user, card, amount, currency).find_the_best_account_for_transaction()

                if not account_obj.used_account:
                    return False

                if self.check_daily_limit(account_obj.used_account, card, account_obj.amt_for_limit_checking):
                    if type_of_payment == "Contactless payment":
                        self._perform_contactless_payment(account_obj, card, used_card, amount)

                    elif type_of_payment == "Internet payment":
                        self._perform_internet_paymant(account_obj, card, used_card, amount, logged_in_user)

                    elif type_of_payment == "Magnetic stripe payment":
                        self._perform_magnetic_stripe_payment(account_obj, used_card, amount)
                else:
                    print(
                        f"\n{' ' * 12}We are unable to complete your transaction because the daily limit has "
                        f"been exceeded. Change your daily limit to be able to make transactions.")

    @staticmethod
    def _card_not_blocked(card: namedtuple) -> bool:
        """Check that the card is not blocked.
        The SINGLE-USE VIRTUAL card cannot be blocked so the condition also applies to it"""
        if not card.blocked or card.card_type == "SINGLE-USE VIRTUAL":
            return True
        print(f"\n{' ' * 12}Your card is blocked. We cannot complete your t.")
        return False

    def _perform_magnetic_stripe_payment(self, account_obj, used_card, amount):
        """Make a magnetic stripe payment"""
        self._add_user_card_payment(account_obj, used_card, amount, "Magnetic stripe payment")

        self._update_user_account(account_obj)

    def _perform_contactless_payment(self, account_obj, card, used_card, amount):
        """Make a contactless payment"""
        if self._limit_of_contactless_payment_has_not_been_exceeded(account_obj, card):

            self._add_user_card_payment(account_obj, used_card, amount, "Contactless payment")

            self._update_user_account(account_obj)

    def _perform_internet_paymant(self, account_obj, card, used_card, amount, logged_in_user):
        """Make an internet payment"""
        if self._limit_of_internet_payment_has_not_been_exceeded(account_obj, card):

            self._add_user_card_payment(account_obj, used_card, amount, "Internet payment")

            self._update_user_account(account_obj)

            if card.card_type == "SINGLE-USE VIRTUAL":
                DeleteCard(self.engine).delete_card(used_card, logged_in_user)

    def _add_user_card_payment(self, account_obj, used_card, amount, card_type):
        """Add a payment card to the database"""
        return self.add_card_transaction(
            account_obj.used_account, used_card,
            self._get_amount_after_exchanging(account_obj),
            0, self._get_balance_after_payment(account_obj),
            "YES", "NO", account_obj.amt_for_limit_checking["info"]["rate"],
            card_type, account_obj.rate, None, amount)

    def _update_user_account(self, account_obj):
        """Update user account after payment"""
        return self.update_account(account_obj.used_account, (self._get_balance_after_payment(account_obj)))

    @staticmethod
    def _limit_of_internet_payment_has_not_been_exceeded(account_obj, card) -> bool:
        """Check that the limit for internet payments has not been exceeded.
        Online cards have no limits on internet transactions"""
        if card.card_type == "STANDARD" and account_obj.amt_for_limit_checking["result"] < card.internet_limit:
            return True
        elif card.card_type != "STANDARD":
            return True
        print(f"\n{' ' * 12}Your internet transactions limits do not allow you to "
              f"complete the transactions. Change your limit.")
        return False

    @staticmethod
    def _limit_of_contactless_payment_has_not_been_exceeded(account_obj, card) -> bool:
        """Check that the limit for contactless payments has not been exceeded"""
        if account_obj.amt_for_limit_checking["result"] < card.contactless_limit:
            return True
        print(f"\n{' ' * 12}Your contactless transaction limit does not allow you to complete the transation. "
              f"Change your limit..")
        return False

    @staticmethod
    def _get_amount_after_exchanging(account_obj):
        """Get the amount after checking whether you should use an account with
        a currency other than the currency in which the payment was made"""
        return account_obj.amount_exched if account_obj.amount_exched else account_obj.entered_amount

    def _get_balance_after_payment(self, account_obj):
        """Get the balance after completing the payment"""
        return account_obj.used_account.balance - self._get_amount_after_exchanging(account_obj)
