from dataclasses import dataclass


@dataclass
class User:
    id: int = None
    login: str = None
    password: str = None
    creation_date: str = None
