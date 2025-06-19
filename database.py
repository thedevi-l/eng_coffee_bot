import sqlite3
from typing import Optional, Dict

class Database:
    def __init__(self):
        self.conn = sqlite3.connect("users.db", check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                name TEXT NOT NULL,
                level TEXT NOT NULL,
                interests TEXT NOT NULL,
                goal TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def save_user(self, user_data: Dict):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO users
            (user_id, username, name, level, interests, goal)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user_data['user_id'],
            user_data['username'],
            user_data['name'],
            user_data['level'],
            user_data['interests'],
            user_data['goal']
        ))
        self.conn.commit()

    def get_user(self, user_id: int) -> Optional[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            return {
                'user_id': row[0],
                'username': row[1],
                'name': row[2],
                'level': row[3],
                'interests': row[4],
                'goal': row[5]
            }
        return None

    def find_match(self, user_id: int, interests: str, level: str) -> Optional[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM users
            WHERE user_id != ? AND level = ?
        """, (user_id, level))
        rows = cursor.fetchall()

        user_interests = set(map(str.strip, interests.lower().split(',')))
        best_score = -1
        best_match = None
        for row in rows:
            other_interests = set(map(str.strip, row[4].lower().split(',')))
            score = len(user_interests & other_interests)
            if score > best_score:
                best_score = score
                best_match = row

        if best_match:
            return {
                'user_id': best_match[0],
                'username': best_match[1],
                'name': best_match[2],
                'level': best_match[3],
                'interests': best_match[4],
                'goal': best_match[5]
            }
        return None

