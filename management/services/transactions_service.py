from management.conversions import *
from management.validation import *
from data_base.model.tables import CurrencyExchangeTable, CardTransactionTable, TransactionTable, UserAccountTable
from data_base.model.tables import CardTable
from data_base.repository.crud_repo import CrudRepo
from data_base.repository.user_account_repo import UserAccountRepo
from datetime import datetime


class TransactionService:
    def last_transactions(self, engine, used_account: namedtuple) -> None:
        """Get and print last 5 transactions """
        sorted_transactions = self._sort_transactions(self.get_all_transactions(engine, used_account))
        filtered_transactions = self._filter_transactions(engine, sorted_transactions, used_account)
        self.print_transactions(filtered_transactions[:len(sorted_transactions) if len(sorted_transactions) < 5 else 5])

    def transactions_between_dates(self, engine, used_account: namedtuple) -> list[namedtuple]:
        """Return all transactions for the account"""
        sorted_transactions = self._sort_transactions(self.get_transactions_btwn_dates(engine, used_account))
        return self._filter_transactions(engine, sorted_transactions, used_account)

    @staticmethod
    def print_transactions(transactions: list[namedtuple]) -> None:
        """Print transactions based on Transaction namedtuple"""
        def space(text: str, elements: int) -> str:
            return ' ' * (elements - len(text)) if text else ' ' * elements
        for x in transactions:
            print(f"Data: {x.date} Customer: {x.customer}{space(x.customer, 20)} "
                  f"Acc number: {x.acc_number}{space(x.acc_number, 22)} "
                  f"Card nb: {x.card_nb}{space(x.card_nb, 16)} "
                  f"Payout: {x.payout}{space(str(x.payout), 7)} "
                  f"Payment: {x.payment}{space(str(x.payment), 7)} "
                  f"Rate: {x.rate}{space(str(x.rate), 4)} "
                  f"Saldo: {x.saldo}{space(str(x.saldo), 7)} "
                  f"Commission: {x.commission}")

    @staticmethod
    def get_all_transactions(engine, used_account: namedtuple) -> tuple:
        """The function returns all transactions for a given account"""
        cur_exch_out = CrudRepo(engine, CurrencyExchangeTable).find_all_with_condition(
            (CurrencyExchangeTable.id_user_account_out, used_account.id))
        cur_exch_in = CrudRepo(engine, CurrencyExchangeTable).find_all_with_condition(
            (CurrencyExchangeTable.id_user_account_in, used_account.id))
        transactions = CrudRepo(engine, TransactionTable).find_all_with_condition(
            (TransactionTable.id_user_account, used_account.id))
        card_transactions = CrudRepo(engine, CardTransactionTable).find_all_with_condition(
            (CardTransactionTable.id_user_account, used_account.id))
        return cur_exch_out, cur_exch_in, transactions, card_transactions

    @staticmethod
    def get_transactions_btwn_dates(engine, used_account: namedtuple) -> tuple:
        """The function returns all transactions for a given account and dates"""
        dates = TransactionService.get_dates()
        cur_exch_out = UserAccountRepo(engine, CurrencyExchangeTable).find_btwn_dates(
            (CurrencyExchangeTable.transaction_time,
             dates.start_date,
             dates.end_date,
             CurrencyExchangeTable.id_user_account_out,
             used_account.id))
        cur_exch_in = UserAccountRepo(engine, CurrencyExchangeTable).find_btwn_dates(
            (CurrencyExchangeTable.transaction_time,
             dates.start_date,
             dates.end_date,
             CurrencyExchangeTable.id_user_account_in,
             used_account.id))
        transactions = UserAccountRepo(engine, TransactionTable).find_btwn_dates(
            (TransactionTable.transaction_time,
             dates.start_date,
             dates.end_date,
             TransactionTable.id_user_account,
             used_account.id))
        card_transactions = UserAccountRepo(engine, CardTransactionTable).find_btwn_dates(
            (CardTransactionTable.transaction_time,
             dates.start_date,
             dates.end_date,
             CardTransactionTable.id_user_account,
             used_account.id))
        return cur_exch_out, cur_exch_in, transactions, card_transactions

    @staticmethod
    def _filter_transactions(engine, transactions: list[namedtuple], used_account: namedtuple) -> list[namedtuple]:
        """Filter the results you get from different namedtuple to one general type"""
        filtred_transactions = []
        for transaction in transactions:
            if type(transaction).__name__ == 'ExchangeCurrency':
                if used_account.id == transaction.id_user_account_out:
                    filtred_transactions.append(all_transactions_named_tuple((
                        transaction.transaction_time,
                        f"Exchanged to {CrudRepo(engine, UserAccountTable).find_by_id(transaction.id_user_account_in)[3]}",
                        "",
                        "",
                        transaction.transfer_amount_out,
                        "",
                        transaction.exchange_rate_out,
                        transaction.balance_out,
                        ""
                    )))
                else:
                    filtred_transactions.append(all_transactions_named_tuple((
                        transaction.transaction_time,
                        f"Exchanged to {used_account.currency}",
                        "",
                        "",
                        "",
                        transaction.transfer_amount_in,
                        transaction.exchange_rate_in,
                        transaction.balance_in,
                        ""
                    )))
            elif type(transaction).__name__ == 'Transaction':
                if transaction.payment == 'YES':
                    filtred_transactions.append(all_transactions_named_tuple((
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
                    filtred_transactions.append(all_transactions_named_tuple((
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
            else:
                filtred_transactions.append(all_transactions_named_tuple((
                    transaction.transaction_time,
                    transaction.payer_name,
                    "",
                    CrudRepo(engine, CardTable).find_by_id(transaction.id_card)[2],
                    transaction.amount,
                    "",
                    transaction.rate,
                    transaction.balance,
                    transaction.commission
                )))
        return filtred_transactions

    @staticmethod
    def _sort_transactions(elements: tuple) -> list[namedtuple]:
        """The function sorts the transactions by date"""
        cur_exch_out_namedtuple = [currency_exchange_named_tuple(item) for item in elements[0]]
        cur_exch_in_namedtuple = [currency_exchange_named_tuple(item) for item in elements[1]]
        transactions_namedtuple = [transaction_named_tuple(item) for item in elements[2]]
        card_transactions_namedtuple = [card_transaction_named_tuple(item) for item in elements[3]]
        all_transactions = cur_exch_out_namedtuple + cur_exch_in_namedtuple + \
                           transactions_namedtuple + card_transactions_namedtuple
        return sorted(all_transactions, key=lambda x: x.transaction_time, reverse=True)

    @staticmethod
    def get_dates() -> namedtuple:
        """Enter and validate dates for which you want to find transactions"""
        start_date = datetime.fromisoformat(get_answer(
            validation_datetime,
            'Enter the start date: ',
            'Entered date doesn"t exist. Enter the date in this format -  2000-12-31'))
        end_date = datetime.fromisoformat(get_answer(
            validation_datetime,
            'Enter the end date: ',
            'Entered date doesn"t exist. Enter the date in this format -  2000-12-31'))
        return dates_named_tuple((start_date, end_date))
