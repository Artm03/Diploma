import base64
from typing import List
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel

from app.utils import users


class Settings(BaseModel):
    authjwt_algorithm: str = users.ALGORITHM
    authjwt_decode_algorithms: List[str] = [users.ALGORITHM]
    authjwt_token_location: set = {'cookies'}
    authjwt_refresh_cookie_key: str = 'refresh_token'
    authjwt_cookie_csrf_protect: bool = False
    authjwt_secret_key: str = users.SECRET_KEY


@AuthJWT.load_config
def get_config():
    return Settings()
