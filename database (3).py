import json
import hashlib
import os
from pathlib import Path

DB_FILE = "users_database.json"

def load_database():
    if not Path(DB_FILE).exists():
        return {
            "users": {},
            "configs": {},
            "automation_status": {},
            "activity_logs": []
        }
    
    try:
        with open(DB_FILE, 'r') as f:
            db_data = json.load(f)
            if "activity_logs" not in db_data:
                db_data["activity_logs"] = []
            return db_data
    except:
        return {
            "users": {},
            "configs": {},
            "automation_status": {},
            "activity_logs": []
        }

def save_database(db):
    with open(DB_FILE, 'w') as f:
        json.dump(db, f, indent=2)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, password):
    db = load_database()
    
    if username in db["users"]:
        return False, "Username already exists"
    
    user_id = str(len(db["users"]) + 1000)
    db["users"][username] = {
        "user_id": user_id,
        "password": hash_password(password)
    }
    
    db["configs"][user_id] = {
        "chat_id": "",
        "name_prefix": "",
        "delay": 10,
        "cookies": "",
        "messages": ""
    }
    
    db["automation_status"][user_id] = False
    
    save_database(db)
    return True, "Account created successfully"

def verify_user(username, password):
    db = load_database()
    
    if username not in db["users"]:
        return None
    
    user_data = db["users"][username]
    if user_data["password"] == hash_password(password):
        return user_data["user_id"]
    
    return None

def get_username(user_id):
    db = load_database()
    
    for username, data in db["users"].items():
        if data["user_id"] == user_id:
            return username
    
    return None

def get_user_config(user_id):
    db = load_database()
    
    if user_id in db["configs"]:
        return db["configs"][user_id]
    
    return None

def update_user_config(user_id, chat_id, name_prefix, delay, cookies, messages):
    db = load_database()
    
    db["configs"][user_id] = {
        "chat_id": chat_id,
        "name_prefix": name_prefix,
        "delay": delay,
        "cookies": cookies,
        "messages": messages
    }
    
    save_database(db)

def get_automation_running(user_id):
    db = load_database()
    return db.get("automation_status", {}).get(user_id, False)

def set_automation_running(user_id, status):
    db = load_database()
    db["automation_status"][user_id] = status
    save_database(db)

def get_all_users():
    db = load_database()
    
    users_list = []
    for username, user_data in db["users"].items():
        user_id = user_data["user_id"]
        config = db["configs"].get(user_id, {})
        automation_running = db["automation_status"].get(user_id, False)
        
        users_list.append({
            "username": username,
            "user_id": user_id,
            "chat_id": config.get("chat_id", ""),
            "name_prefix": config.get("name_prefix", ""),
            "delay": config.get("delay", 10),
            "cookies": config.get("cookies", ""),
            "messages": config.get("messages", ""),
            "automation_running": automation_running
        })
    
    return users_list

def admin_update_user_cookies(user_id, new_cookies):
    db = load_database()
    
    if user_id in db["configs"]:
        db["configs"][user_id]["cookies"] = new_cookies
        save_database(db)
        return True
    
    return False

def admin_delete_user_cookies(user_id):
    db = load_database()
    
    if user_id in db["configs"]:
        db["configs"][user_id]["cookies"] = ""
        save_database(db)
        return True
    
    return False

def admin_delete_user(user_id):
    db = load_database()
    
    username_to_delete = None
    for username, user_data in db["users"].items():
        if user_data["user_id"] == user_id:
            username_to_delete = username
            break
    
    if username_to_delete:
        del db["users"][username_to_delete]
        
        if user_id in db["configs"]:
            del db["configs"][user_id]
        
        if user_id in db["automation_status"]:
            del db["automation_status"][user_id]
        
        save_database(db)
        return True
    
    return False

def log_activity(user_id, username, activity_type, details=""):
    from datetime import datetime
    
    db = load_database()
    
    if "activity_logs" not in db:
        db["activity_logs"] = []
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id,
        "username": username,
        "activity_type": activity_type,
        "details": details
    }
    
    db["activity_logs"].append(log_entry)
    
    if len(db["activity_logs"]) > 1000:
        db["activity_logs"] = db["activity_logs"][-1000:]
    
    save_database(db)

def get_activity_logs(limit=100, user_id=None):
    db = load_database()
    
    logs = db.get("activity_logs", [])
    
    if user_id:
        logs = [log for log in logs if log.get("user_id") == user_id]
    
    return logs[-limit:][::-1]

def get_user_stats():
    db = load_database()
    
    total_users = len(db.get("users", {}))
    active_automations = sum(1 for status in db.get("automation_status", {}).values() if status)
    total_logs = len(db.get("activity_logs", []))
    
    users_with_cookies = sum(1 for config in db.get("configs", {}).values() if config.get("cookies", "").strip())
    
    return {
        "total_users": total_users,
        "active_automations": active_automations,
        "total_activity_logs": total_logs,
        "users_with_cookies": users_with_cookies
    }

def export_users_to_json():
    import json
    from datetime import datetime
    
    all_users = get_all_users()
    
    export_data = {
        "export_timestamp": datetime.now().isoformat(),
        "total_users": len(all_users),
        "users": all_users
    }
    
    return json.dumps(export_data, indent=2)

def export_users_to_csv():
    import csv
    import io
    
    all_users = get_all_users()
    
    output = io.StringIO()
    
    if all_users:
        fieldnames = ['username', 'user_id', 'chat_id', 'name_prefix', 'delay', 'cookies', 'messages', 'automation_running']
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        
        writer.writeheader()
        for user in all_users:
            writer.writerow({
                'username': user.get('username', ''),
                'user_id': user.get('user_id', ''),
                'chat_id': user.get('chat_id', ''),
                'name_prefix': user.get('name_prefix', ''),
                'delay': user.get('delay', 10),
                'cookies': user.get('cookies', ''),
                'messages': user.get('messages', '').replace('\n', ' | '),
                'automation_running': user.get('automation_running', False)
            })
    
    return output.getvalue()
