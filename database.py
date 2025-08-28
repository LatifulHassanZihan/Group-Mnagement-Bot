import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

class Database:
    def __init__(self, db_url: str):
        # Use in-memory database for Render free tier
        if db_url.startswith('sqlite:///'):
            db_path = db_url.replace('sqlite:///', '')
            if db_path == 'bot.db':  # Default path, use in-memory instead
                self.conn = sqlite3.connect(':memory:', check_same_thread=False)
            else:
                self.conn = sqlite3.connect(db_path, check_same_thread=False)
        else:
            # Fallback to in-memory database
            self.conn = sqlite3.connect(':memory:', check_same_thread=False)
        
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
        
        # Statistics table (in-memory only, will reset on restart)
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
    
    # ... rest of the database methods remain the same
