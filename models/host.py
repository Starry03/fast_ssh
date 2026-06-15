from typing import TypedDict


class Host(TypedDict):
    id: int
    name: str
    ip: str
    username: str
    password: str