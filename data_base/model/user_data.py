from dataclasses import dataclass


@dataclass
class UserData:
    id: int = None
    id_user: int = None
    name: str = None
    surname: str = None
    country: str = None
    address: str = None
    email: str = None
    phone: str = None
