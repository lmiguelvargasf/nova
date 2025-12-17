from dataclasses import dataclass

import strawberry


@strawberry.input
@dataclass
class UserInput:
    username: str
    first_name: str
    last_name: str
    email: str
