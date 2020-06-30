from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware

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
async def GetHome():
    return "Hello World!"


@app.post("/rooms")
async def create_rooms(room_owner: str = Form(...)):
    room_code = GenerateRoomCode()
    # TODO save room_code and room_owner in database
    return room_code
