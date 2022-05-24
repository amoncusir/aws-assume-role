from dataclasses import dataclass


@dataclass
class AuthorizationDetails:

    access_key: str
    secret_key: str
    session_token: str
