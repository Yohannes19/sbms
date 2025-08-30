from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models import Room
from app.schemas import RoomCreate, RoomRead, RoomUpdate
import app.services.rooms as svc

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(prefix="/rooms", tags=["rooms"])

# UI endpoints (register before param routes)
@router.get("/ui")
def rooms_ui(request: Request, db: Session = Depends(get_db)):
    rooms = svc.list_rooms(db)
    return templates.TemplateResponse("rooms.html", {"request": request, "rooms": rooms})

@router.get("/ui/new")
def room_new_ui(request: Request):
    return templates.TemplateResponse("room_form.html", {"request": request, "action": "create"})

@router.get("/ui/{room_id}")
def room_detail_ui(room_id: int, request: Request, db: Session = Depends(get_db)):
    room = svc.get_room(db, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return templates.TemplateResponse("room_detail.html", {"request": request, "room": room})

@router.get("/ui/{room_id}/edit")
def room_edit_ui(room_id: int, request: Request, db: Session = Depends(get_db)):
    room = svc.get_room(db, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return templates.TemplateResponse("room_form.html", {"request": request, "room": room, "action": "edit"})

# API endpoints
@router.get("/", response_model=List[RoomRead])
def list_rooms(db: Session = Depends(get_db)):
    return svc.list_rooms(db)

@router.post("/", response_model=RoomRead, status_code=status.HTTP_201_CREATED)
def create_room(payload: RoomCreate, db: Session = Depends(get_db)):
    return svc.create_room(db, payload)

@router.get("/{room_id}", response_model=RoomRead)
def get_room(room_id: int, db: Session = Depends(get_db)):
    room = svc.get_room(db, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room

@router.put("/{room_id}", response_model=RoomRead)
def update_room(room_id: int, payload: RoomUpdate, db: Session = Depends(get_db)):
    room = svc.get_room(db, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    changes = payload.dict(exclude_unset=True)
    return svc.update_room(db, room, **changes)

@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_room(room_id: int, db: Session = Depends(get_db)):
    room = svc.get_room(db, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    svc.delete_room(db, room)
    return None