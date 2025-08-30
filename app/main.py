from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.routes import dashboard
from app.routes import tenants, contracts, rooms, payments


app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Routes
app.include_router(dashboard.router)
app.include_router(tenants.router)
app.include_router(contracts.router)
app.include_router(rooms.router)
app.include_router(payments.router)

@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})
