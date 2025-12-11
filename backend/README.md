# JEFF Agent - Backend (Ultra)

This is the FastAPI backend for the JEFF customer-support AI agent.

## Features
- Groq LLM (llama-3.1-8b-instant)
- JWT auth (signup/login)
- PostgreSQL ticket & message models
- Email (SMTP) + Twilio SMS
- File upload handler (text extraction placeholder)
- Admin endpoints
- Dockerized for hosting

## Run locally
1. Copy `.env.example` to `.env` and fill in secrets.
2. Create Postgres DB and set `DATABASE_URL`.
3. Build and run:
