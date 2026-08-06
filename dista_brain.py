import os
import re
import math
import platform
from datetime import datetime
from dista_tools import EmailTool, DocsTool, MessagesTool, WORKSPACE_DIR
from dista_gmail import gmail_service
from dista_db import db_engine

# Try importing g4f for free unlimited local AI generation
try:
    import g4f
    from g4f.client import Client as G4FClient
    g4f_client = G4FClient()
    G4F_AVAILABLE = True
except Exception:
    G4F_AVAILABLE = False
    g4f_client = None

try:
    import psutil
except ImportError:
    psutil = None

class DistaBrain:
    """
    Supercharged Local AI Brain
    Combines Real Gmail Integration, MongoDB/SQLite DB, Local Document I/O,
    and G4F (GPT-4o) Free Unlimited AI Intelligence. Zero API key barriers.
    """

    def __init__(self):
        self.name = "Dista AI"

    def _call_g4f(self, user_query: str, system_prompt: str = "") -> str:
        """Query free G4F AI engine for rich, intelligent responses"""
        if not G4F_AVAILABLE or not g4f_client:
            return ""

        try:
            sys_msg = system_prompt or "You are Dista AI, a razor-sharp, helpful AI workspace assistant. Answer in 2-3 flowing, clear sentences without markdown headers."
            response = g4f_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": sys_msg},
                    {"role": "user", "content": user_query}
                ]
            )
            reply = response.choices[0].message.content
            if reply:
                return reply.strip()
        except Exception as e:
            print(f"[G4F Engine] Fallback notice: {e}")

        return ""

    def process_input(self, user_text: str) -> dict:
        text = user_text.strip().lower()
        if not text:
            return {"reply": "I'm online and listening, sir. State your command.", "action": None, "data": None}

        # Save user query to DB
        db_engine.save_chat("YOU", user_text)

        # ── 1. REAL GMAIL FETCH / CONFIG ────────────────────────────────
        if "connect gmail" in text or "configure gmail" in text or "set gmail" in text:
            return {
                "reply": "To monitor your real Gmail inbox, enter your Gmail Address and App Password in the Settings dialog.",
                "action": "show_gmail_config",
                "data": None
            }

        if any(w in text for w in ["real email", "real gmail", "my email", "check inbox", "live emails"]):
            if gmail_service.is_configured():
                real_unread = gmail_service.fetch_unread_emails(max_results=5)
                if real_unread:
                    top = real_unread[0]
                    reply = f"Connected to your Gmail! Found {len(real_unread)} unread emails. Latest email from {top['sender']}: '{top['subject']}'."
                    return {"reply": reply, "action": "show_emails", "data": real_unread}
                else:
                    return {"reply": "Connected to Gmail! Your inbox is clean with zero unread emails.", "action": "show_emails", "data": []}
            else:
                reply = "Gmail service is ready. To connect your live inbox, click 'Connect Gmail' or provide your Gmail address and 16-character App Password."
                return {"reply": reply, "action": "show_gmail_config", "data": None}

        # ── 2. REAL / DRAFT EMAIL CREATION & SENDING ───────────────────
        if any(w in text for w in ["send email to", "send real email", "mail to"]):
            match = re.search(r"to\s+([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", text)
            to_addr = match.group(1) if match else "test@example.com"
            res = gmail_service.send_real_email(to_addr, "Dista AI Transmission", f"Hello,\n\nSent automatically via Dista AI.\n\nQuery: {user_text}")
            reply = res["message"]
            return {"reply": reply, "action": "show_emails", "data": EmailTool.get_all_emails()}

        if any(w in text for w in ["email", "inbox", "mail", "unread", "draft"]):
            unread = EmailTool.get_unread_emails()
            all_emails = EmailTool.get_all_emails()
            
            if any(w in text for w in ["unread", "check", "summarize", "show", "list"]):
                if unread:
                    reply = f"You have {len(unread)} unread emails stored locally. Top message from {unread[0]['sender']} regarding '{unread[0]['subject']}'."
                else:
                    reply = "Your local inbox is clear."
                return {"reply": reply, "action": "show_emails", "data": all_emails}

            if any(w in text for w in ["draft", "write", "send", "compose"]):
                match = re.search(r"to\s+([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|[a-zA-Z]+)", text)
                recipient = match.group(1) if match else "sarah@company.com"
                
                # Use G4F AI to draft an intelligent body if available
                ai_draft = self._call_g4f(f"Draft a professional concise email reply regarding: {user_text}")
                body = ai_draft or "Thank you for the update. I have reviewed the details and will proceed."
                
                EmailTool.draft_reply(recipient, "Project Follow-up", body)
                db_engine.save_email(f"Me -> {recipient}", "Project Follow-up", body, "DRAFT")
                
                reply = f"Email draft created for {recipient}: '{body[:100]}...'"
                return {"reply": reply, "action": "show_emails", "data": EmailTool.get_all_emails()}

        # ── 3. DAILY BRIEFING ──────────────────────────────────────────
        if any(w in text for w in ["briefing", "overview", "daily briefing", "status report"]):
            unread = EmailTool.get_unread_emails()
            docs = DocsTool.list_documents()
            msgs = MessagesTool.get_recent_messages()
            now_str = datetime.now().strftime("%A, %B %d at %I:%M %p")
            
            reply = f"Good day, sir. Executive briefing for {now_str}: You have {len(unread)} unread emails, {len(docs)} workspace documents, and {len(msgs)} recent messages. MongoDB/SQLite database is active."
            return {"reply": reply, "action": "show_briefing", "data": {"unread": unread, "docs": docs, "msgs": msgs}}

        # ── 4. CREATE / READ DOCUMENTS ─────────────────────────────────
        if any(w in text for w in ["create doc", "new document", "write note", "save note", "create file"]):
            filename = f"note_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            content_ai = self._call_g4f(f"Write a brief markdown document outline for: {user_text}")
            content = content_ai or f"# Dista AI Note\n\nCreated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\nContent:\n{user_text}\n"
            
            DocsTool.create_document(filename, content)
            return {"reply": f"Document '{filename}' created and saved in your ./workspace/ folder.", "action": "show_docs", "data": DocsTool.list_documents()}

        if any(w in text for w in ["doc", "document", "file", "note", "read", "summary", "summarize"]):
            docs = DocsTool.list_documents()
            if any(w in text for w in ["list", "show", "open", "view"]):
                reply = f"Workspace documents found: {', '.join(docs)}."
                content = DocsTool.read_document(docs[0]) if docs else ""
                return {"reply": reply, "action": "show_docs", "data": {"files": docs, "current": docs[0] if docs else None, "content": content}}

            if any(w in text for w in ["summarize", "read", "analyze"]):
                filename = docs[0] if docs else "sample_notes.md"
                content = DocsTool.read_document(filename)
                ai_sum = self._call_g4f(f"Summarize this document in 2 sentences:\n{content[:1500]}")
                summary = ai_sum or DocsTool.summarize_text(content)
                reply = f"Summary for '{filename}': {summary}"
                return {"reply": reply, "action": "show_docs", "data": {"files": docs, "current": filename, "content": content}}

        # ── 5. MESSAGES & CONTACTS ─────────────────────────────────────
        if any(w in text for w in ["message", "msg", "chat", "contact", "jordan", "elena"]):
            msgs = MessagesTool.get_recent_messages()
            if any(w in text for w in ["send", "reply", "write"]):
                res = MessagesTool.send_message("Jordan Miller", "Received your message. Dista AI has processed it.")
                return {"reply": "Message transmitted to Jordan Miller and logged in your database.", "action": "show_messages", "data": MessagesTool.get_recent_messages()}
            
            latest = msgs[0] if msgs else None
            reply = f"Latest message from {latest['contact']}: '{latest['message']}'" if latest else "No recent messages."
            return {"reply": reply, "action": "show_messages", "data": msgs}

        # ── 6. SYSTEM DIAGNOSTIC (CPU / RAM / DB) ──────────────────────
        if any(w in text for w in ["system", "cpu", "memory", "ram", "diagnostic", "specs", "db", "database"]):
            db_type = "MongoDB" if db_engine.use_mongo else "SQLite"
            if psutil:
                cpu_v = psutil.cpu_percent(interval=0.1)
                mem_v = psutil.virtual_memory().percent
                reply = f"System Status: OS {platform.system()} {platform.release()} | CPU: {cpu_v}% | RAM: {mem_v}% | Storage Engine: {db_type}. All systems operational."
            else:
                reply = f"System Status: OS {platform.system()} | Storage Engine: {db_type}. All systems operational."
            return {"reply": reply, "action": "show_system", "data": None}

        # ── 7. MATH CALCULATOR ─────────────────────────────────────────
        calc_match = re.search(r"(?:calculate|compute|math|what is)\s+([0-9\.\+\-\*\/\(\)\s]+)", text)
        if calc_match:
            expr = calc_match.group(1).strip()
            try:
                allowed = set("0123456789+-*/(). ")
                if all(c in allowed for c in expr):
                    res = eval(expr)
                    return {"reply": f"Calculated result for '{expr}' is {res}.", "action": None, "data": res}
            except Exception:
                pass

        # ── 8. AI INTELLIGENCE GENERATOR (G4F GPT-4o) ─────────────────
        ai_reply = self._call_g4f(user_text)
        if ai_reply:
            db_engine.save_chat("DISTA AI", ai_reply)
            return {"reply": ai_reply, "action": None, "data": None}

        # ── 9. FALLBACK RESPONDER ──────────────────────────────────────
        fallback = f"I have received your command: '{user_text}'. Subsystems (Gmail, Docs, Messages, Database) are active."
        db_engine.save_chat("DISTA AI", fallback)
        return {"reply": fallback, "action": None, "data": None}
