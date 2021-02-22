import json
from datetime import datetime, timedelta, timezone

from broadcaster import Broadcast
from fastapi import (
    Depends,
    FastAPI,
    Form,
    HTTPException,
    Request,
    Response,
    Security,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyCookie
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from sse_starlette.sse import EventSourceResponse

from . import crud, schemas
from .config import settings
from .database import SessionLocal
from .utils import CleanDiceRolls, CreateAccessToken, GenerateRoomCode

ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours
API_KEY_COOKIE_NAME = "key"

# THIS STRING IS ALSO USED BY THE APP.
CLOSE_ROOM_COMMAND = "***CLOSE_ROOM***"

api_key = APIKeyCookie(name=API_KEY_COOKIE_NAME)

broadcast = Broadcast(settings.SQLALCHEMY_DATABASE_URI)
app = FastAPI(on_startup=[broadcast.connect], on_shutdown=[broadcast.disconnect],)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["GET", "PUT"],
)


roomQueues = {}


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


@app.post("/rolls/{room_code}")
async def submit_dice_roll(
    room_code: str,
    diceRolls: str = Form(...),
    playerAndRoom=Depends(get_current_player_and_room),
):
    player, room = playerAndRoom
    if room.code != room_code:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )

    try:
        diceRolls = CleanDiceRolls(diceRolls)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The dice rolls are in a bad format.",
        )

    timestamp = str(datetime.now(timezone.utc))
    data = f"{player}|{diceRolls}|{timestamp}"
    await broadcast.publish(channel=room_code, message=data)


@app.get("/rooms/{room_code}")
async def join_room(
    room_code: str, req: Request, playerAndRoom=Depends(get_current_player_and_room),
):
    player, room = playerAndRoom
    if room.code != room_code:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )

    async def streamRoomActivity():
        while True:
            disconnected = await req.is_disconnected()
            if disconnected:
                # TODO Remove player from the room
                # TODO If the room no longer has players, remove room
                break
            async with broadcast.subscribe(channel=room.code) as subscriber:
                async for event in subscriber:
                    yield json.dumps(event.message)

    return EventSourceResponse(streamRoomActivity())


@app.put("/rooms/{room_code}/status/0")
async def close_room_lobby(
    room_code: str,
    playerAndRoom=Depends(get_current_player_and_room),
    db: Session = Depends(get_db),
):
    currentPlayer, room = playerAndRoom
    if room_code != room.code or currentPlayer != room.owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )

    # Check that the room_code is actually in the "lobby" / available
    availableRoom = crud.get_available_room(db, room_code)
    if availableRoom is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room does not exist or already closed.",
        )

    crud.close_room(db, room_code=room_code)
    await broadcast.publish(channel=room_code, message=CLOSE_ROOM_COMMAND)


@app.post("/rooms", response_model=schemas.Room)
def create_room(
    response: Response, room_owner: str = Form(...), db: Session = Depends(get_db),
):
    while True:
        room_code = GenerateRoomCode()
        room = crud.get_room(db, room_code)
        if not room:
            break

    # TODO validate player/room_owner only contain alphanumeric characters.
    # We use | and , to represent a dice roll entry: [PLAYER]|[THREE,DICE,ROLL]
    # so if player has those characters, it could mess up what the API returns
    # ^^^ Make a TEST out of this: When API receives non-alphanumeric, API
    # should return a 400.

    roomSchema = schemas.RoomCreate(code=room_code, owner=room_owner)
    room = crud.create_room(db=db, roomSchema=roomSchema)
    roomPlayerSchema = schemas.RoomPlayer(room_code=room.code, player=room.owner)
    crud.add_room_player(
        db, room_player=roomPlayerSchema,
    )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = CreateAccessToken(
        data={"sub": room_owner, "dicery_room": room_code},
        expires_delta=access_token_expires,
    )
    response.set_cookie(key=API_KEY_COOKIE_NAME, value=f"{access_token}", httponly=True)

    return room


@app.get("/lobby/{room_code}")
async def join_lobby(
    room_code: str,
    req: Request,
    playerAndRoom=Depends(get_current_player_and_room),
    db: Session = Depends(get_db),
):
    player, room = playerAndRoom
    if room.code != room_code:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )

    async def streamLobbyActivity():
        players = crud.get_room_players(db, room.code)
        yield json.dumps(",".join(players))
        while True:
            disconnected = await req.is_disconnected()
            if disconnected:
                # TODO remove player from the room? What if they're exiting
                # the lobby, to ENTER the room?
                # TODO have a lobby_players table?
                break
            async with broadcast.subscribe(channel=room.code) as subscriber:
                async for event in subscriber:
                    msg = event.message
                    yield json.dumps(msg)

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

    # TODO validate player only contain alphanumeric characters.
    # We use | and , to represent a dice roll entry: [PLAYER]|[THREE,DICE,ROLL]
    # so if player has those characters, it could mess up what the API returns
    # ^^^ Make a TEST out of this: When API receives non-alphanumeric, API
    # should return a 400.
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

    response.set_cookie(key=API_KEY_COOKIE_NAME, value=f"{access_token}", httponly=True)

    room_player_schema = schemas.RoomPlayer(room_code=room_code, player=player)
    crud.add_room_player(db, room_player=room_player_schema)
    await broadcast.publish(channel=room_code, message=player)

    return room
