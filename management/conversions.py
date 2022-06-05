from collections import namedtuple


def user_named_tuple(items):
    User = namedtuple("User", "id login password creation_date")
    return User(*items)


def user_data_named_tuple(items):
    UserData = namedtuple("UserData", "id id_user name surname country address email phone")
    return UserData(*items)


def user_account_named_tuple(items):
    UserAccount = namedtuple("UserData", "id id_user_data account_number currency amount")
    return UserAccount(*items)

