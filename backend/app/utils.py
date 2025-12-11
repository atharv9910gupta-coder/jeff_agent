# app/utils.py
import io
from typing import Optional
# placeholder for file parsing libs like pdfplumber, textract, tika etc.
def extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    # Very simple fallback: if text file, decode; else return stub
    try:
        if filename.endswith((".txt", ".md")):
            return file_bytes.decode("utf-8", errors="ignore")
        # Implement PDF/DOCX extraction on demand if you add pdfplumber / python-docx
    except Exception:
        pass
    return "[binary file content omitted]"

