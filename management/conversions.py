from collections import namedtuple


def user_data_named_tuple(items):
    UserData = namedtuple("UserData", "id name surname country address email phone login password creation_date")
    return UserData(*items)


def user_account_named_tuple(items):
    UserAccount = namedtuple("UserAccount", "id id_user_data account_number currency balance")
    return UserAccount(*items)

