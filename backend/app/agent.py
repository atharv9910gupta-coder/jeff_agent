# app/agent.py
import requests
from app.config import settings
from typing import List, Dict, Any

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def ask_groq(messages: List[Dict[str,str]], model: str = None) -> Dict[str, Any]:
    """
    Send a chat request to Groq. `messages` should be a list of dicts:
    [{"role":"system","content":"..."}, {"role":"user","content":"..."}]
    """
    model_name = model or settings.GROQ_MODEL
    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": model_name,
        "messages": messages
    }
    resp = requests.post(GROQ_URL, headers=headers, json=body, timeout=60)
    try:
        data = resp.json()
    except Exception:
        return {"error": f"Invalid JSON from Groq {resp.text}", "status_code": resp.status_code}

    if resp.status_code != 200:
        return {"error": data.get("error", "Unknown error"), "status_code": resp.status_code}
    # Groq returns choices -> message -> content typical
    # adapt to different shapes defensively
    try:
        content = data["choices"][0]["message"]["content"]
        return {"content": content, "raw": data}
    except Exception:
        return {"error": "Unexpected response shape", "raw": data}

def build_system_prompt(system_instructions: str = None) -> List[Dict[str,str]]:
    base = [
        {"role":"system","content": "You are JEFF, a professional customer support assistant. Be concise, polite, and action-oriented."}
    ]
    if system_instructions:
        base.append({"role":"system", "content": system_instructions})
    return base

def chat_reply(user_message: str, history: List[Dict[str,str]] = None, system_instructions: str = None) -> str:
    messages = build_system_prompt(system_instructions)
    if history:
        messages.extend(history)
    messages.append({"role":"user","content": user_message})
    res = ask_groq(messages)
    if "content" in res:
        return res["content"]
    else:
        # fallback error
        return f"Agent error: {res.get('error','unknown')}"
