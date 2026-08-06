import os
import sqlite3
from datetime import datetime

# Try loading PyMongo for MongoDB integration
try:
    import pymongo
    MONGO_AVAILABLE = True
except ImportError:
    MONGO_AVAILABLE = False

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "workspace", "dista_local_data.db")

class DistaDatabase:
    """
    Unified MongoDB & SQLite Persistence Layer
    Connects to local MongoDB (`mongodb://localhost:27017`) if available,
    or transparently falls back to local SQLite database.
    """

    def __init__(self):
        self.use_mongo = False
        self.mongo_client = None
        self.db = None

        if MONGO_AVAILABLE:
            try:
                mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
                self.mongo_client = pymongo.MongoClient(mongo_uri, serverSelectionTimeoutMS=1000)
                # Quick server ping check
                self.mongo_client.admin.command('ping')
                self.db = self.mongo_client["dista_ai_db"]
                self.use_mongo = True
                print("[Database] Successfully connected to MongoDB!")
            except Exception:
                self.use_mongo = False

        if not self.use_mongo:
            print("[Database] Using SQLite local persistence.")
            self._init_sqlite()

    def _init_sqlite(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
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
        cur.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender TEXT,
                message TEXT,
                timestamp TEXT
            )
        """)
        conn.commit()
        conn.close()

    def save_email(self, sender: str, subject: str, body: str, priority: str = "INFO", is_read: int = 0):
        timestamp = datetime.now().strftime("%Y-%m-%d %I:%M %p")
        if self.use_mongo:
            self.db.emails.insert_one({
                "sender": sender,
                "subject": subject,
                "body": body,
                "priority": priority,
                "timestamp": timestamp,
                "is_read": bool(is_read)
            })
        else:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO emails (sender, subject, body, priority, timestamp, is_read)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (sender, subject, body, priority, timestamp, is_read))
            conn.commit()
            conn.close()

    def get_emails(self, limit=10):
        if self.use_mongo:
            docs = list(self.db.emails.find().sort("_id", -1).limit(limit))
            return [
                {
                    "sender": d.get("sender", ""),
                    "subject": d.get("subject", ""),
                    "body": d.get("body", ""),
                    "priority": d.get("priority", "INFO"),
                    "timestamp": d.get("timestamp", "")
                }
                for d in docs
            ]
        else:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT sender, subject, body, priority, timestamp FROM emails ORDER BY id DESC LIMIT ?", (limit,))
            rows = cur.fetchall()
            conn.close()
            return [
                {"sender": r[0], "subject": r[1], "body": r[2], "priority": r[3], "timestamp": r[4]}
                for r in rows
            ]

    def save_chat(self, sender: str, message: str):
        timestamp = datetime.now().strftime("%I:%M %p")
        if self.use_mongo:
            self.db.chat_history.insert_one({
                "sender": sender,
                "message": message,
                "timestamp": timestamp
            })
        else:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("INSERT INTO chat_history (sender, message, timestamp) VALUES (?, ?, ?)", (sender, message, timestamp))
            conn.commit()
            conn.close()

db_engine = DistaDatabase()
