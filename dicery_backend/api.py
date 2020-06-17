from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"])

@app.get("/")
async def GetHome():
    return "Hello World!"

@app.post("/rooms")
async def create_rooms(room_owner: str = Form(...)):
    return room_owner
