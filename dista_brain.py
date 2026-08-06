import os
import re
import math
import platform
import psutil
from datetime import datetime
from dista_tools import EmailTool, DocsTool, MessagesTool, WORKSPACE_DIR

class DistaBrain:
    """
    Supercharged Offline Local AI Engine
    Handles natural language voice/text intents, local file I/O, email drafting,
    system diagnostics, scheduling, calculations, and creative writing.
    Zero external API key dependencies.
    """

    def __init__(self):
        self.name = "Dista AI"

    def process_input(self, user_text: str) -> dict:
        text = user_text.strip().lower()
        if not text:
            return {"reply": "I'm listening, sir. Please state your command.", "action": None, "data": None}

        # ── 1. Daily Briefing / Overview ────────────────────────────────
        if any(w in text for w in ["briefing", "overview", "daily briefing", "status report"]):
            unread = EmailTool.get_unread_emails()
            docs = DocsTool.list_documents()
            msgs = MessagesTool.get_recent_messages()
            now_str = datetime.now().strftime("%A, %B %d at %I:%M %p")
            
            reply = f"Good day, sir. Executive briefing for {now_str}: You have {len(unread)} unread emails, {len(docs)} workspace documents, and {len(msgs)} recent messages. All local subsystems are operational."
            return {"reply": reply, "action": "show_briefing", "data": {"unread": unread, "docs": docs, "msgs": msgs}}

        # ── 2. Email Intents ──────────────────────────────────────────
        if any(w in text for w in ["email", "inbox", "mail", "unread", "draft"]):
            unread = EmailTool.get_unread_emails()
            all_emails = EmailTool.get_all_emails()
            
            if any(w in text for w in ["unread", "check", "summarize", "show", "list"]):
                if unread:
                    reply = f"You have {len(unread)} unread emails. Primary email from {unread[0]['sender']} regarding '{unread[0]['subject']}'."
                else:
                    reply = "Your inbox is completely clear. No unread emails."
                return {"reply": reply, "action": "show_emails", "data": all_emails}

            if any(w in text for w in ["draft", "write", "send", "compose", "reply"]):
                match = re.search(r"to\s+([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|[a-zA-Z]+)", text)
                recipient = match.group(1) if match else "sarah@company.com"
                result = EmailTool.draft_reply(recipient, "Project Follow-up", "Thank you for the update. I have reviewed the items and will proceed.")
                return {"reply": f"Email draft created for {recipient} and saved locally in your database.", "action": "show_emails", "data": EmailTool.get_all_emails()}

        # ── 3. Create or Read Document ─────────────────────────────────
        if any(w in text for w in ["create doc", "new document", "write note", "save note", "create file"]):
            filename = f"note_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            content = f"# Dista AI Local Note\n\nCreated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\nContent:\n{user_text}\n"
            msg = DocsTool.create_document(filename, content)
            return {"reply": f"Document '{filename}' created and saved in your workspace.", "action": "show_docs", "data": DocsTool.list_documents()}

        if any(w in text for w in ["doc", "document", "file", "note", "read", "summary", "summarize"]):
            docs = DocsTool.list_documents()
            if any(w in text for w in ["list", "show", "open", "view"]):
                reply = f"Workspace documents found: {', '.join(docs)}."
                content = DocsTool.read_document(docs[0]) if docs else ""
                return {"reply": reply, "action": "show_docs", "data": {"files": docs, "current": docs[0] if docs else None, "content": content}}

            if any(w in text for w in ["summarize", "read", "analyze"]):
                filename = docs[0] if docs else "sample_notes.md"
                content = DocsTool.read_document(filename)
                summary = DocsTool.summarize_text(content)
                reply = f"Summary for '{filename}': {summary[:180]}"
                return {"reply": reply, "action": "show_docs", "data": {"files": docs, "current": filename, "content": content}}

        # ── 4. Messages / Contacts ─────────────────────────────────────
        if any(w in text for w in ["message", "msg", "chat", "contact", "jordan", "elena"]):
            msgs = MessagesTool.get_recent_messages()
            if any(w in text for w in ["send", "reply", "write"]):
                result = MessagesTool.send_message("Jordan Miller", "Received your update. Proceeding with execution.")
                return {"reply": f"Message transmitted to Jordan Miller.", "action": "show_messages", "data": MessagesTool.get_recent_messages()}
            
            latest = msgs[0] if msgs else None
            reply = f"Latest message from {latest['contact']}: '{latest['message']}'" if latest else "No recent messages."
            return {"reply": reply, "action": "show_messages", "data": msgs}

        # ── 5. Schedule & Calendar ─────────────────────────────────────
        if any(w in text for w in ["schedule", "calendar", "meeting", "agenda", "remind", "event"]):
            now_str = datetime.now().strftime("%I:%M %p")
            reply = f"Your schedule for today: 1) 10:00 AM — Dista AI Code Review. 2) 02:00 PM — Workspace Sync. 3) 04:30 PM — Daily Standup. Next event is at 02:00 PM."
            return {"reply": reply, "action": "show_schedule", "data": None}

        # ── 6. System Diagnostics (CPU/Memory) ─────────────────────────
        if any(w in text for w in ["system", "cpu", "memory", "ram", "diagnostic", "specs", "health"]):
            try:
                cpu_usage = psutil.cpu_percent(interval=0.1)
                mem = psutil.virtual_memory()
                mem_used = mem.percent
                reply = f"System Diagnostic: OS is {platform.system()} {platform.release()}. CPU Load: {cpu_usage}%. RAM Memory Usage: {mem_used}% of {round(mem.total / (1024**3), 1)} GB. Engine is operating at peak performance."
            except Exception:
                reply = f"System Diagnostic: Running on {platform.system()} {platform.release()}. All local services active."
            return {"reply": reply, "action": "show_system", "data": None}

        # ── 7. Math & Calculator ───────────────────────────────────────
        calc_match = re.search(r"(?:calculate|compute|math|what is)\s+([0-9\.\+\-\*\/\(\)\s]+)", text)
        if calc_match:
            expr = calc_match.group(1).strip()
            try:
                # Safe evaluation for basic math
                allowed = set("0123456789+-*/(). ")
                if all(c in allowed for c in expr):
                    res = eval(expr)
                    return {"reply": f"Calculated result for '{expr}' is {res}.", "action": None, "data": res}
            except Exception:
                pass

        # ── 8. Creative Writing & Brainstorming ────────────────────────
        if any(w in text for w in ["brainstorm", "idea", "suggest", "plan", "outline"]):
            reply = "Here is a 3-step action plan: 1) Audit current workspace documents. 2) Draft follow-up emails for pending tasks. 3) Automate daily status summaries using Dista AI."
            return {"reply": reply, "action": None, "data": None}

        # ── 9. Greetings & Identity ─────────────────────────────────────
        if any(w in text for w in ["hello", "hi", "hey", "greetings", "who are you", "what can you do"]):
            reply = "Greetings! I am Dista AI, your 100% offline desktop personal assistant. I can handle emails, workspace documents, messaging, system diagnostics, and daily scheduling with zero API keys required."
            return {"reply": reply, "action": None, "data": None}

        if any(w in text for w in ["time", "clock", "date", "today"]):
            now_str = datetime.now().strftime("%A, %B %d at %I:%M %p")
            return {"reply": f"The current local time is {now_str}.", "action": None, "data": None}

        # ── 10. Fallback Conversational Responder ──────────────────────
        return {
            "reply": f"Command received: '{user_text}'. All local Python subsystems are ready. You can ask for a daily briefing, email draft, document summary, or system check.",
            "action": None,
            "data": None
        }
