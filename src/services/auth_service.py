from abc import ABC, abstractmethod


class AuthService(ABC):

    def __init__(self):
        self.clients = {}

    @abstractmethod
    def validate_token(self, token) -> dict:
        """
        Validates an auth token, returns an object which includes user id
        May also return an error object with a specific error message
        """
        pass
