from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    id: int = None
    login: str = None
    password: str = None
    creation_date: datetime = None
