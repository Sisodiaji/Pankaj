import hashlib
import json
from pathlib import Path

DB_FILE = Path("users_db.json")

def _load_db():
    if DB_FILE.exists():
        try:
            return json.loads(DB_FILE.read_text())
        except:
            return {"users": {}, "configs": {}, "automation_status": {}, "color_preferences": {}}
    return {"users": {}, "configs": {}, "automation_status": {}, "color_preferences": {}}

def _save_db(db):
    DB_FILE.write_text(json.dumps(db, indent=2))

def _hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, password):
    db = _load_db()
    
    if username in db["users"]:
        return False, "Username already exists"
    
    user_id = str(len(db["users"]) + 1)
    db["users"][username] = {
        "user_id": user_id,
        "password": _hash_password(password)
    }
    
    db["configs"][user_id] = {
        "chat_id": "",
        "name_prefix": "",
        "delay": 5,
        "cookies": "",
        "messages": "Hello!"
    }
    
    db["automation_status"][user_id] = False
    
    _save_db(db)
    return True, "Account created successfully"

def verify_user(username, password):
    db = _load_db()
    
    if username not in db["users"]:
        return None
    
    user_data = db["users"][username]
    if user_data["password"] == _hash_password(password):
        return user_data["user_id"]
    
    return None

def get_username(user_id):
    db = _load_db()
    for username, data in db["users"].items():
        if data["user_id"] == user_id:
            return username
    return None

def get_user_config(user_id):
    db = _load_db()
    return db["configs"].get(user_id)

def update_user_config(user_id, chat_id, name_prefix, delay, cookies, messages):
    db = _load_db()
    
    if user_id not in db["configs"]:
        db["configs"][user_id] = {}
    
    db["configs"][user_id] = {
        "chat_id": chat_id,
        "name_prefix": name_prefix,
        "delay": delay,
        "cookies": cookies,
        "messages": messages
    }
    
    _save_db(db)

def get_automation_running(user_id):
    db = _load_db()
    return db["automation_status"].get(user_id, False)

def set_automation_running(user_id, status):
    db = _load_db()
    db["automation_status"][user_id] = status
    _save_db(db)

def get_admin_e2ee_thread_id(user_id, current_cookies):
    return None, None

def set_admin_e2ee_thread_id(user_id, thread_id, cookies, chat_type):
    pass

def clear_admin_e2ee_thread_id(user_id):
    pass

def get_color_preferences(user_id):
    db = _load_db()
    if "color_preferences" not in db:
        db["color_preferences"] = {}
    return db["color_preferences"].get(user_id, {
        "theme": "random",
        "dark_mode": False,
        "custom_gradient": None,
        "custom_border": None,
        "custom_focus": None
    })

def save_color_preferences(user_id, theme, dark_mode, custom_gradient=None, custom_border=None, custom_focus=None):
    db = _load_db()
    if "color_preferences" not in db:
        db["color_preferences"] = {}
    
    db["color_preferences"][user_id] = {
        "theme": theme,
        "dark_mode": dark_mode,
        "custom_gradient": custom_gradient,
        "custom_border": custom_border,
        "custom_focus": custom_focus
    }
    _save_db(db)
