from fastapi import APIRouter

from app.schemas.ping import Ping

router = APIRouter()


@router.get('/', response_model=Ping)
async def get_ping_message():
    return Ping(message="Hello world!")
