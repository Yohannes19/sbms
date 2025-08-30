import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.session import Base
from app.models import Room
from app.services.rooms import create_room, get_room, list_rooms, update_room, delete_room
from app.schemas.room import RoomCreate

@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_crud_room(session):
    payload = RoomCreate(number="301", floor="3", capacity=2, active=True)
    r = create_room(session, payload)
    assert r.id is not None
    assert r.number == "301"

    r2 = get_room(session, r.id)
    assert r2.floor == "3"

    all_r = list_rooms(session)
    assert len(all_r) == 1

    updated = update_room(session, r, number="301A", capacity=3)
    assert updated.number == "301A"
    assert updated.capacity == 3

    delete_room(session, updated)
    assert get_room(session, r.id) is None