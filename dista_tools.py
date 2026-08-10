import os
import json
import sqlite3
import csv
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

        # Seed sample mock data only if empty
        cur.execute("SELECT COUNT(*) FROM emails")
        if cur.fetchone()[0] == 0:
            sample_emails = [
                ("sarah.jenkins@techcorp.com", "Q3 Strategic AI Integration & Budget Review", "Hi Tanaka,\n\nPlease review the attached Q3 roadmap and budget allocation spreadsheet. We need your sign-off before 5 PM today for production deployment.\n\nBest,\nSarah Jenkins", "HIGH", "09:15 AM", 0),
                ("alex.rivera@devops.org", "NVIDIA NIM & DeepSeek Latency Benchmark Live", "Hey Tanaka,\n\nThe multi-provider LLM latency benchmark report is complete. Llama 3.3 70B is clocking 142ms average response time.\n\nRegards,\nAlex", "NORMAL", "Yesterday, 04:30 PM", 0),
                ("security@github.com", "[Security Alert] New OAuth 2.0 Token Issued", "A new OAuth token was authorized for Dista AI Executive Assistant on your Google Account.", "ACTION", "2 days ago", 0),
            ]
            cur.executemany("""
                INSERT INTO emails (sender, subject, body, priority, timestamp, is_read)
                VALUES (?, ?, ?, ?, ?, ?)
            """, sample_emails)

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[Init DB Notice]: {e}")

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
    def add_email(sender: str, subject: str, body: str, priority: str = "NORMAL"):
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            timestamp = datetime.now().strftime("%I:%M %p")
            cur.execute("""
                INSERT INTO emails (sender, subject, body, priority, timestamp, is_read)
                VALUES (?, ?, ?, ?, ?, 0)
            """, (sender, subject, body, priority, timestamp))
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False

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

class DocsTool:
    @staticmethod
    def list_documents():
        try:
            if not os.path.exists(WORKSPACE_DIR):
                return []
            files = []
            for f in os.listdir(WORKSPACE_DIR):
                file_path = os.path.join(WORKSPACE_DIR, f)
                if os.path.isfile(file_path):
                    size = os.path.getsize(file_path)
                    mod_time = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d %H:%M")
                    ext = os.path.splitext(f)[1].lower()
                    doc_type = "Spreadsheet (CSV)" if ext == ".csv" else ("Markdown Note" if ext == ".md" else "Document")
                    files.append({"filename": f, "size": f"{size} B", "modified": mod_time, "type": doc_type})
            return files
        except Exception:
            return []

    @staticmethod
    def read_document(filename: str):
        file_path = os.path.join(WORKSPACE_DIR, filename)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                return f"Error reading document: {e}"
        return f"# File Not Found ({filename})"

    @staticmethod
    def create_document(filename: str, content: str):
        try:
            os.makedirs(WORKSPACE_DIR, exist_ok=True)
            file_path = os.path.join(WORKSPACE_DIR, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"[Create Doc Notice]: {e}")
            return False

    @staticmethod
    def create_spreadsheet(filename: str, rows_data: list):
        """Creates a CSV Excel spreadsheet file in workspace"""
        try:
            if not filename.endswith('.csv'):
                filename += '.csv'
            os.makedirs(WORKSPACE_DIR, exist_ok=True)
            file_path = os.path.join(WORKSPACE_DIR, filename)
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                for row in rows_data:
                    writer.writerow(row)
            return True
        except Exception as e:
            print(f"[Create CSV Notice]: {e}")
            return False

class MessagesTool:
    @staticmethod
    def get_messages():
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT id, contact, message, direction, timestamp FROM messages ORDER BY id DESC")
            rows = cur.fetchall()
            conn.close()
            return [{"id": r[0], "contact": r[1], "message": r[2], "direction": r[3], "timestamp": r[4]} for r in rows]
        except Exception:
            return []
