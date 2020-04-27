from typing import NamedTuple
from src.model.user_recovery_token import UserRecoveryToken

class SerializedUserRecoveryToken(NamedTuple):
    """
    It has the responsability of representing all the user_recovery_token data with strings
    """
    email: str
    token: str
    timestamp: str

    @classmethod
    def from_user_recovery_token(cls, user_recovery_token: UserRecoveryToken) -> 'SerializedUserRecoveryToken':
        return SerializedUserRecoveryToken(email=user_recovery_token.email, token=user_recovery_token.token,
                                           timestamp=user_recovery_token.timestamp)
