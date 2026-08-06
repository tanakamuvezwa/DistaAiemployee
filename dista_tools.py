import os
import json
import sqlite3
from datetime import datetime

# Workspace directory for Docs
WORKSPACE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "workspace")
os.makedirs(WORKSPACE_DIR, exist_ok=True)

DB_PATH = os.path.join(WORKSPACE_DIR, "dista_local_data.db")


def init_db():
    """Initialize local SQLite DB for Emails & Messages"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Emails Table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            subject TEXT,
            body TEXT,
            priority TEXT,
            timestamp TEXT,
            is_read INTEGER DEFAULT 0
        )
    """)
    
    # Messages Table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact TEXT,
            message TEXT,
            direction TEXT,
            timestamp TEXT
        )
    """)
    
    # Insert initial mock data if empty
    cur.execute("SELECT COUNT(*) FROM emails")
    if cur.fetchone()[0] == 0:
        cur.executemany("""
            INSERT INTO emails (sender, subject, body, priority, timestamp, is_read)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [
            ("sarah@company.com", "Project Status Update Required", "Hi! Please send over the weekly report for Dista AI before 5 PM today.", "HIGH", "10:30 AM", 0),
            ("alex@techcorp.io", "Quarterly Roadmap Meeting", "Are you free tomorrow at 2 PM to review the 2030 product vision deck?", "MEDIUM", "Yesterday", 1),
            ("newsletter@dev.org", "Top Python & AI Libraries of 2026", "Discover PyQt6, Whisper, and local LLM frameworks taking over desktop dev.", "LOW", "2 days ago", 1),
        ])

    cur.execute("SELECT COUNT(*) FROM messages")
    if cur.fetchone()[0] == 0:
        cur.executemany("""
            INSERT INTO messages (contact, message, direction, timestamp)
            VALUES (?, ?, ?, ?)
        """, [
            ("Jordan Miller", "Hey! Is the Dista AI local prototype ready?", "INCOMING", "11:15 AM"),
            ("Jordan Miller", "Yeah, it runs 100% offline with zero API keys!", "OUTGOING", "11:16 AM"),
            ("Elena Vance", "Did you check the sample markdown doc in workspace?", "INCOMING", "09:40 AM"),
        ])

    conn.commit()
    conn.close()

# Initialize DB on load
init_db()


class EmailTool:
    """Local Email Handler"""

    @staticmethod
    def get_unread_emails():
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT id, sender, subject, body, priority, timestamp FROM emails WHERE is_read = 0 ORDER BY id DESC")
        rows = cur.fetchall()
        conn.close()

        return [
            {"id": r[0], "sender": r[1], "subject": r[2], "body": r[3], "priority": r[4], "timestamp": r[5]}
            for r in rows
        ]

    @staticmethod
    def get_all_emails():
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT id, sender, subject, body, priority, timestamp, is_read FROM emails ORDER BY id DESC")
        rows = cur.fetchall()
        conn.close()

        return [
            {"id": r[0], "sender": r[1], "subject": r[2], "body": r[3], "priority": r[4], "timestamp": r[5], "is_read": r[6]}
            for r in rows
        ]

    @staticmethod
    def draft_reply(to_email: str, subject: str, message: str) -> str:
        timestamp = datetime.now().strftime("%I:%M %p")
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO emails (sender, subject, body, priority, timestamp, is_read)
            VALUES (?, ?, ?, 'DRAFT', ?, 1)
        """, (f"Me -> {to_email}", f"Re: {subject}", message, timestamp))
        conn.commit()
        conn.close()
        return f"Draft saved locally for {to_email} with subject 'Re: {subject}'."


class DocsTool:
    """Local Document Handler (.txt, .md files in ./workspace/)"""

    @staticmethod
    def list_documents():
        files = [f for f in os.listdir(WORKSPACE_DIR) if f.endswith(('.txt', '.md', '.markdown', '.json'))]
        if not files:
            # Create a default sample markdown file
            sample_path = os.path.join(WORKSPACE_DIR, "sample_notes.md")
            with open(sample_path, "w", encoding="utf-8") as f:
                f.write("# Dista AI Project Overview\n\n- Running 100% offline in Python\n- Pixel-art humanoid avatar with 30FPS glow\n- Pyttsx3 TTS voice synthesis\n- Retro-modern dark mode with orange highlights.\n")
            files = ["sample_notes.md"]
        return files

    @staticmethod
    def read_document(filename: str) -> str:
        filepath = os.path.join(WORKSPACE_DIR, filename)
        if not os.path.exists(filepath):
            return f"Error: Document '{filename}' not found."
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"

    @staticmethod
    def create_document(filename: str, content: str) -> str:
        if not filename.endswith(('.txt', '.md')):
            filename += ".md"
        filepath = os.path.join(WORKSPACE_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Document '{filename}' created successfully in ./workspace/"

    @staticmethod
    def summarize_text(text: str) -> str:
        """Local extractive rule-based summarizer"""
        lines = [line.strip() for line in text.splitlines() if line.strip() and not line.startswith('#')]
        if not lines:
            return "Document is empty."
        key_lines = lines[:4]
        return "• " + "\n• ".join(key_lines)


class MessagesTool:
    """Local Messages & Inbox Handler"""

    @staticmethod
    def get_recent_messages():
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT contact, message, direction, timestamp FROM messages ORDER BY id DESC LIMIT 10")
        rows = cur.fetchall()
        conn.close()
        return [
            {"contact": r[0], "message": r[1], "direction": r[2], "timestamp": r[3]}
            for r in rows
        ]

    @staticmethod
    def send_message(contact: str, message: str) -> str:
        timestamp = datetime.now().strftime("%I:%M %p")
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO messages (contact, message, direction, timestamp)
            VALUES (?, ?, 'OUTGOING', ?)
        """, (contact, message, timestamp))
        conn.commit()
        conn.close()
        return f"Message sent to {contact}."
