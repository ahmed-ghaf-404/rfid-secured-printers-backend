from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from models import Note

router = APIRouter()

class NoteRequest(BaseModel):
    content: str

class NoteResponse(BaseModel):
    id: int
    content: str

    class Config:
        orm_mode = True

@router.post("/add", response_model=NoteResponse)
def add_note(request: NoteRequest, db: Session = Depends(get_db)):
    new_note = Note(content=request.content)
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return new_note

@router.get("/", response_model=list[NoteResponse])
def get_notes(db: Session = Depends(get_db)):
    notes = db.query(Note).all()
    return notes if notes else []  # Ensure response is always an array

@router.delete("/{note_id}")
def delete_note(note_id: int, db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(note)
    db.commit()
    return {"message": f"Note {note_id} deleted successfully"}
