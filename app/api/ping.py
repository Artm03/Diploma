from app.schemas.ping import Ping


async def handle():
    return Ping(message="OK")
