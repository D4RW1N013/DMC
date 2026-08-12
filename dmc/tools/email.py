import email
import imaplib
import os
from email.header import decode_header
from ..models import Tool

def _decode(value):
    if not value:
        return ""
    parts = decode_header(value)
    out = []
    for text, enc in parts:
        if isinstance(text, bytes):
            out.append(text.decode(enc or "utf-8", errors="replace"))
        else:
            out.append(text)
    return "".join(out)

def _body(msg):
    if msg.is_multipart():
        parts = []
        for part in msg.walk():
            if part.get_content_type() == "text/plain" and "attachment" not in str(part.get("Content-Disposition")):
                payload = part.get_payload(decode=True)
                if payload:
                    parts.append(payload.decode(part.get_content_charset() or "utf-8", errors="replace"))
        return "\n".join(parts)
    payload = msg.get_payload(decode=True)
    return payload.decode(msg.get_content_charset() or "utf-8", errors="replace") if payload else ""

def _connect():
    host = os.getenv("DMC_IMAP_HOST")
    port = int(os.getenv("DMC_IMAP_PORT", "993"))
    user = os.getenv("DMC_EMAIL_ADDRESS")
    password = os.getenv("DMC_EMAIL_PASSWORD")
    if not all([host, user, password]):
        raise RuntimeError("Email is not configured. Set DMC_IMAP_HOST, DMC_EMAIL_ADDRESS and DMC_EMAIL_PASSWORD in .env.")
    box = imaplib.IMAP4_SSL(host, port)
    box.login(user, password)
    box.select("INBOX")
    return box

def register(registry):
    def recent_emails(limit=20):
        box = _connect()
        try:
            status, data = box.search(None, "ALL")
            ids = data[0].split()[-limit:]
            rows = []
            for mid in reversed(ids):
                status, msg_data = box.fetch(mid, "(RFC822)")
                raw = msg_data[0][1]
                msg = email.message_from_bytes(raw)
                rows.append(
                    f"ID: {mid.decode()}\n"
                    f"DATE: {_decode(msg.get('Date'))}\n"
                    f"FROM: {_decode(msg.get('From'))}\n"
                    f"SUBJECT: {_decode(msg.get('Subject'))}\n"
                    f"BODY:\n{_body(msg)[:5000]}"
                )
            return "\n\n--- EMAIL ---\n\n".join(rows)
        finally:
            try:
                box.logout()
            except Exception:
                pass

    registry.register(Tool(
        "recent_emails",
        "Read recent emails from the configured IMAP inbox. Use this to summarize and prioritize email.",
        {"type": "object", "properties": {"limit": {"type": "integer", "minimum": 1, "maximum": 100}}, "required": ["limit"]},
        recent_emails))
