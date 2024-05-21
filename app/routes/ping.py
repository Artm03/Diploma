from fastapi import APIRouter

from app.api import ping as ping_api
from app.schemas.ping import Ping

router = APIRouter()


@router.get('/api/ping', response_model=Ping)
async def get_ping_message():
    return await ping_api.handle()
