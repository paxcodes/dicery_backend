from typing import List, Tuple

from sqlalchemy.orm import Session

from . import models, schemas


def get_room(db: Session, room_code: str):
    return db.query(models.Room).filter(models.Room.code == room_code).first()


def get_available_room(db: Session, room_code: str):
    return (
        db.query(models.Room)
        .filter(models.Room.code == room_code, models.Room.isAvailable)
        .first()
    )


def close_room(db: Session, room_code: str):
    db.query(models.Room).filter(models.Room.code == room_code).update(
        {"isAvailable": False}
    )
    db.commit()


def create_room(db: Session, roomSchema: schemas.RoomCreate) -> models.Room:
    # TODO move room code generation here instead of
    # it being in the RoomCreate schema?
    room = models.Room(code=roomSchema.code, owner=roomSchema.owner)
    db.add(room)
    db.commit()
    # TODO do we really need to refresh? Check whether room
    # will have the `isAvailable` already after we commit()
    # and before we refresh. If it does, then we don't need
    # to refresh
    db.refresh(room)
    return room


def delete_room(db: Session, room_code: str):
    db.query(models.Room).filter(models.Room.code == room_code).delete()
    db.commit()


def add_room_player(db: Session, room_player: schemas.RoomPlayer):
    room_player = models.RoomPlayer(
        room_code=room_player.room_code, player=room_player.player
    )
    db.add(room_player)
    db.commit()


def get_room_players(db: Session, room_code: str) -> List[str]:
    queryResult: List[Tuple[str]] = db.query(models.RoomPlayer.player).filter(
        models.RoomPlayer.room_code == room_code
    ).all()
    return [row[0] for row in queryResult]


def get_all_players(db: Session) -> List[str]:
    return db.query(models.RoomPlayer).all()
