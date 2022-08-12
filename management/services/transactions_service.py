from management.conversions import *
from database.model.tables import CurrencyExchangeTable, CardTransactionTable, TransactionTable, UserAccountTable
from database.model.tables import CardTable
from database.repository.crud_repo import CrudRepo
from database.repository.user_account_repo import UserAccountRepo


class TransactionService:
    def __init__(self, engine):
        self.engine = engine

        self.user_account_crud_repo = CrudRepo(self.engine, UserAccountTable)
        self.currency_exch_crud_repo = UserAccountRepo(self.engine, CurrencyExchangeTable)
        self.transaction_crud_repo = UserAccountRepo(self.engine, TransactionTable)
        self.card_transaction_crud_repo = UserAccountRepo(self.engine, CardTransactionTable)
        self.card_crud_repo = CrudRepo(self.engine, CardTable)

    def last_transactions(self, used_account: namedtuple, logged_in_user: namedtuple) -> None:
        """Get and print last 5 transactions """
        sorted_transactions = self._sort_transactions(self._get_all_transactions(used_account))
        filtered_transactions = self._filter_transactions(sorted_transactions, used_account)
        self._print_transactions(
            filtered_transactions[:len(sorted_transactions) if len(sorted_transactions) < 5 else 5], logged_in_user)

    def transactions_between_dates(self, used_account: namedtuple, dates: namedtuple) -> list[namedtuple]:
        """Return all transactions for the account"""
        sorted_transactions = self._sort_transactions(self._get_transactions_btwn_dates(used_account, dates))
        return self._filter_transactions(sorted_transactions, used_account)

    def _get_all_transactions(self, used_account: namedtuple) -> tuple:
        """The function returns all transactions for a given account"""
        cur_exch_out = self.currency_exch_crud_repo.find_all_with_condition(
            (CurrencyExchangeTable.id_user_account_out, used_account.id))
        cur_exch_in = self.currency_exch_crud_repo.find_all_with_condition(
            (CurrencyExchangeTable.id_user_account_in, used_account.id))
        transactions = self.transaction_crud_repo.find_all_with_condition(
            (TransactionTable.id_user_account, used_account.id))
        card_transactions = self.card_transaction_crud_repo.find_all_with_condition(
            (CardTransactionTable.id_user_account, used_account.id))
        return cur_exch_out, cur_exch_in, transactions, card_transactions

    def _get_transactions_btwn_dates(self, used_account: namedtuple, dates: namedtuple) -> tuple:
        """The function returns all transactions for a given account and dates"""

        cur_exch_out = self.currency_exch_crud_repo.find_btwn_dates(
            (CurrencyExchangeTable.transaction_time,
             dates.start_date,
             dates.end_date,
             CurrencyExchangeTable.id_user_account_out,
             used_account.id))
        cur_exch_in = self.currency_exch_crud_repo.find_btwn_dates(
            (CurrencyExchangeTable.transaction_time,
             dates.start_date,
             dates.end_date,
             CurrencyExchangeTable.id_user_account_in,
             used_account.id))
        transactions = self.transaction_crud_repo.find_btwn_dates(
            (TransactionTable.transaction_time,
             dates.start_date,
             dates.end_date,
             TransactionTable.id_user_account,
             used_account.id))
        card_transactions = self.card_transaction_crud_repo.find_btwn_dates(
            (CardTransactionTable.transaction_time,
             dates.start_date,
             dates.end_date,
             CardTransactionTable.id_user_account,
             used_account.id))
        return cur_exch_out, cur_exch_in, transactions, card_transactions

    def _filter_transactions(self, transactions: list[namedtuple], used_account: namedtuple) -> list[namedtuple]:
        """Filter the results you get from different namedtuple to one general type"""
        filtred_transactions = []
        for transaction in transactions:
            if type(transaction).__name__ == 'ExchangeCurrency':
                if used_account.id == transaction.id_user_account_out:
                    filtred_transactions.append(transactions_to_statement_named_tuple((
                        transaction.transaction_time,
                        f"Exchanged to {self.user_account_crud_repo.find_by_id(transaction.id_user_account_in)[3]}",
                        "",
                        "",
                        transaction.transfer_amount_out,
                        "",
                        transaction.exchange_rate_out,
                        transaction.balance_out,
                        transaction.commission_in_main_user_currency
                    )))
                else:
                    filtred_transactions.append(transactions_to_statement_named_tuple((
                        transaction.transaction_time,
                        f"Exchanged to {used_account.currency}",
                        "",
                        "",
                        "",
                        transaction.transfer_amount_in,
                        transaction.exchange_rate_in,
                        transaction.balance_in,
                        transaction.commission_in_main_user_currency
                    )))
            elif type(transaction).__name__ == 'Transaction':
                if transaction.payment == 'YES':
                    filtred_transactions.append(transactions_to_statement_named_tuple((
                        transaction.transaction_time,
                        f"From {transaction.payer_name}",
                        transaction.payer_account_number,
                        "",
                        "",
                        transaction.amount,
                        "",
                        transaction.balance,
                        ""
                    )))
                else:
                    filtred_transactions.append(transactions_to_statement_named_tuple((
                        transaction.transaction_time,
                        f"To {transaction.payer_name}",
                        transaction.payer_account_number,
                        "",
                        transaction.amount,
                        "",
                        "",
                        transaction.balance,
                        ""
                    )))
            elif type(transaction).__name__ == 'CardTransaction':
                card_number = self.card_crud_repo.find_by_id(transaction.id_card)
                if transaction.payout == 'YES':
                    filtred_transactions.append(transactions_to_statement_named_tuple((
                        transaction.transaction_time,
                        transaction.payer_name,
                        "",
                        card_number[2] if card_number else "NOT EXIST",
                        transaction.amount,
                        "",
                        transaction.rate_tu_used_account,
                        transaction.balance,
                        transaction.commission_in_main_user_currency
                    )))
                else:
                    filtred_transactions.append(transactions_to_statement_named_tuple((
                        transaction.transaction_time,
                        transaction.payer_name,
                        transaction.payer_account_number,
                        card_number[2] if card_number else "NOT EXIST",
                        "",
                        transaction.amount,
                        transaction.rate_tu_used_account,
                        transaction.balance,
                        transaction.commission_in_main_user_currency
                    )))
        return filtred_transactions

    @staticmethod
    def _sort_transactions(elements: tuple) -> list[namedtuple]:
        """The function sorts the transactions by date"""
        cur_exch_out_namedtuple = [currency_exchange_named_tuple(item) for item in elements[0]]
        cur_exch_in_namedtuple = [currency_exchange_named_tuple(item) for item in elements[1]]
        transactions_namedtuple = [transaction_named_tuple(item) for item in elements[2]]
        card_transactions_namedtuple = [card_transaction_named_tuple(item) for item in elements[3]]
        all_transactions = \
            cur_exch_out_namedtuple + cur_exch_in_namedtuple + transactions_namedtuple + card_transactions_namedtuple
        return sorted(all_transactions, key=lambda x: x.transaction_time, reverse=True)

    @staticmethod
    def _print_transactions(transactions: list[namedtuple], logged_in_user: namedtuple) -> None:
        """Print transactions based on Transaction namedtuple"""

        def space(text: str, elements: int) -> str:
            return ' ' * (elements - len(text)) if text else ' ' * elements

        for x in transactions:
            print(
                f"Data: {x.date} Customer: {x.customer}{space(x.customer, 16)} "
                f"Acc number: {x.acc_number}{space(x.acc_number, 22)} "
                f"Card nb: {x.card_nb}{space(x.card_nb, 18)} "
                f"Payout: {x.payout}{space(str(x.payout), 7)} "
                f"Payment: {x.payment}{space(str(x.payment), 7)} "
                f"Rate: {x.rate}{space(str(x.rate), 4)} "
                f"Saldo: {x.saldo}{space(str(x.saldo), 7)} "
                f"Fee in {logged_in_user.main_currency}: {x.commission}")
