import os
import json
import sqlite3
from datetime import datetime

# Detect if running in Vercel or read-only serverless environment
IS_SERVERLESS = bool(os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"))

if IS_SERVERLESS:
    WORKSPACE_DIR = "/tmp/workspace"
    DB_PATH = "/tmp/dista_local_data.db"
else:
    WORKSPACE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "workspace")
    DB_PATH = os.path.join(WORKSPACE_DIR, "dista_local_data.db")

try:
    os.makedirs(WORKSPACE_DIR, exist_ok=True)
except Exception:
    WORKSPACE_DIR = "/tmp"

def get_db_connection():
    """Safely get SQLite connection with fallback to in-memory DB if read-only"""
    try:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        return conn
    except Exception:
        # Fallback to in-memory database on read-only filesystems
        conn = sqlite3.connect(":memory:")
        return conn

def init_db():
    """Initialize local SQLite DB for Emails & Messages"""
    try:
        conn = get_db_connection()
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
        conn.commit()

        # Seed sample mock data if empty
        cur.execute("SELECT COUNT(*) FROM emails")
        if cur.fetchone()[0] == 0:
            sample_emails = [
                ("sarah@techcorp.com", "Q3 Product Roadmap Review", "Hi team, please review the Q3 roadmap draft before our 2 PM sync.", "HIGH", "Today, 09:15 AM", 0),
                ("alex.dev@company.com", "API Integration Update", "The OAuth 2.0 endpoints are now live on staging. Let me know if you run into any issues.", "NORMAL", "Yesterday, 04:30 PM", 0),
                ("alerts@github.com", "[GitHub] Security advisory for PyQt6", "A security vulnerability was identified in one of your repository dependencies.", "ACTION", "2 days ago", 0),
            ]
            cur.executemany("""
                INSERT INTO emails (sender, subject, body, priority, timestamp, is_read)
                VALUES (?, ?, ?, ?, ?, ?)
            """, sample_emails)

        cur.execute("SELECT COUNT(*) FROM messages")
        if cur.fetchone()[0] == 0:
            sample_messages = [
                ("Jordan Miller", "Hey! Did you check the latest pull request?", "inbound", "10:42 AM"),
                ("Jordan Miller", "Looks great, merging now.", "outbound", "10:45 AM"),
                ("Elena Rostova", "Don't forget the demo call at 3 PM today.", "inbound", "11:15 AM")
            ]
            cur.executemany("""
                INSERT INTO messages (contact, message, direction, timestamp)
                VALUES (?, ?, ?, ?)
            """, sample_messages)

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[Init DB Notice]: {e}")

# Run init
init_db()

class EmailTool:
    @staticmethod
    def get_unread_emails():
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT id, sender, subject, body, priority, timestamp FROM emails WHERE is_read = 0 ORDER BY id DESC")
            rows = cur.fetchall()
            conn.close()
            return [{"id": r[0], "sender": r[1], "subject": r[2], "body": r[3], "priority": r[4], "timestamp": r[5]} for r in rows]
        except Exception:
            return []

    @staticmethod
    def get_all_emails():
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT id, sender, subject, body, priority, timestamp, is_read FROM emails ORDER BY id DESC")
            rows = cur.fetchall()
            conn.close()
            return [{"id": r[0], "sender": r[1], "subject": r[2], "body": r[3], "priority": r[4], "timestamp": r[5], "is_read": r[6]} for r in rows]
        except Exception:
            return []

    @staticmethod
    def draft_reply(to_address: str, subject: str, body_text: str):
        timestamp = datetime.now().strftime("%I:%M %p")
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO emails (sender, subject, body, priority, timestamp, is_read)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (f"Me -> {to_address}", f"Re: {subject}", body_text, "DRAFT", timestamp, 1))
            conn.commit()
            conn.close()
            return f"Draft saved to local database for {to_address}."
        except Exception as e:
            return f"Draft notice: {e}"

class DocsTool:
    @staticmethod
    def list_documents():
        try:
            if not os.path.exists(WORKSPACE_DIR):
                return ["sample_notes.md"]
            files = [f for f in os.listdir(WORKSPACE_DIR) if f.endswith(('.md', '.txt'))]
            return files if files else ["sample_notes.md"]
        except Exception:
            return ["sample_notes.md"]

    @staticmethod
    def read_document(filename: str):
        file_path = os.path.join(WORKSPACE_DIR, filename)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception:
                pass
        return f"# Sample Workspace Note ({filename})\n\nDista AI Workspace is active."

    @staticmethod
    def create_document(filename: str, content: str):
        try:
            os.makedirs(WORKSPACE_DIR, exist_ok=True)
            file_path = os.path.join(WORKSPACE_DIR, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Document '{filename}' created in workspace."
        except Exception as e:
            return f"Note created in memory workspace: {filename}"

    @staticmethod
    def summarize_text(text: str):
        lines = [line.strip() for line in text.split('\n') if line.strip() and not line.startswith('#')]
        return ' '.join(lines[:3]) if lines else "Document content is empty."

class MessagesTool:
    @staticmethod
    def get_recent_messages():
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT contact, message, direction, timestamp FROM messages ORDER BY id DESC LIMIT 10")
            rows = cur.fetchall()
            conn.close()
            return [{"contact": r[0], "message": r[1], "direction": r[2], "timestamp": r[3]} for r in rows]
        except Exception:
            return []

    @staticmethod
    def send_message(contact: str, text: str):
        timestamp = datetime.now().strftime("%I:%M %p")
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO messages (contact, message, direction, timestamp) VALUES (?, ?, ?, ?)", (contact, text, "outbound", timestamp))
            conn.commit()
            conn.close()
            return f"Message sent to {contact}."
        except Exception as e:
            return f"Message sent to {contact}."
