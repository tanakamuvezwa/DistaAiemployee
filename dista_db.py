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
    Unified MongoDB Cloud & SQLite Local Persistence Layer
    Supports MongoDB Atlas (`mongodb+srv://...`) and local SQLite fallback.
    """

    def __init__(self):
        self.use_mongo = False
        self.mongo_client = None
        self.db = None
        self.mongo_uri = os.environ.get("MONGO_URI", "")

        if MONGO_AVAILABLE and self.mongo_uri:
            self.connect_mongodb(self.mongo_uri)

        if not self.use_mongo:
            print("[Database] Using SQLite local persistence.")
            self._init_sqlite()

    def connect_mongodb(self, uri: str) -> dict:
        """Connects to a live MongoDB Atlas cloud database or local MongoDB"""
        if not MONGO_AVAILABLE:
            return {"success": False, "message": "PyMongo package not installed."}

        try:
            client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=4000)
            client.admin.command('ping')
            self.mongo_client = client
            self.db = client["dista_ai_db"]
            self.use_mongo = True
            self.mongo_uri = uri
            os.environ["MONGO_URI"] = uri
            print(f"[Database] Successfully connected to MongoDB Cloud!")
            return {"success": True, "message": "Successfully connected to MongoDB Cloud Database!"}
        except Exception as e:
            self.use_mongo = False
            return {"success": False, "message": f"MongoDB Connection Error: {str(e)}"}

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
        if self.use_mongo and self.db is not None:
            try:
                self.db.emails.insert_one({
                    "sender": sender,
                    "subject": subject,
                    "body": body,
                    "priority": priority,
                    "timestamp": timestamp,
                    "is_read": bool(is_read)
                })
                return
            except Exception:
                pass
        
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO emails (sender, subject, body, priority, timestamp, is_read)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (sender, subject, body, priority, timestamp, is_read))
        conn.commit()
        conn.close()

    def get_emails(self, limit=10):
        if self.use_mongo and self.db is not None:
            try:
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
            except Exception:
                pass

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
        if self.use_mongo and self.db is not None:
            try:
                self.db.chat_history.insert_one({
                    "sender": sender,
                    "message": message,
                    "timestamp": timestamp
                })
                return
            except Exception:
                pass

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("INSERT INTO chat_history (sender, message, timestamp) VALUES (?, ?, ?)", (sender, message, timestamp))
        conn.commit()
        conn.close()

db_engine = DistaDatabase()
