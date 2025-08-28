import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

class Database:
    def __init__(self, db_url: str):
        self.conn = sqlite3.connect(db_url, check_same_thread=False)
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                join_date TIMESTAMP,
                warnings INTEGER DEFAULT 0,
                is_banned BOOLEAN DEFAULT FALSE,
                roles TEXT DEFAULT '[]'
            )
        ''')
        
        # Groups table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS groups (
                group_id INTEGER PRIMARY KEY,
                title TEXT,
                settings TEXT DEFAULT '{}'
            )
        ''')
        
        # Warnings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS warnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                group_id INTEGER,
                reason TEXT,
                date TIMESTAMP,
                admin_id INTEGER
            )
        ''')
        
        # Moderation actions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS moderation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                group_id INTEGER,
                action TEXT,
                duration INTEGER,
                reason TEXT,
                date TIMESTAMP,
                admin_id INTEGER
            )
        ''')
        
        # Statistics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS statistics (
                group_id INTEGER,
                date DATE,
                messages INTEGER DEFAULT 0,
                joins INTEGER DEFAULT 0,
                leaves INTEGER DEFAULT 0,
                PRIMARY KEY (group_id, date)
            )
        ''')
        
        self.conn.commit()
    
    def add_user(self, user_id: int, username: str, first_name: str, last_name: str = None):
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT OR IGNORE INTO users (user_id, username, first_name, last_name, join_date) VALUES (?, ?, ?, ?, ?)',
            (user_id, username, first_name, last_name, datetime.now())
        )
        self.conn.commit()
    
    def update_user(self, user_id: int, **kwargs):
        cursor = self.conn.cursor()
        set_clause = ', '.join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values())
        values.append(user_id)
        cursor.execute(f'UPDATE users SET {set_clause} WHERE user_id = ?', values)
        self.conn.commit()
    
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        if row:
            columns = [description[0] for description in cursor.description]
            return dict(zip(columns, row))
        return None
    
    def add_warning(self, user_id: int, group_id: int, reason: str, admin_id: int):
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO warnings (user_id, group_id, reason, date, admin_id) VALUES (?, ?, ?, ?, ?)',
            (user_id, group_id, reason, datetime.now(), admin_id)
        )
        
        # Update user's warning count
        cursor.execute(
            'UPDATE users SET warnings = warnings + 1 WHERE user_id = ?',
            (user_id,)
        )
        
        self.conn.commit()
        return cursor.lastrowid
    
    def get_warnings(self, user_id: int, group_id: int) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT * FROM warnings WHERE user_id = ? AND group_id = ? ORDER BY date DESC',
            (user_id, group_id)
        )
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in rows]
    
    def clear_warnings(self, user_id: int, group_id: int):
        cursor = self.conn.cursor()
        cursor.execute(
            'DELETE FROM warnings WHERE user_id = ? AND group_id = ?',
            (user_id, group_id)
        )
        
        # Reset user's warning count
        cursor.execute(
            'UPDATE users SET warnings = 0 WHERE user_id = ?',
            (user_id,)
        )
        
        self.conn.commit()
    
    def add_moderation_action(self, user_id: int, group_id: int, action: str, duration: int, reason: str, admin_id: int):
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO moderation (user_id, group_id, action, duration, reason, date, admin_id) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (user_id, group_id, action, duration, reason, datetime.now(), admin_id)
        )
        self.conn.commit()
        return cursor.lastrowid
    
    def get_moderation_actions(self, user_id: int, group_id: int, action: str = None) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        if action:
            cursor.execute(
                'SELECT * FROM moderation WHERE user_id = ? AND group_id = ? AND action = ? ORDER BY date DESC',
                (user_id, group_id, action)
            )
        else:
            cursor.execute(
                'SELECT * FROM moderation WHERE user_id = ? AND group_id = ? ORDER BY date DESC',
                (user_id, group_id)
            )
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in rows]
    
    def update_statistics(self, group_id: int, date: str, **kwargs):
        cursor = self.conn.cursor()
        
        # Check if record exists
        cursor.execute(
            'SELECT * FROM statistics WHERE group_id = ? AND date = ?',
            (group_id, date)
        )
        
        if cursor.fetchone():
            set_clause = ', '.join([f"{key} = {key} + ?" for key in kwargs.keys()])
            values = list(kwargs.values())
            values.extend([group_id, date])
            cursor.execute(f'UPDATE statistics SET {set_clause} WHERE group_id = ? AND date = ?', values)
        else:
            columns = ['group_id', 'date'] + list(kwargs.keys())
            placeholders = ', '.join(['?'] * len(columns))
            values = [group_id, date] + list(kwargs.values())
            cursor.execute(f'INSERT INTO statistics ({", ".join(columns)}) VALUES ({placeholders})', values)
        
        self.conn.commit()
    
    def get_statistics(self, group_id: int, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT * FROM statistics WHERE group_id = ? AND date BETWEEN ? AND ? ORDER BY date',
            (group_id, start_date, end_date)
        )
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in rows]
    
    def get_top_warned_users(self, group_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute(
            '''SELECT u.user_id, u.username, u.first_name, u.last_name, COUNT(w.id) as warning_count
               FROM warnings w
               JOIN users u ON w.user_id = u.user_id
               WHERE w.group_id = ?
               GROUP BY w.user_id
               ORDER BY warning_count DESC
               LIMIT ?''',
            (group_id, limit)
        )
        rows = cursor.fetchall()
        return [{
            'user_id': row[0],
            'username': row[1],
            'first_name': row[2],
            'last_name': row[3],
            'warning_count': row[4]
        } for row in rows]
    
    def get_top_active_users(self, group_id: int, days: int = 7, limit: int = 10) -> List[Dict[str, Any]]:
        # This is a simplified version - in a real implementation, you'd track individual user messages
        cursor = self.conn.cursor()
        cursor.execute(
            '''SELECT u.user_id, u.username, u.first_name, u.last_name, COUNT(m.id) as message_count
               FROM messages m
               JOIN users u ON m.user_id = u.user_id
               WHERE m.group_id = ? AND m.date >= date('now', ?)
               GROUP BY m.user_id
               ORDER BY message_count DESC
               LIMIT ?''',
            (group_id, f'-{days} days', limit)
        )
        rows = cursor.fetchall()
        return [{
            'user_id': row[0],
            'username': row[1],
            'first_name': row[2],
            'last_name': row[3],
            'message_count': row[4]
        } for row in rows]
    
    def add_group(self, group_id: int, title: str):
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT OR IGNORE INTO groups (group_id, title) VALUES (?, ?)',
            (group_id, title)
        )
        self.conn.commit()
    
    def update_group_settings(self, group_id: int, settings: Dict[str, Any]):
        cursor = self.conn.cursor()
        cursor.execute(
            'UPDATE groups SET settings = ? WHERE group_id = ?',
            (json.dumps(settings), group_id)
        )
        self.conn.commit()
    
    def get_group_settings(self, group_id: int) -> Dict[str, Any]:
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT settings FROM groups WHERE group_id = ?',
            (group_id,)
        )
        row = cursor.fetchone()
        if row and row[0]:
            return json.loads(row[0])
        return {}
    
    def get_user_roles(self, user_id: int, group_id: int) -> List[str]:
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT roles FROM users WHERE user_id = ?',
            (user_id,)
        )
        row = cursor.fetchone()
        if row and row[0]:
            return json.loads(row[0])
        return []
    
    def update_user_roles(self, user_id: int, roles: List[str]):
        cursor = self.conn.cursor()
        cursor.execute(
            'UPDATE users SET roles = ? WHERE user_id = ?',
            (json.dumps(roles), user_id)
        )
        self.conn.commit()
    
    def get_group_admins(self, group_id: int) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute(
            '''SELECT u.user_id, u.username, u.first_name, u.last_name
               FROM users u
               JOIN user_roles ur ON u.user_id = ur.user_id
               WHERE ur.group_id = ? AND ur.role = 'admin'
               ORDER BY u.first_name''',
            (group_id,)
        )
        rows = cursor.fetchall()
        return [{
            'user_id': row[0],
            'username': row[1],
            'first_name': row[2],
            'last_name': row[3]
        } for row in rows]
    
    def add_user_role(self, user_id: int, group_id: int, role: str):
        cursor = self.conn.cursor()
        # First check if the role already exists
        cursor.execute(
            'SELECT roles FROM user_roles WHERE user_id = ? AND group_id = ?',
            (user_id, group_id)
        )
        row = cursor.fetchone()
        
        if row:
            roles = json.loads(row[0])
            if role not in roles:
                roles.append(role)
                cursor.execute(
                    'UPDATE user_roles SET roles = ? WHERE user_id = ? AND group_id = ?',
                    (json.dumps(roles), user_id, group_id)
                )
        else:
            cursor.execute(
                'INSERT INTO user_roles (user_id, group_id, roles) VALUES (?, ?, ?)',
                (user_id, group_id, json.dumps([role]))
            )
        
        self.conn.commit()
    
    def remove_user_role(self, user_id: int, group_id: int, role: str):
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT roles FROM user_roles WHERE user_id = ? AND group_id = ?',
            (user_id, group_id)
        )
        row = cursor.fetchone()
        
        if row:
            roles = json.loads(row[0])
            if role in roles:
                roles.remove(role)
                if roles:
                    cursor.execute(
                        'UPDATE user_roles SET roles = ? WHERE user_id = ? AND group_id = ?',
                        (json.dumps(roles), user_id, group_id)
                    )
                else:
                    cursor.execute(
                        'DELETE FROM user_roles WHERE user_id = ? AND group_id = ?',
                        (user_id, group_id)
                    )
        
        self.conn.commit()