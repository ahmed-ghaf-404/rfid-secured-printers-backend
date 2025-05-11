from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import users, print_jobs
from database import engine, Base

app = FastAPI(title="RFID Secured Printers API", version="1.0")

# Allow frontend to access backend (CORS fix)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://192.168.0.139:3000"],  # React frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Include API routes
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(print_jobs.router, prefix="/api/print-jobs", tags=["Print Jobs"])

@app.get("/")
def home():
    return {"message": "Welcome to the RFID Secured Printers API"}
