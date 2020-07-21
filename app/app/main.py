from datetime import timedelta
from typing import Tuple

from fastapi import Depends, FastAPI, Form, HTTPException, Response
from fastapi import Security, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyCookie
from sqlalchemy.orm import Session

from jose import JWTError, jwt

from . import crud, schemas
from .config import settings
from .database import SessionLocal
from .utils import CreateAccessToken, GenerateRoomCode

ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", scheme_name="http")

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"])


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def get_home():
    return "Hello World!"


@app.post("/rooms", response_model=schemas.Room)
def create_room(room_owner: str = Form(...), db: Session = Depends(get_db)):
    while True:
        room_code = GenerateRoomCode()
        room = crud.get_room(db, room_code)
        if not room:
            break

    room = schemas.RoomCreate(code=room_code, owner=room_owner)
    return crud.create_room(db=db, room=room)


async def get_current_player_and_room(
    token: str = Depends(oauth2_scheme), db=Depends(get_db)
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


@app.get("/lobby/{room_code}")
async def join_lobby(token: str = Depends(oauth2_scheme)):
    # this will be an SSE connection
    raise NotImplementedError


@app.post("/token", response_model=schemas.Token)
async def validate_room_for_access_token(
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
    # TODO add player to the database so we can confirm later that the player
    # can submit/subscribe.
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = CreateAccessToken(
        data={"sub": player, "dicery_room": room_code},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}
