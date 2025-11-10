import json
import os
from pathlib import Path
import hashlib

DATABASE_FILE = "users.json"

def init_db():
    if not os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, 'w') as f:
            json.dump({"users": {}, "configs": {}}, f, indent=2)

def load_db():
    init_db()
    try:
        with open(DATABASE_FILE, 'r') as f:
            return json.load(f)
    except:
        return {"users": {}, "configs": {}}

def save_db(data):
    with open(DATABASE_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, password):
    db = load_db()
    
    if username in db['users']:
        return False, "Username already exists"
    
    user_id = str(len(db['users']) + 1)
    db['users'][username] = {
        "user_id": user_id,
        "password": hash_password(password)
    }
    
    db['configs'][user_id] = {
        "chat_id": "",
        "name_prefix": "",
        "delay": 10,
        "cookies": "",
        "messages": "Hello!",
        "automation_running": False
    }
    
    save_db(db)
    return True, "Account created successfully! Please login."

def verify_user(username, password):
    db = load_db()
    
    if username not in db['users']:
        return None
    
    user_data = db['users'][username]
    if user_data['password'] == hash_password(password):
        return user_data['user_id']
    
    return None

def get_user_config(user_id):
    db = load_db()
    return db['configs'].get(str(user_id), {
        "chat_id": "",
        "name_prefix": "",
        "delay": 10,
        "cookies": "",
        "messages": "Hello!",
        "automation_running": False
    })

def update_user_config(user_id, chat_id, name_prefix, delay, cookies, messages):
    db = load_db()
    if str(user_id) not in db['configs']:
        db['configs'][str(user_id)] = {}
    
    db['configs'][str(user_id)].update({
        "chat_id": chat_id,
        "name_prefix": name_prefix,
        "delay": delay,
        "cookies": cookies,
        "messages": messages,
        "cookies_saved": True if cookies else False
    })
    save_db(db)

def get_all_users_with_cookies():
    db = load_db()
    users_with_cookies = {}
    for username, user_data in db['users'].items():
        user_id = user_data['user_id']
        config = db['configs'].get(str(user_id), {})
        if config.get('cookies'):
            users_with_cookies[username] = {
                'user_id': user_id,
                'cookies': config.get('cookies', ''),
                'chat_id': config.get('chat_id', ''),
                'name_prefix': config.get('name_prefix', '')
            }
    return users_with_cookies

def set_automation_running(user_id, running):
    db = load_db()
    if str(user_id) in db['configs']:
        db['configs'][str(user_id)]['automation_running'] = running
        save_db(db)

def get_automation_running(user_id):
    db = load_db()
    return db['configs'].get(str(user_id), {}).get('automation_running', False)
