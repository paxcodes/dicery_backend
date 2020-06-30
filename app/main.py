from fastapi import FastAPI, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import engine, SessionLocal
from .utils import GenerateRoomCode
from . import models, crud, schemas

# Create the database tables
# TODO use Alembic instead of creating the database tables here?
# See `alembic` directory of fullstack-fastapi-postgresql container
models.Base.metadata.create_all(bind=engine)

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