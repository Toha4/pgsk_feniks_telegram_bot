from dataclasses import dataclass


@dataclass
class User:
    id: int
    user_id: int
    tg_username: str
    name: str
    phone_number: str
    garage_number: int
    date_create: str
    status: int
    is_admin: int

@dataclass
class UserShort:
    id: int
    name: str
    garage_number: int
    status: int
    is_admin: int