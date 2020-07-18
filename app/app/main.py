from fastapi import FastAPI, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import SessionLocal
from .utils import GenerateRoomCode
from . import crud, schemas

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


@app.post("/lobby/{room_code}")
async def enter_lobby(req: Request, room_code, db: Session = Depends(get_db)):
    room = crud.get_available_room(db=db, room_code=room_code)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")