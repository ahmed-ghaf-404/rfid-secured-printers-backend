from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from models import User

router = APIRouter()

class RFIDLoginRequest(BaseModel):
    rfid_uid: str

class UserResponse(BaseModel):
    id: int
    name: str
    rfid_uid: str

    class Config:
        orm_mode = True

class UserCreateRequest(BaseModel):
    rfid_uid: str
    name: str

@router.post("/rfid-login")
def rfid_login(request: RFIDLoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.rfid_uid == request.rfid_uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "message": "Login successful",
        "user": {
            "id": user.id,
            "name": user.name,
            "rfid_uid": user.rfid_uid
        }
    }

@router.get("/", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@router.post("/add")
def add_user(request: UserCreateRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.rfid_uid == request.rfid_uid).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="RFID UID already exists")
    new_user = User(
        rfid_uid=request.rfid_uid,
        name=request.name
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User added successfully", "user": new_user.name}

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": f"User {user.name} deleted successfully"}
