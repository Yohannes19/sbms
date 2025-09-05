from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
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
def room_new_ui(request: Request, db: Session = Depends(get_db)):
    # pass query params to template to allow pre-filling fields (e.g. /rooms/ui/new?number=900)
    form_prefill = dict(request.query_params)
    return templates.TemplateResponse("room_form.html", {"request": request, "action": "create", "form": form_prefill})

# handle HTML form POST for creating a room
@router.post("/ui/new")
async def room_create_ui(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    # basic parsing / normalization
    data = {k: v for k, v in form.items()}
    # parse comma-separated lists
    def _split_list(val):
        if not val:
            return None
        return [s.strip() for s in val.split(",") if s.strip()]

    data["amenities"] = _split_list(data.get("amenities"))
    data["tags"] = _split_list(data.get("tags"))
    data["images"] = _split_list(data.get("images"))

    # booleans from form checkbox (present/true -> True)
    for b in ("has_ac", "private_bath", "accessible", "available"):
        data[b] = True if form.get(b) in ("on", "true", "True", "1") else False

    # numeric conversions
    try:
        if data.get("capacity") not in (None, ""):
            data["capacity"] = int(data["capacity"])
        if data.get("bed_count") not in (None, ""):
            data["bed_count"] = int(data["bed_count"])
        if data.get("max_occupancy") not in (None, ""):
            data["max_occupancy"] = int(data["max_occupancy"])
        if data.get("sq_meters") not in (None, ""):
            data["sq_meters"] = float(data["sq_meters"])
        if data.get("price") not in (None, ""):
            data["price"] = float(data["price"])
        if data.get("deposit_amount") not in (None, ""):
            data["deposit_amount"] = float(data["deposit_amount"])
    except ValueError as e:
        return templates.TemplateResponse("room_form.html", {"request": request, "action": "create", "error": "Invalid numeric value", "form": data}, status_code=400)

    # validate via Pydantic schema by constructing RoomCreate
    try:
        payload = RoomCreate(**data)
    except Exception as e:
        return templates.TemplateResponse("room_form.html", {"request": request, "action": "create", "error": str(e), "form": data}, status_code=400)

    room = svc.create_room(db, payload)
    return RedirectResponse(f"/rooms/ui/{room.id}", status_code=status.HTTP_303_SEE_OTHER)

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

# handle HTML form POST for editing a room
@router.post("/ui/{room_id}/edit")
async def room_edit_post(room_id: int, request: Request, db: Session = Depends(get_db)):
    room = svc.get_room(db, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    form = await request.form()
    data = {k: v for k, v in form.items()}

    def _split_list(val):
        if not val:
            return None
        return [s.strip() for s in val.split(",") if s.strip()]

    data["amenities"] = _split_list(data.get("amenities"))
    data["tags"] = _split_list(data.get("tags"))
    data["images"] = _split_list(data.get("images"))

    for b in ("has_ac", "private_bath", "accessible", "available"):
        data[b] = True if form.get(b) in ("on", "true", "True", "1") else False

    try:
        if data.get("capacity") not in (None, ""):
            data["capacity"] = int(data["capacity"])
        if data.get("bed_count") not in (None, ""):
            data["bed_count"] = int(data["bed_count"])
        if data.get("max_occupancy") not in (None, ""):
            data["max_occupancy"] = int(data["max_occupancy"])
        if data.get("sq_meters") not in (None, ""):
            data["sq_meters"] = float(data["sq_meters"])
        if data.get("price") not in (None, ""):
            data["price"] = float(data["price"])
        if data.get("deposit_amount") not in (None, ""):
            data["deposit_amount"] = float(data["deposit_amount"])
    except ValueError:
        return templates.TemplateResponse("room_form.html", {"request": request, "room": room, "action": "edit", "error": "Invalid numeric value", "form": data}, status_code=400)

    # build partial update dict (exclude empty strings)
    changes = {k: v for k, v in data.items() if v not in (None, "")}
    try:
        updated = svc.update_room(db, room, **changes)
    except Exception as e:
        return templates.TemplateResponse("room_form.html", {"request": request, "room": room, "action": "edit", "error": str(e), "form": data}, status_code=400)

    return RedirectResponse(f"/rooms/ui/{updated.id}", status_code=status.HTTP_303_SEE_OTHER)

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