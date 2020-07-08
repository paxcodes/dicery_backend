from sqlalchemy.orm import Session
from . import models, schemas


def get_room(db: Session, room_code: str):
    return db.query(models.Room).filter(models.Room.code == room_code).first()


def get_available_room(db: Session, room_code: str):
    raise NotImplementedError


def create_room(db: Session, room: schemas.RoomCreate):
    # TODO move room code generation here instead of
    # it being in the RoomCreate schema?
    room = models.Room(code=room.code, owner=room.owner)
    db.add(room)
    db.commit()
    # TODO do we really need to refresh? Check whether room
    # will have the `isAvailable` already after we commit()
    # and before we refresh. If it does, then we don't need
    # to refresh
    db.refresh(room)
    return room
