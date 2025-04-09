from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from database import get_db
from models import PrintJob, User
from pydantic import BaseModel
from pathlib import Path
import platform
import subprocess
import sys

# Conditional Windows-only imports
if platform.system() == "Windows":
    import win32print
    import win32api

UPLOAD_DIR = Path("uploaded_files")
UPLOAD_DIR.mkdir(exist_ok=True)

router = APIRouter()

class PrintJobResponse(BaseModel):
    id: int
    user_id: int
    user_name: str
    status: str
    timestamp: str

    class Config:
        orm_mode = True


@router.get("/history", response_model=list[PrintJobResponse])
def get_print_history(db: Session = Depends(get_db)):
    jobs = db.query(PrintJob).join(PrintJob.user).all()

    return [
        PrintJobResponse(
            id=job.id,
            user_id=job.user_id,
            user_name=job.user.name,
            status=job.status,
            timestamp=job.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        )
        for job in jobs
    ]


@router.post("/send")
def send_print_job(
    user_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Save uploaded file
    file_location = UPLOAD_DIR / file.filename
    with open(file_location, "wb") as f:
        f.write(file.file.read())

    system_type = platform.system()

    try:
        if system_type == "Windows":
            printer_name = win32print.GetDefaultPrinter()
            win32api.ShellExecute(
                0,
                "print",
                str(file_location),
                None,
                ".",
                0
            )
        elif system_type in ["Linux", "Darwin"]:  # Darwin = macOS
            subprocess.run(["lpr", str(file_location)], check=True)
        else:
            raise Exception(f"Unsupported OS: {system_type}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Print error: {e}")

    # Log the job
    job = PrintJob(user_id=user.id)
    db.add(job)
    db.commit()

    return {
        "message": f"File '{file.filename}' printed for user {user.name} on {system_type}"
    }
