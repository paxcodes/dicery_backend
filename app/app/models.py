from sqlalchemy import Column, ARRAY, ForeignKey
from sqlalchemy import Integer, DateTime, String, Boolean
from sqlalchemy.orm import relationship

from .database import Base


class RoomPlayer(Base):
    __table_name__ = "room_players"

    room_code = Column(String, ForeignKey("rooms.code"), primary_key=True)
    player = Column(String, primary_key=True)

    room = relationship("Room", back_populates="players")


class RoomLog(Base):
    __tablename__ = "room_logs"

    room_code = Column(String, ForeignKey("rooms.code"), primary_key=True)
    player = Column(String, primary_key=True)
    created_time = Column(DateTime, primary_key=True)
    roll = Column(ARRAY(Integer), nullable=False)

    room = relationship("Room", back_populates="logs")


class Room(Base):
    __tablename__ = "rooms"

    code = Column(String, primary_key=True)
    isAvailable = Column(Boolean, nullable=False, default=True)
    owner = Column(String, nullable=False)

    logs = relationship(
        "RoomLog", order_by=RoomLog.created_time, back_populates="room"
    )

    players = relationship(
        "RoomPlayer", order_by=RoomPlayer.player, back_populates="room"
    )
