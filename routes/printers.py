from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from models import Printer

router = APIRouter()

class PrinterCreateRequest(BaseModel):
    name: str

class PrinterResponse(BaseModel):
    id: int
    name: str
    status: str

    class Config:
        orm_mode = True

@router.get("/", response_model=list[PrinterResponse])
def get_printers(db: Session = Depends(get_db)):
    return db.query(Printer).all()

@router.post("/add")
def add_printer(request: PrinterCreateRequest, db: Session = Depends(get_db)):
    existing_printer = db.query(Printer).filter(Printer.name == request.name).first()
    if existing_printer:
        raise HTTPException(status_code=400, detail="Printer name already exists")
    new_printer = Printer(name=request.name, status="available")
    db.add(new_printer)
    db.commit()
    db.refresh(new_printer)
    return {"message": f"Printer {new_printer.name} registered successfully!"}
