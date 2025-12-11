# app/main.py
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.config import settings
from app.db import get_db, Base, engine
from app import models, schemas, auth, agent, tools, utils
from datetime import timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import uvicorn

# Create DB tables (simple init - use Alembic for production)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="JEFF Customer Support - Backend")

origins = [o.strip() for o in (settings.FRONTEND_ORIGINS or "*").split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = auth.decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid auth")
    user = db.query(models.User).filter(models.User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/auth/register", response_model=schemas.UserOut)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = auth.hash_password(user_in.password)
    user = models.User(email=user_in.email, hashed_password=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.post("/auth/token", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Bad credentials")
    token = auth.create_access_token({"user_id": user.id}, expires_delta=timedelta(minutes=settings.JWT_EXPIRE_MINUTES))
    return {"access_token": token, "token_type":"bearer"}

# Chat endpoint
@app.post("/chat")
def chat(message: str = Body(..., embed=True), ticket_id: int = Body(None), current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Build history
    history_db = []
    if ticket_id:
        ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
        if not ticket:
            raise HTTPException(404, "Ticket not found")
        for m in ticket.messages:
            history_db.append({"role": m.role, "content": m.content})

    reply = agent.chat_reply(message, history=history_db)
    # save message & reply
    user_msg = models.Message(role="user", content=message, user_id=current_user.id, ticket_id=ticket_id)
    agent_msg = models.Message(role="agent", content=reply, user_id=None, ticket_id=ticket_id)
    db.add_all([user_msg, agent_msg])
    db.commit()
    return {"reply": reply}

# Ticket crud
@app.post("/tickets", response_model=schemas.TicketOut)
def create_ticket(ticket_in: schemas.TicketCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    ticket = models.Ticket(title=ticket_in.title, description=ticket_in.description, owner_id=current_user.id)
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket

@app.get("/tickets", response_model=list[schemas.TicketOut])
def list_tickets(limit: int = 50, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Ticket).filter(models.Ticket.owner_id == current_user.id).order_by(models.Ticket.created_at.desc()).limit(limit).all()

# File upload endpoint
@app.post("/upload")
async def upload_file(file: UploadFile = File(...), current_user: models.User = Depends(get_current_user)):
    body = await file.read()
    text = utils.extract_text_from_file(body, file.filename)
    # Save as a message without ticket by default
    return {"filename": file.filename, "extracted_text": text}

# Admin: send email / SMS
@app.post("/admin/send_email")
def admin_send_email(to: str = Body(...), subject: str = Body(...), body: str = Body(...), current_user: models.User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(403, "Admins only")
    tools.send_email(to, subject, body)
    return {"status": "sent"}

@app.post("/admin/send_sms")
def admin_send_sms(to: str = Body(...), body: str = Body(...), current_user: models.User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(403, "Admins only")
    sid = tools.send_sms(to, body)
    return {"sid": sid}

# Health
@app.get("/health")
def health():
    return {"status": "ok"}

# Run with: uvicorn app.main:app --host 0.0.0.0 --port 8000
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

