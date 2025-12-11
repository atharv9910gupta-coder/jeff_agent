from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .config import FRONTEND_ORIGINS
from .agent import run_agent
from .auth import create_access_token, hash_password, verify_password, decode_token
from .db import SessionLocal, engine
from . import models

models.Base.metadata.create_all(bind=engine)  # create tables

app = FastAPI(title="JEFF Agent Backend")

origins = [o.strip() for o in (FRONTEND_ORIGINS or "*").split(",")]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# --- auth endpoints (very basic) ---
class SignupIn(BaseModel):
    email: str
    password: str

@app.post("/api/v1/auth/signup")
def signup(payload: SignupIn):
    db = SessionLocal()
    hashed = hash_password(payload.password)
    user = models.User(email=payload.email, hashed_password=hashed)
    db.add(user); db.commit()
    token = create_access_token({"sub": payload.email})
    return {"access_token": token}

class SigninIn(BaseModel):
    email: str
    password: str

@app.post("/api/v1/auth/signin")
def signin(payload: SigninIn):
    db = SessionLocal()
    u = db.query(models.User).filter(models.User.email==payload.email).first()
    if not u or not verify_password(payload.password, u.hashed_password):
        raise HTTPException(401, "Invalid credentials")
    token = create_access_token({"sub": u.email})
    return {"access_token": token}

# --- chat endpoint ---
class Ask(BaseModel):
    message: str
    session_id: str | None = "default"

@app.post("/api/v1/ask")
def ask(payload: Ask):
    reply = run_agent(payload.message)
    return {"response": reply}

# tickets, email, sms endpoints — wrap the functions in tools/agent
@app.post("/api/v1/tickets")
def create_ticket(title: str = Form(...), description: str = Form(...)):
    db = SessionLocal()
    t = models.Ticket(title=title, description=description)
    db.add(t); db.commit(); db.refresh(t)
    return {"ticket": {"id": t.id, "title": t.title}}

@app.get("/api/v1/tickets")
def list_tickets():
    db = SessionLocal()
    rows = db.query(models.Ticket).order_by(models.Ticket.created_at.desc()).all()
    return {"tickets": [{"id":r.id,"title":r.title,"status":r.status} for r in rows]}

# file upload endpoint (extract text, store to memory)
@app.post("/api/v1/upload-file")
async def upload_file(session_id: str = Form("default"), file: UploadFile = File(...)):
    from .file_handler import extract_text_auto
    content = await file.read()
    text = extract_text_auto(file.filename, content)
    # store to memory table — simple approach omitted here for brevity
    return {"ok": True, "text_preview": text[:200]}

