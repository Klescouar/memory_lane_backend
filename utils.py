from typing import Optional
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import SecurityScopes, HTTPAuthorizationCredentials, HTTPBearer
import os
import certifi
import ssl
import urllib.request

ssl_context = ssl.create_default_context(cafile=certifi.where())


class UnauthorizedException(HTTPException):
    def __init__(self, detail: str, **kwargs):
        super().__init__(status.HTTP_403_FORBIDDEN, detail=detail)


class UnauthenticatedException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Requires authentication"
        )


class VerifyToken:
    def __init__(self):
        jwks_url = f"https://{os.getenv('AUTH0_DOMAIN')}/.well-known/jwks.json"
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        self.jwks_client = jwt.PyJWKClient(jwks_url, ssl_context=ssl_context)

    async def verify(
        self,
        security_scopes: SecurityScopes,
        token: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer()),
    ):

        if token is None:
            raise UnauthenticatedException

        try:
            signing_key = self.jwks_client.get_signing_key_from_jwt(
                token.credentials
            ).key
        except jwt.exceptions.PyJWKClientError as error:
            raise UnauthorizedException(str(error))
        except jwt.exceptions.DecodeError as error:
            raise UnauthorizedException(str(error))

        try:
            payload = jwt.decode(
                token.credentials,
                signing_key,
                algorithms=os.getenv("AUTH0_ALGORITHMS"),
                audience=os.getenv("AUTH0_API_AUDIENCE"),
                issuer=os.getenv("AUTH0_ISSUER"),
            )
        except Exception as error:
            raise UnauthorizedException(str(error))

        return payload
