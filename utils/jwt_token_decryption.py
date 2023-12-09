import jwt
from django.conf import settings


def decode_jwt_token(token):
    try:
        # Decode the token using the secret key
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        # Handle token expiration
        return {"error": "Token has expired"}
    except jwt.InvalidTokenError:
        # Handle invalid token
        return {"error": "Invalid token"}
