from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.routes import dashboard
from app.routes import tenants, contracts, rooms, payments
from app.routes import auth as auth_routes
from app.routes.auth import require_user_ui
from app.db.session import get_db
from app.models import User


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
app.include_router(auth_routes.router)

@app.get("/")
def read_root(request: Request, current_user = Depends(require_user_ui), db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.id.desc()).all()
    return templates.TemplateResponse("dashboard.html", {"request": request, "current_user": current_user, "users": users})
