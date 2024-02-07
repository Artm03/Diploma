import fastapi
from app.routes.ping import router as ping_routers

app = fastapi.FastAPI()

app.include_router(ping_routers)
