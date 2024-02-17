from app.oauth2 import AuthJWT

from fastapi import Response


async def handle(
    response: Response,
    Authorize: AuthJWT,
):
    Authorize.unset_jwt_cookies()
    response.set_cookie('logged_in', '', -1)

    return {'status': 'success'}
