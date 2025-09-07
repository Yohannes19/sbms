from fastapi import APIRouter, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.models.user import User
from app.routes.auth import require_user_ui

templates = Jinja2Templates(directory="app/templates")
router = APIRouter()


@router.get("/dashboard")
async def dashboard(request: Request, current_user: User = Depends(require_user_ui)):
    return templates.TemplateResponse("dashboard.html", {"request": request, "current_user": current_user})
