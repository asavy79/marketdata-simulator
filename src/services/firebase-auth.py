from auth_service import AuthService
from firebase_admin import auth


class FirebaseAuth(AuthService):

    def __init__(self):
        super().__init__()

    def validate_token(self, token) -> dict:
        try:

            decoded_token = auth.verify_id_token(token)
            user_id = decoded_token['user_id']

            return {"success": True, "user_id": user_id}

        except auth.ExpiredIdTokenError as e:
            pass

        except auth.RevokedIdTokenError as e:
            pass

        except auth.InvalidIdTokenError as e:
            pass

        except Exception as e:
            pass
