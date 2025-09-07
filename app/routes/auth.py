from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
import app.services.users as users_svc
from app.schemas.user import UserCreate, UserRead, Token
from app.core.security import create_access_token, decode_access_token
from app.core.config import settings
from app.core.exceptions import RedirectException
from app.models.user import User

templates = Jinja2Templates(directory="app/templates")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

router = APIRouter(prefix="/auth", tags=["auth"])

# API token endpoint (existing)
@router.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = users_svc.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    access_token = create_access_token(subject=user.id)
    return {"access_token": access_token, "token_type": "bearer"}

# -- UI: show login page --
@router.get("/login")
def login_ui(request: Request):
    return templates.TemplateResponse("auth_login.html", {"request": request})

# -- UI: process login form, set HttpOnly cookie and redirect --
@router.post("/login")
def login_ui_post(request: Request, response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = users_svc.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        # re-render login with error
        return templates.TemplateResponse("auth_login.html", {"request": request, "error": "Invalid credentials"}, status_code=401)

    token = create_access_token(subject=user.id)
    redirect = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    # set HttpOnly cookie with token (also set SameSite and secure as needed)
    redirect.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=60 * settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        samesite="lax",
        secure=False # set True in production with HTTPS
    )
    return redirect

# -- UI: register page --
@router.get("/register")
def register_ui(request: Request):
    return templates.TemplateResponse("auth_register.html", {"request": request})

# API registration endpoint
@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    existing = users_svc.get_user_by_username(db, payload.username)
    if existing:
        raise HTTPException(status_code=400, detail="username already registered")
    user = users_svc.create_user(db, payload)
    return user

# logout (clear cookie)
@router.get("/logout")
def logout():
    redirect = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    redirect.delete_cookie("access_token")
    return redirect

# Helper: get current user from Authorization header OR cookie
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # oauth2_scheme will look for Authorization header; if missing it will raise.
    try:
        payload = decode_access_token(token)
        user_id = int(payload.get("sub"))
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
    user = users_svc.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

# UI-friendly dependency: check cookie and redirect to login when missing / invalid
def require_user_ui(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        # Redirect the browser to login
        raise RedirectException(path="/auth/login")

    try:
        payload = decode_access_token(token)
        user_id = int(payload.get("sub"))
    except Exception:
        raise RedirectException(path="/auth/login")
        
    user = users_svc.get_user(db, user_id)
    if not user:
        raise RedirectException(path="/auth/login")
        
    return user
