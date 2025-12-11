import os, requests
from .config import GROQ_API_KEY, GROQ_MODEL
from typing import List, Dict
from .tools import send_email_smtp, send_sms_twilio

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def call_groq(messages: List[Dict], max_tokens:int=400, temperature:float=0.2):
    if not GROQ_API_KEY:
        return {"error": "GROQ_API_KEY not configured."}
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type":"application/json"}
    payload = {"model": GROQ_MODEL, "messages": messages, "max_tokens": max_tokens, "temperature": temperature}
    try:
        r = requests.post(GROQ_URL, json=payload, headers=headers, timeout=30)
        data = r.json()
        if "choices" in data:
            return {"text": data["choices"][0].get("message", {}).get("content", "")}
        return {"error": "Unexpected Groq response."}
    except Exception as e:
        return {"error": str(e)}

# Tool router: simple rule-based calls — extend later
def run_agent(user_text: str, history: List[Dict]=None):
    history = history or []
    system = {"role":"system","content":"You are JEFF, a professional AI assistant for business support. Use tools as requested by user."}
    messages = [system] + history + [{"role":"user","content": user_text}]
    # quick detection for tool calls
    lower = user_text.lower()
    if lower.startswith("email:"):
        # format: "email: to=foo@x.com; subject=...; body=..."
        try:
            _, rest = user_text.split(":",1)
            parts = {k.strip(): v.strip() for k,v in [p.split("=",1) for p in rest.split(";")]}
            ok, msg = send_email_smtp(parts.get("to"), parts.get("subject",""), parts.get("body",""))
            return f"Email tool result: {ok} - {msg}"
        except Exception as e:
            return f"Email tool parse error: {e}"
    if lower.startswith("sms:"):
        try:
            _, rest = user_text.split(":",1)
            to, body = rest.split(";",1)
            res = send_sms_twilio(to.strip(), body.strip())
            return f"SMS result: {res}"
        except Exception as e:
            return f"SMS tool parse error: {e}"

    # fallback to language model
    out = call_groq(messages)
    if "text" in out:
        return out["text"]
    return out.get("error","No response")

