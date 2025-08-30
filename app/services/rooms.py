from typing import List, Optional
from sqlalchemy.orm import Session

from app.models import Room
from app.schemas.room import RoomCreate

def list_rooms(db: Session) -> List[Room]:
    return db.query(Room).order_by(Room.id.desc()).all()

def get_room(db: Session, room_id: int) -> Optional[Room]:
    return db.get(Room, room_id)

def create_room(db: Session, payload: RoomCreate) -> Room:
    room = Room(**payload.dict())
    db.add(room)
    db.commit()
    db.refresh(room)
    return room

def update_room(db: Session, room: Room, **changes) -> Room:
    for k, v in changes.items():
        setattr(room, k, v)
    db.commit()
    db.refresh(room)
    return room

def delete_room(db: Session, room: Room) -> None:
    db.delete(room)
    db.commit()