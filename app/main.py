import fastapi
from app.routes.ping import router as ping_routers
from app.routes.users import router as user_routers
from app.routes.email import router as email_routers

app = fastapi.FastAPI()

app.include_router(ping_routers)
app.include_router(user_routers)
app.include_router(email_routers)
