from collections import OrderedDict
from datetime import timedelta
from typing import Tuple
from queue import Queue, Empty

import asyncio
from fastapi import Depends, FastAPI, Form, Request, HTTPException, Response
from fastapi import Security, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyCookie
from sqlalchemy.orm import Session
from sse_starlette.sse import EventSourceResponse

from jose import JWTError, jwt

from . import crud, schemas
from .config import settings
from .database import SessionLocal
from .utils import CreateAccessToken, GenerateRoomCode


ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours
API_KEY_COOKIE_NAME = "key"

# THIS STRING IS ALSO USED BY THE APP.
CLOSE_ROOM_COMMAND = "***CLOSE_ROOM***"

api_key = APIKeyCookie(name=API_KEY_COOKIE_NAME)

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"])


lobbyQueues = {}


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_player_and_room(
    token: str = Security(api_key), db=Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate player and room",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        player: str = payload.get("sub")
        room_code: str = payload.get("dicery_room")
        if player is None or room_code is None:
            raise credentials_exception
        token_data = schemas.TokenData(player=player, room_code=room_code)
    except JWTError:
        raise credentials_exception
    # TODO verify player is *in* the room.
    room = crud.get_room(db, token_data.room_code)
    if room is None:
        raise credentials_exception
    return player, room


@app.get("/")
async def get_home():
    return "Hello World!"


@app.put("/rooms/{room_code}/status/0")
async def closeRoomLobby(
    room_code: str, playerAndRoom=Depends(get_current_player_and_room)
):
    currentPlayer, room = playerAndRoom
    if room_code not in lobbyQueues:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room does not exist or already closed.",
        )

    if room_code != room.code or currentPlayer != room.owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )

    for aPlayer in lobbyQueues[room_code]:
        lobbyQueues[room_code][aPlayer].put(CLOSE_ROOM_COMMAND)


@app.post("/rooms", response_model=schemas.Room)
def create_room(
    response: Response,
    room_owner: str = Form(...),
    db: Session = Depends(get_db),
):
    while True:
        room_code = GenerateRoomCode()
        room = crud.get_room(db, room_code)
        if not room:
            break

    room = schemas.RoomCreate(code=room_code, owner=room_owner)
    # TODO make sure the queue is removed / cleaned up if the room has
    # been CLOSED
    lobbyQueues[room_code] = OrderedDict()
    lobbyQueues[room_code][room_owner] = Queue()

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = CreateAccessToken(
        data={"sub": room_owner, "dicery_room": room_code},
        expires_delta=access_token_expires,
    )
    response.set_cookie(
        key=API_KEY_COOKIE_NAME, value=f"{access_token}", httponly=True
    )

    return crud.create_room(db=db, room=room)


@app.get("/lobby/{room_code}")
async def join_lobby(
    req: Request, playerAndRoom=Depends(get_current_player_and_room)
):
    player, room = playerAndRoom
    # TODO validate whether player can join this lobby
    # TODO verify room.code == room_code
    # return {"player": player}
    async def streamLobbyActivity():
        yield ",".join(lobbyQueues[room.code].keys())
        # TODO get all players currently in the room
        # yield players
        while True:
            disconnected = await req.is_disconnected()
            if disconnected:
                break
            try:
                playerLobbyQueue = lobbyQueues[room.code][player]

                # TODO we know that `break`ing from the loop
                # will cause the stream to end. (TODO verify in the
                # app) -- when owner closes the room, break ittt.
                queueEntry = playerLobbyQueue.get(block=False)
                if queueEntry == CLOSE_ROOM_COMMAND:
                    del lobbyQueues[room.code][player]
                    if len(lobbyQueues[room.code]) == 0:
                        del lobbyQueues[room.code]
                    yield CLOSE_ROOM_COMMAND
                    break
                else:
                    playerWhoJoined = queueEntry
            except Empty:
                pass
            else:
                yield playerWhoJoined

    return EventSourceResponse(streamLobbyActivity())


@app.post("/token", response_model=schemas.Room)
async def validate_room_for_access_token(
    response: Response,
    room_code: str = Form(...),
    player: str = Form(...),
    db: Session = Depends(get_db),
):
    room = crud.get_available_room(db=db, room_code=room_code)
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Room not found"
        )

    # TODO if player `already exists`, concatenate with `_[NUMBER]`
    # player = f"{player}_{number}"
    # TODO add player to the database so we can confirm later that the player
    # can submit/subscribe.
    # TODO ^^^ Also we need a list of players *already* in the room.
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = CreateAccessToken(
        data={"sub": player, "dicery_room": room_code},
        expires_delta=access_token_expires,
    )

    response.set_cookie(
        key=API_KEY_COOKIE_NAME, value=f"{access_token}", httponly=True
    )

    if room_code not in lobbyQueues:
        lobbyQueues[room_code] = OrderedDict()
    for playername in lobbyQueues[room_code]:
        lobbyQueues[room_code][playername].put(player)
    lobbyQueues[room_code][player] = Queue()
    return room
