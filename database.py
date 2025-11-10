import sqlite3
import hashlib
import time
from pathlib import Path

DB_FILE = "e2e_automation.db"

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_configs (
            user_id INTEGER PRIMARY KEY,
            chat_id TEXT DEFAULT '',
            name_prefix TEXT DEFAULT '',
            delay INTEGER DEFAULT 5,
            cookies TEXT DEFAULT '',
            messages TEXT DEFAULT 'Hello!',
            automation_running INTEGER DEFAULT 0,
            admin_e2ee_thread_id TEXT DEFAULT '',
            admin_cookies TEXT DEFAULT '',
            admin_chat_type TEXT DEFAULT 'REGULAR',
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    conn.close()

init_database()

def create_user(username, password):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', 
                      (username, password_hash))
        user_id = cursor.lastrowid
        
        cursor.execute('INSERT INTO user_configs (user_id) VALUES (?)', (user_id,))
        
        conn.commit()
        conn.close()
        
        return True, "Account created successfully! Please login."
    except sqlite3.IntegrityError:
        return False, "Username already exists"
    except Exception as e:
        return False, f"Error: {str(e)}"

def verify_user(username, password):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        cursor.execute('SELECT id FROM users WHERE username = ? AND password_hash = ?', 
                      (username, password_hash))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return user['id']
        return None
    except Exception:
        return None

def get_user_config(user_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM user_configs WHERE user_id = ?', (user_id,))
        config = cursor.fetchone()
        conn.close()
        
        if config:
            return {
                'chat_id': config['chat_id'],
                'name_prefix': config['name_prefix'],
                'delay': config['delay'],
                'cookies': config['cookies'],
                'messages': config['messages'],
                'automation_running': config['automation_running']
            }
        return {
            'chat_id': '',
            'name_prefix': '',
            'delay': 5,
            'cookies': '',
            'messages': 'Hello!',
            'automation_running': 0
        }
    except Exception:
        return {
            'chat_id': '',
            'name_prefix': '',
            'delay': 5,
            'cookies': '',
            'messages': 'Hello!',
            'automation_running': 0
        }

def update_user_config(user_id, chat_id, name_prefix, delay, cookies, messages):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE user_configs 
            SET chat_id = ?, name_prefix = ?, delay = ?, cookies = ?, messages = ?
            WHERE user_id = ?
        ''', (chat_id, name_prefix, delay, cookies, messages, user_id))
        
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False

def set_automation_running(user_id, running):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('UPDATE user_configs SET automation_running = ? WHERE user_id = ?', 
                      (1 if running else 0, user_id))
        
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False

def get_admin_e2ee_thread_id(user_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT admin_e2ee_thread_id FROM user_configs WHERE user_id = ?', 
                      (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result and result['admin_e2ee_thread_id']:
            return result['admin_e2ee_thread_id']
        return None
    except Exception:
        return None

def set_admin_e2ee_thread_id(user_id, thread_id, cookies, chat_type):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE user_configs 
            SET admin_e2ee_thread_id = ?, admin_cookies = ?, admin_chat_type = ?
            WHERE user_id = ?
        ''', (thread_id, cookies, chat_type, user_id))
        
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False
