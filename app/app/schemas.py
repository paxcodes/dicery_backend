from datetime import datetime
from typing import List

from pydantic import BaseModel


class RoomLogBase(BaseModel):
    player: str
    roll: List[int]


class RoomLogCreate(RoomLogBase):
    pass


class RoomLog(RoomLogBase):
    room_code: str
    created_time: datetime

    class Config:
        orm_mode = True


class RoomBase(BaseModel):
    code: str
    owner: str


class RoomCreate(RoomBase):
    pass


class Room(RoomBase):
    isAvailable: bool

    class Config:
        orm_mode = True
