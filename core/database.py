import sqlite3
import json
import time
from pathlib import Path
from typing import List, Dict, Any
from utils.logger import logger
from utils.config import config
from core.event_bus import Event, EventType

class DatabaseManager:
    def __init__(self):
        self.db_path = "data/system_watch.db"
        self._ensure_db_dir()
        self._init_db()

    def _ensure_db_dir(self):
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    def _init_db(self):
        conn = self._get_conn()
        cursor = conn.cursor()
        
        # Events Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                type TEXT,
                source TEXT,
                data TEXT
            )
        ''')
        
        # Baselines Table (for AI)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS baselines (
                key TEXT PRIMARY KEY,
                data TEXT,
                updated_at REAL
            )
        ''')
        
        conn.commit()
        conn.close()

    def _get_conn(self):
        return sqlite3.connect(self.db_path)

    def store_event(self, event: Event):
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO events (timestamp, type, source, data) VALUES (?, ?, ?, ?)',
                (event.timestamp, event.type.value, event.source, json.dumps(event.data))
            )
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"DB Error store_event: {e}")

    def get_recent_events(self, limit: int = 100) -> List[Dict]:
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute(
                'SELECT timestamp, type, source, data FROM events ORDER BY timestamp DESC LIMIT ?',
                (limit,)
            )
            rows = cursor.fetchall()
            conn.close()
            
            return [{
                'timestamp': r[0],
                'type': r[1],
                'source': r[2],
                'data': json.loads(r[3]) if r[3] else {}
            } for r in rows]
        except Exception as e:
            logger.error(f"DB Error get_recent_events: {e}")
            return []

    def save_baseline(self, key: str, data: Dict):
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT OR REPLACE INTO baselines (key, data, updated_at) VALUES (?, ?, ?)',
                (key, json.dumps(data), time.time())
            )
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"DB Error save_baseline: {e}")

    def get_baseline(self, key: str) -> Dict:
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute('SELECT data FROM baselines WHERE key = ?', (key,))
            row = cursor.fetchone()
            conn.close()
            if row:
                return json.loads(row[0])
            return None
        except Exception as e:
            logger.error(f"DB Error get_baseline: {e}")
            return None

# Global Instance
db = DatabaseManager()
