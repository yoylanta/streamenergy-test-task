from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db, init_db
from crud import create_note, get_notes, get_note_by_id, search_notes_by_tag
from pydantic import BaseModel
from typing import List
import uvicorn
import asyncio
from bot import start_bot
import logging

logging.basicConfig(level=logging.INFO)

app = FastAPI()

class NoteCreate(BaseModel):
    title: str
    content: str
    tags: List[str] = []

class NoteOut(BaseModel):
    id: int
    title: str
    content: str
    created_at: str
    updated_at: str

@app.post("/notes/", response_model=NoteOut)
def create_note_view(note: NoteCreate, db: Session = Depends(get_db)):
    logging.info(f"Received note data - Title: {note.title}, Content: {note.content}, Tags: {note.tags}")
    note_out = create_note(db, note.title, note.content, note.tags)
    note_out.created_at = note_out.created_at.strftime("%Y-%m-%d %H:%M:%S")
    note_out.updated_at = note_out.updated_at.strftime("%Y-%m-%d %H:%M:%S")
    logging.info(f"Note created with ID: {note_out.id}")
    return note_out 

@app.get("/notes/", response_model=List[NoteOut])
def read_notes(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    notes = get_notes(db, skip=skip, limit=limit)
    for note in notes:
        note.created_at = note.created_at.strftime("%Y-%m-%d %H:%M:%S")
        note.updated_at = note.updated_at.strftime("%Y-%m-%d %H:%M:%S")
    return notes

@app.get("/notes/{note_id}", response_model=NoteOut)
def read_note(note_id: int, db: Session = Depends(get_db)):
    note = get_note_by_id(db, note_id)
    note.created_at = note.created_at.strftime("%Y-%m-%d %H:%M:%S")
    note.updated_at = note.updated_at.strftime("%Y-%m-%d %H:%M:%S")
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@app.get("/notes/tag/{tag_name}", response_model=List[NoteOut])
def search_notes(tag_name: str, db: Session = Depends(get_db)):
    notes =  search_notes_by_tag(db, tag_name)
    for note in notes:
        note.created_at = note.created_at.strftime("%Y-%m-%d %H:%M:%S")
        note.updated_at = note.updated_at.strftime("%Y-%m-%d %H:%M:%S")
    return notes

async def start_fastapi():
    config = uvicorn.Config("main:app", host="0.0.0.0", port=8080, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

async def run_services():
     # Start FastAPI using uvicorn's Config and Server in an asynchronous way
    config = uvicorn.Config("main:app", host="0.0.0.0", port=8080, log_level="info")
    server = uvicorn.Server(config)
    
    bot_task = asyncio.create_task(start_bot())  # Start the bot
    fastapi_task = asyncio.create_task(server.serve())  # Start FastAPI

    await asyncio.gather(bot_task, fastapi_task)  # Run both concurrently

if __name__=="__main__":
    asyncio.run(run_services())