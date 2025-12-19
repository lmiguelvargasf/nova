from dataclasses import dataclass

import strawberry


@strawberry.input
@dataclass
class UserInput:
    email: str
    password: str
    first_name: str
    last_name: str
