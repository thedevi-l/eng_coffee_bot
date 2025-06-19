import sqlite3

class Database:
    def __init__(self):
        self.conn = sqlite3.connect("users.db", check_same_thread=False)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                name TEXT,
                level TEXT,
                interests TEXT,
                goal TEXT
            )
        """)
        self.conn.commit()

    def save_user(self, user):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO users (user_id, username, name, level, interests, goal)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user['user_id'],
            user['username'],
            user['name'],
            user['level'],
            user['interests'],
            user['goal']
        ))
        self.conn.commit()

    def get_user(self, user_id):
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

    def find_best_match(self, user_id, level, interests):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE user_id != ? AND level = ?",
            (user_id, level)
        )
        rows = cursor.fetchall()
        if not rows:
            return None

        user_interests = set(i.strip().lower() for i in interests.split(","))
        best_score = -1
        best_match = None

        for row in rows:
            other_interests = set(i.strip().lower() for i in row[4].split(","))
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

    def get_all_users(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        return [{'user_id': row[0]} for row in rows]
