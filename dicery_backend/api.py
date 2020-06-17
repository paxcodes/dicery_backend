from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware

from .utils import GenerateRoomCode

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"])

@app.get("/")
async def GetHome():
    return "Hello World!"

@app.post("/rooms")
async def create_rooms(room_owner: str = Form(...)):
    room_code = GenerateRoomCode()
    # TODO save room_code and room_owner in database
    return room_code
