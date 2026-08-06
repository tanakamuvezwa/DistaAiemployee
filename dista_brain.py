import re
from datetime import datetime
from dista_tools import EmailTool, DocsTool, MessagesTool

class DistaBrain:
    """
    Offline Local AI Command Engine
    Processes user text/voice inputs, matches intents, interacts with local tools,
    and returns concise conversational responses. Zero external API keys needed.
    """

    def __init__(self):
        self.name = "Dista"

    def process_input(self, user_text: str) -> dict:
        """
        Processes user query and returns dict:
        {
            "reply": str,           # Spoken / displayed text reply
            "action": str or None,  # Action code (e.g. "show_emails", "show_docs", "show_messages")
            "data": any             # Optional payload for UI update
        }
        """
        text = user_text.strip().lower()
        if not text:
            return {"reply": "I didn't catch that. How can I assist you?", "action": None, "data": None}

        # ── 1. Email Intents ──────────────────────────────────────────
        if any(w in text for w in ["email", "inbox", "mail", "unread"]):
            unread = EmailTool.get_unread_emails()
            all_emails = EmailTool.get_all_emails()
            if "unread" in text or "check" in text or "summarize" in text or "show" in text:
                if unread:
                    reply = f"You have {len(unread)} unread emails. Top email is from {unread[0]['sender']} regarding '{unread[0]['subject']}'."
                else:
                    reply = "Your inbox is clear. No unread emails."
                return {"reply": reply, "action": "show_emails", "data": all_emails}

            if "draft" in text or "write" in text or "send" in text:
                # Extract potential recipient
                match = re.search(r"to\s+([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|[a-zA-Z]+)", text)
                recipient = match.group(1) if match else "sarah@company.com"
                result = EmailTool.draft_reply(recipient, "Follow up", "I will review this right away.")
                return {"reply": f"Draft created! {result}", "action": "show_emails", "data": all_emails}

        # ── 2. Document / Notes Intents ────────────────────────────────
        if any(w in text for w in ["doc", "document", "file", "note", "read", "summary", "summarize"]):
            docs = DocsTool.list_documents()
            if "list" in text or "show" in text or "open" in text or "view" in text:
                reply = f"Found {len(docs)} documents in your workspace: {', '.join(docs)}."
                content = DocsTool.read_document(docs[0]) if docs else ""
                return {"reply": reply, "action": "show_docs", "data": {"files": docs, "current": docs[0] if docs else None, "content": content}}

            if "summarize" in text or "read" in text:
                filename = docs[0] if docs else "sample_notes.md"
                content = DocsTool.read_document(filename)
                summary = DocsTool.summarize_text(content)
                reply = f"Here is the local summary for '{filename}': {summary[:160]}..."
                return {"reply": reply, "action": "show_docs", "data": {"files": docs, "current": filename, "content": content}}

        # ── 3. Messages / Inbox Intents ───────────────────────────────
        if any(w in text for w in ["message", "msg", "chat", "contact", "jordan", "elena"]):
            msgs = MessagesTool.get_recent_messages()
            if "send" in text or "reply" in text:
                result = MessagesTool.send_message("Jordan Miller", "Got it, thanks!")
                return {"reply": result, "action": "show_messages", "data": MessagesTool.get_recent_messages()}
            
            latest = msgs[0] if msgs else None
            reply = f"Recent message from {latest['contact']}: '{latest['message']}'" if latest else "No recent messages."
            return {"reply": reply, "action": "show_messages", "data": msgs}

        # ── 4. System / Time / Greetings ───────────────────────────────
        if any(w in text for w in ["hello", "hi", "hey", "greetings", "who are you"]):
            return {
                "reply": "Greetings! I am Dista AI, your local offline workspace assistant. I can handle emails, docs, and messages directly on your machine.",
                "action": None,
                "data": None
            }

        if any(w in text for w in ["time", "clock", "date", "today"]):
            now_str = datetime.now().strftime("%A, %B %d at %I:%M %p")
            return {"reply": f"The current local time is {now_str}.", "action": None, "data": None}

        if any(w in text for w in ["help", "what can you do", "commands"]):
            return {
                "reply": "You can ask me to: 1) Summarize or draft emails. 2) Read and summarize local docs. 3) Check or send messages. 4) Operate 100% offline via text or voice.",
                "action": None,
                "data": None
            }

        # ── 5. General Fallback ───────────────────────────────────────
        return {
            "reply": f"I processed your command: '{user_text}'. All local subsystems (Emails, Docs, Messages) are ready.",
            "action": None,
            "data": None
        }
