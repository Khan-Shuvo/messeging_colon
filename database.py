import sqlite3
from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal

class Database(QObject):
    user_status_changed = pyqtSignal(int, bool)  # user_id, is_online
    
    def __init__(self):
        super().__init__()
        self.conn = sqlite3.connect('messaging_app.db', check_same_thread=False)
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_online BOOLEAN DEFAULT FALSE,
            last_seen TIMESTAMP
        )
        ''')
        
        # Messages table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER,
            group_id INTEGER,
            content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_read BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (sender_id) REFERENCES users(id),
            FOREIGN KEY (receiver_id) REFERENCES users(id),
            FOREIGN KEY (group_id) REFERENCES groups(id),
            CHECK ((receiver_id IS NOT NULL AND group_id IS NULL) OR 
                   (receiver_id IS NULL AND group_id IS NOT NULL))
        )
        ''')
        
        # Groups table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_by INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
        ''')
        
        # Group members table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS group_members (
            group_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (group_id, user_id),
            FOREIGN KEY (group_id) REFERENCES groups(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        
        self.conn.commit()
    
    # User related methods
    def add_user(self, first_name, last_name, email, password):
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO users (first_name, last_name, email, password)
        VALUES (?, ?, ?, ?)
        ''', (first_name, last_name, email, password))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_user_by_email(self, email):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        return cursor.fetchone()
    
    def update_user_status(self, user_id, is_online):
        cursor = self.conn.cursor()
        cursor.execute('''
        UPDATE users 
        SET is_online = ?, last_seen = ?
        WHERE id = ?
        ''', (is_online, datetime.now(), user_id))
        self.conn.commit()
        self.user_status_changed.emit(user_id, is_online)
    
    def get_online_users(self, exclude_user_id=None):
        cursor = self.conn.cursor()
        if exclude_user_id:
            cursor.execute('''
            SELECT id, first_name, last_name, email 
            FROM users 
            WHERE is_online = TRUE AND id != ?
            ''', (exclude_user_id,))
        else:
            cursor.execute('''
            SELECT id, first_name, last_name, email 
            FROM users 
            WHERE is_online = TRUE
            ''')
        return cursor.fetchall()
    
    # Message related methods
    def add_message(self, sender_id, receiver_id=None, group_id=None, content=""):
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO messages (sender_id, receiver_id, group_id, content)
        VALUES (?, ?, ?, ?)
        ''', (sender_id, receiver_id, group_id, content))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_messages(self, user1_id, user2_id):
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT * FROM messages
        WHERE (sender_id = ? AND receiver_id = ?) OR 
              (sender_id = ? AND receiver_id = ?)
        ORDER BY timestamp
        ''', (user1_id, user2_id, user2_id, user1_id))
        return cursor.fetchall()
    
    def get_group_messages(self, group_id):
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT m.*, u.first_name, u.last_name 
        FROM messages m
        JOIN users u ON m.sender_id = u.id
        WHERE m.group_id = ?
        ORDER BY m.timestamp
        ''', (group_id,))
        return cursor.fetchall()
    
    # Group related methods
    def create_group(self, name, created_by):
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO groups (name, created_by)
        VALUES (?, ?)
        ''', (name, created_by))
        group_id = cursor.lastrowid
        self.conn.commit()
        return group_id
    
    def add_group_member(self, group_id, user_id):
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT OR IGNORE INTO group_members (group_id, user_id)
        VALUES (?, ?)
        ''', (group_id, user_id))
        self.conn.commit()
    
    def get_user_groups(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT g.* FROM groups g
        JOIN group_members gm ON g.id = gm.group_id
        WHERE gm.user_id = ?
        ''', (user_id,))
        return cursor.fetchall()
    
    def close(self):
        self.conn.close()
    

    # database.py ফাইলে
    def search_user_by_email_or_name(self, search_term, exclude_user_id):
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT id, first_name, last_name, email, is_online 
        FROM users 
        WHERE (email LIKE ? OR first_name LIKE ? OR last_name LIKE ?) 
        AND id != ?
        ''', (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%", exclude_user_id))
        return cursor.fetchall()

    def get_user_by_id(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        return cursor.fetchone()