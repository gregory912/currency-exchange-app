from collections import namedtuple


def user_data_named_tuple(items):
    UserData = namedtuple("UserData", "id name surname country address email phone login password creation_date")
    return UserData(*items)


def user_account_named_tuple(items):
    UserAccount = namedtuple("UserAccount", "id id_user_data account_number currency balance")
    return UserAccount(*items)


def currency_exchange_named_tuple(items):
    ExchangeCurrency = namedtuple("ExchangeCurrency",
                                  "id "
                                  "id_user_account_out "
                                  "transfer_amount_out "
                                  "exchange_rate_out "
                                  "balance_out "
                                  "id_user_account_in "
                                  "transfer_amount_in "
                                  "exchange_rate_in "
                                  "balance_in "
                                  "transaction_time")
    return ExchangeCurrency(*items)


def transaction_named_tuple(items):
    Transaction = namedtuple("Transaction",
                             "id "
                             "id_user_account "
                             "payment "
                             "payout "
                             "transfer_title "
                             "transaction_time "
                             "amount "
                             "balance "
                             "payer_name "
                             "payer_account_number")
    return Transaction(*items)


def card_transaction_named_tuple(items):
    CardTransaction = namedtuple("CardTransaction",
                                 "id "
                                 "id_user_account "
                                 "transaction_time "
                                 "amount "
                                 "commission "
                                 "balance "
                                 "payer_name "
                                 "id_card")
    return CardTransaction(*items)


def all_transactions_named_tuple(items):
    AllTransactions = namedtuple("AllTransactions",
                                 "date "
                                 "customer "
                                 "acc_number "
                                 "card_nb "
                                 "payout "
                                 "payment "
                                 "rate "
                                 "saldo "
                                 "comission")
    return AllTransactions(*items)


def dates_named_tuple(items):
    Dates = namedtuple("Dates",
                       "start_date "
                       "end_date ")
    return Dates(*items)
