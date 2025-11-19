import streamlit as st
import time
import threading
import random
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import database as db
import requests
import os
import json

st.set_page_config(
    page_title="FB E2EE by Sonu Rajput",
    page_icon="😘",
    layout="wide",
    initial_sidebar_state="expanded"
)

COLOR_PALETTES = {
    "random": {
        "name": "Random Colors",
        "gradient": None,
        "border": None,
        "focus": None,
        "description": "Fresh random colors on every page load"
    },
    "ocean": {
        "name": "Ocean Breeze",
        "gradient": ["#667eea", "#764ba2"],
        "border": "#4a90e2",
        "focus": "#50c9ff",
        "description": "Cool blues and purples"
    },
    "sunset": {
        "name": "Sunset Glow",
        "gradient": ["#ff6b6b", "#feca57"],
        "border": "#ff6348",
        "focus": "#ff9ff3",
        "description": "Warm reds and oranges"
    },
    "forest": {
        "name": "Forest Green",
        "gradient": ["#11998e", "#38ef7d"],
        "border": "#06D6A0",
        "focus": "#80ed99",
        "description": "Fresh greens and teals"
    },
    "royal": {
        "name": "Royal Purple",
        "gradient": ["#8e2de2", "#4a00e0"],
        "border": "#7209b7",
        "focus": "#b388ff",
        "description": "Majestic purples"
    },
    "fire": {
        "name": "Fire & Ice",
        "gradient": ["#f12711", "#f5af19"],
        "border": "#e63946",
        "focus": "#ff006e",
        "description": "Hot reds and golds"
    },
    "midnight": {
        "name": "Midnight Sky",
        "gradient": ["#2c3e50", "#3498db"],
        "border": "#34495e",
        "focus": "#5dade2",
        "description": "Deep blues and grays"
    }
}

def generate_random_gradient():
    """Generate random gradient colors for input fields"""
    colors = [
        f"#{random.randint(0, 255):02x}{random.randint(0, 255):02x}{random.randint(0, 255):02x}",
        f"#{random.randint(0, 255):02x}{random.randint(0, 255):02x}{random.randint(0, 255):02x}"
    ]
    return colors

def generate_random_color():
    """Generate a single random color"""
    return f"#{random.randint(0, 255):02x}{random.randint(0, 255):02x}{random.randint(0, 255):02x}"

def get_theme_colors(theme_name, user_id=None):
    """Get colors based on theme selection"""
    if theme_name == "random":
        return {
            "gradient": generate_random_gradient(),
            "border": generate_random_color(),
            "focus": generate_random_color()
        }
    elif theme_name in COLOR_PALETTES:
        palette = COLOR_PALETTES[theme_name]
        return {
            "gradient": palette["gradient"],
            "border": palette["border"],
            "focus": palette["focus"]
        }
    return {
        "gradient": ["#667eea", "#764ba2"],
        "border": "#4a90e2",
        "focus": "#50c9ff"
    }

if 'current_theme' not in st.session_state:
    st.session_state.current_theme = "random"
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False
if 'input_gradient' not in st.session_state:
    theme_colors = get_theme_colors(st.session_state.current_theme)
    st.session_state.input_gradient = theme_colors["gradient"]
if 'border_color' not in st.session_state:
    theme_colors = get_theme_colors(st.session_state.current_theme)
    st.session_state.border_color = theme_colors["border"]
if 'focus_color' not in st.session_state:
    theme_colors = get_theme_colors(st.session_state.current_theme)
    st.session_state.focus_color = theme_colors["focus"]

dark_bg = "#1a1a2e" if st.session_state.dark_mode else "#ffffff"
dark_text = "#e0e0e0" if st.session_state.dark_mode else "#333333"
dark_card_bg = "#16213e" if st.session_state.dark_mode else "white"
dark_sidebar_bg = "#0f1419" if st.session_state.dark_mode else "#f0f2f6"

custom_css = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    * {{
        font-family: 'Poppins', sans-serif;
        transition: background-color 0.5s ease, color 0.5s ease, border-color 0.5s ease;
    }}
    
    .stApp {{
        background-color: {dark_bg};
        transition: background-color 0.5s ease;
    }}
    
    .main-header {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        transition: all 0.5s ease;
    }}
    
    .main-header h1 {{
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }}
    
    .main-header p {{
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }}
    
    .stButton>button {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }}
    
    .stButton>button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }}
    
    .login-box {{
        background: {dark_card_bg};
        padding: 3rem;
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        max-width: 500px;
        margin: 2rem auto;
        transition: all 0.5s ease;
    }}
    
    .success-box {{
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 1rem 0;
    }}
    
    .error-box {{
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 1rem 0;
    }}
    
    .footer {{
        text-align: center;
        padding: 2rem;
        color: {'#8b9dc3' if st.session_state.dark_mode else '#667eea'};
        font-weight: 600;
        margin-top: 3rem;
        transition: color 0.5s ease;
    }}
    
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stNumberInput>div>div>input {{
        border-radius: 10px;
        border: 3px solid {st.session_state.border_color};
        background: linear-gradient(135deg, {st.session_state.input_gradient[0]} 0%, {st.session_state.input_gradient[1]} 100%);
        padding: 0.75rem;
        transition: all 0.5s ease, transform 0.2s ease, box-shadow 0.3s ease;
        color: white;
        font-weight: 600;
    }}
    
    .stTextInput>div>div>input::placeholder, .stTextArea>div>div>textarea::placeholder {{
        color: rgba(255, 255, 255, 0.7);
    }}
    
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {{
        border-color: {st.session_state.focus_color};
        box-shadow: 0 0 0 3px {st.session_state.focus_color}40;
        transform: scale(1.02);
    }}
    
    .info-card {{
        background: linear-gradient(135deg, {'#1e2936' if st.session_state.dark_mode else '#f5f7fa'} 0%, {'#2d3748' if st.session_state.dark_mode else '#c3cfe2'} 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        transition: all 0.5s ease;
    }}
    
    .log-container {{
        background: #1e1e1e;
        color: #00ff00;
        padding: 1rem;
        border-radius: 10px;
        font-family: 'Courier New', monospace;
        max-height: 400px;
        overflow-y: auto;
    }}
    
    .palette-card {{
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
        border: 2px solid transparent;
    }}
    
    .palette-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        border-color: #667eea;
    }}
    
    .palette-preview {{
        height: 50px;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        transition: all 0.3s ease;
    }}
    
    .theme-name {{
        font-weight: 600;
        color: {dark_text};
        margin-bottom: 0.25rem;
        transition: color 0.5s ease;
    }}
    
    .theme-desc {{
        font-size: 0.85rem;
        color: {'#a0a0a0' if st.session_state.dark_mode else '#666666'};
        transition: color 0.5s ease;
    }}
    
    section[data-testid="stSidebar"] {{
        background-color: {dark_sidebar_bg};
        transition: background-color 0.5s ease;
    }}
    
    .stMarkdown, .stMarkdown p {{
        color: {dark_text};
        transition: color 0.5s ease;
    }}
    
    @keyframes colorPulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.8; }}
    }}
    
    .color-changing {{
        animation: colorPulse 1s ease-in-out;
    }}
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'automation_running' not in st.session_state:
    st.session_state.automation_running = False
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'message_count' not in st.session_state:
    st.session_state.message_count = 0

class AutomationState:
    def __init__(self):
        self.running = False
        self.message_count = 0
        self.logs = []
        self.message_rotation_index = 0

if 'automation_state' not in st.session_state:
    st.session_state.automation_state = AutomationState()

if 'auto_start_checked' not in st.session_state:
    st.session_state.auto_start_checked = False

def log_message(msg, automation_state=None):
    timestamp = time.strftime("%H:%M:%S")
    formatted_msg = f"[{timestamp}] {msg}"
    
    if automation_state:
        automation_state.logs.append(formatted_msg)
    else:
        if 'logs' in st.session_state:
            st.session_state.logs.append(formatted_msg)

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
        log_message(f'{process_id}: Page Title: {page_title}', automation_state)
        log_message(f'{process_id}: Page URL: {page_url}', automation_state)
    except Exception as e:
        log_message(f'{process_id}: Could not get page info: {e}', automation_state)
    
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
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            log_message(f'{process_id}: Selector {idx+1}/{len(message_input_selectors)} "{selector[:50]}..." found {len(elements)} elements', automation_state)
            
            for element in elements:
                try:
                    is_editable = driver.execute_script("""
                        return arguments[0].contentEditable === 'true' || 
                               arguments[0].tagName === 'TEXTAREA' || 
                               arguments[0].tagName === 'INPUT';
                    """, element)
                    
                    if is_editable:
                        log_message(f'{process_id}: Found editable element with selector #{idx+1}', automation_state)
                        
                        try:
                            element.click()
                            time.sleep(0.5)
                        except:
                            pass
                        
                        element_text = driver.execute_script("return arguments[0].placeholder || arguments[0].getAttribute('aria-label') || arguments[0].getAttribute('aria-placeholder') || '';", element).lower()
                        
                        keywords = ['message', 'write', 'type', 'send', 'chat', 'msg', 'reply', 'text', 'aa']
                        if any(keyword in element_text for keyword in keywords):
                            log_message(f'{process_id}: ✅ Found message input with text: {element_text[:50]}', automation_state)
                            return element
                        elif idx < 10:
                            log_message(f'{process_id}: ✅ Using primary selector editable element (#{idx+1})', automation_state)
                            return element
                        elif selector == '[contenteditable="true"]' or selector == 'textarea' or selector == 'input[type="text"]':
                            log_message(f'{process_id}: ✅ Using fallback editable element', automation_state)
                            return element
                except Exception as e:
                    log_message(f'{process_id}: Element check failed: {str(e)[:50]}', automation_state)
                    continue
        except Exception as e:
            continue
    
    try:
        page_source = driver.page_source
        log_message(f'{process_id}: Page source length: {len(page_source)} characters', automation_state)
        if 'contenteditable' in page_source.lower():
            log_message(f'{process_id}: Page contains contenteditable elements', automation_state)
        else:
            log_message(f'{process_id}: No contenteditable elements found in page', automation_state)
    except Exception:
        pass
    
    return None

def setup_browser(automation_state=None):
    log_message('Setting up Chrome browser...', automation_state)
    
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-setuid-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36')
    
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
    
    chromedriver_paths = [
        '/usr/bin/chromedriver',
        '/usr/local/bin/chromedriver'
    ]
    
    driver_path = None
    for driver_candidate in chromedriver_paths:
        if Path(driver_candidate).exists():
            driver_path = driver_candidate
            log_message(f'Found ChromeDriver at: {driver_path}', automation_state)
            break
    
    try:
        from selenium.webdriver.chrome.service import Service
        
        if driver_path:
            service = Service(executable_path=driver_path)
            driver = webdriver.Chrome(service=service, options=chrome_options)
            log_message('Chrome started with detected ChromeDriver!', automation_state)
        else:
            driver = webdriver.Chrome(options=chrome_options)
            log_message('Chrome started with default driver!', automation_state)
        
        driver.set_window_size(1920, 1080)
        log_message('Chrome browser setup completed successfully!', automation_state)
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
                else:
                    log_message(f'{process_id}: Send button clicked', automation_state)
                
                time.sleep(1)
                
                messages_sent += 1
                automation_state.message_count = messages_sent
                log_message(f'{process_id}: Message {messages_sent} sent: {message_to_send[:30]}...', automation_state)
                
                time.sleep(delay)
                
            except Exception as e:
                log_message(f'{process_id}: Error sending message: {str(e)}', automation_state)
                break
        
        log_message(f'{process_id}: Automation stopped! Total messages sent: {messages_sent}', automation_state)
        automation_state.running = False
        db.set_automation_running(user_id, False)
        return messages_sent
        
    except Exception as e:
        log_message(f'{process_id}: Fatal error: {str(e)}', automation_state)
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

def start_automation(user_config, user_id):
    automation_state = st.session_state.automation_state
    
    if automation_state.running:
        return
    
    automation_state.running = True
    automation_state.message_count = 0
    automation_state.logs = []
    
    db.set_automation_running(user_id, True)
    
    username = db.get_username(user_id)
    thread = threading.Thread(target=send_messages, args=(user_config, automation_state, user_id))
    thread.daemon = True
    thread.start()

def stop_automation(user_id):
    st.session_state.automation_state.running = False
    db.set_automation_running(user_id, False)

st.markdown('<div class="main-header"><h1>Sonu Rajput E2EE FACEBOOK CONVO</h1><p>Created by Sonu Rajput</p></div>', unsafe_allow_html=True)

if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["🔐 Login", "✨ Sign Up"])
    
    with tab1:
        st.markdown("### Welcome Back!")
        username = st.text_input("Username", key="login_username", placeholder="Enter your username")
        password = st.text_input("Password", key="login_password", type="password", placeholder="Enter your password")
        
        if st.button("Login", key="login_btn", use_container_width=True):
            if username and password:
                user_id = db.verify_user(username, password)
                if user_id:
                    st.session_state.logged_in = True
                    st.session_state.user_id = user_id
                    st.session_state.username = username
                    
                    color_prefs = db.get_color_preferences(user_id)
                    st.session_state.current_theme = color_prefs.get("theme", "random")
                    st.session_state.dark_mode = color_prefs.get("dark_mode", False)
                    
                    if color_prefs.get("custom_gradient"):
                        st.session_state.input_gradient = color_prefs["custom_gradient"]
                        st.session_state.border_color = color_prefs.get("custom_border", generate_random_color())
                        st.session_state.focus_color = color_prefs.get("custom_focus", generate_random_color())
                    else:
                        theme_colors = get_theme_colors(st.session_state.current_theme)
                        st.session_state.input_gradient = theme_colors["gradient"]
                        st.session_state.border_color = theme_colors["border"]
                        st.session_state.focus_color = theme_colors["focus"]
                    
                    should_auto_start = db.get_automation_running(user_id)
                    if should_auto_start:
                        user_config = db.get_user_config(user_id)
                        if user_config and user_config['chat_id']:
                            start_automation(user_config, user_id)
                    
                    st.success(f"✅ Welcome back, {username}!")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password!")
            else:
                st.warning("⚠️ Please enter both username and password")
    
    with tab2:
        st.markdown("### Create New Account")
        new_username = st.text_input("Choose Username", key="signup_username", placeholder="Choose a unique username")
        new_password = st.text_input("Choose Password", key="signup_password", type="password", placeholder="Create a strong password")
        confirm_password = st.text_input("Confirm Password", key="confirm_password", type="password", placeholder="Re-enter your password")
        
        if st.button("Create Account", key="signup_btn", use_container_width=True):
            if new_username and new_password and confirm_password:
                if new_password == confirm_password:
                    success, message = db.create_user(new_username, new_password)
                    if success:
                        st.success(f"✅ {message} Please login now!")
                    else:
                        st.error(f"❌ {message}")
                else:
                    st.error("❌ Passwords do not match!")
            else:
                st.warning("⚠️ Please fill all fields")

else:
    if not st.session_state.auto_start_checked and st.session_state.user_id:
        st.session_state.auto_start_checked = True
        should_auto_start = db.get_automation_running(st.session_state.user_id)
        if should_auto_start and not st.session_state.automation_state.running:
            user_config = db.get_user_config(st.session_state.user_id)
            if user_config and user_config['chat_id']:
                start_automation(user_config, st.session_state.user_id)
    
    st.sidebar.markdown(f"### 👤 {st.session_state.username}")
    st.sidebar.markdown(f"**User ID:** {st.session_state.user_id}")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎨 Appearance")
    
    dark_mode_checkbox = st.sidebar.checkbox("🌙 Dark Mode", value=st.session_state.dark_mode, key="dark_mode_toggle")
    
    if dark_mode_checkbox != st.session_state.dark_mode:
        st.session_state.dark_mode = dark_mode_checkbox
        if st.session_state.user_id:
            if st.session_state.current_theme == "random":
                db.save_color_preferences(
                    st.session_state.user_id,
                    st.session_state.current_theme,
                    dark_mode_checkbox,
                    None,
                    None,
                    None
                )
            else:
                db.save_color_preferences(
                    st.session_state.user_id,
                    st.session_state.current_theme,
                    dark_mode_checkbox,
                    st.session_state.input_gradient,
                    st.session_state.border_color,
                    st.session_state.focus_color
                )
        st.rerun()
    
    st.sidebar.markdown("### 🎨 Color Themes")
    
    for theme_key, theme_data in COLOR_PALETTES.items():
        if theme_data["gradient"]:
            gradient_style = f"background: linear-gradient(135deg, {theme_data['gradient'][0]} 0%, {theme_data['gradient'][1]} 100%);"
        else:
            gradient_style = "background: linear-gradient(135deg, #667eea 0%, #764ba2 100%, #f093fb 100%);"
        
        is_selected = st.session_state.current_theme == theme_key
        border_style = "border: 3px solid #667eea;" if is_selected else "border: 2px solid transparent;"
        
        palette_html = f"""
        <div class="palette-card" style="{border_style} background: {'#2d3748' if st.session_state.dark_mode else '#f8f9fa'};">
            <div class="palette-preview" style="{gradient_style}"></div>
            <div class="theme-name">{'✓ ' if is_selected else ''}{theme_data['name']}</div>
            <div class="theme-desc">{theme_data['description']}</div>
        </div>
        """
        st.sidebar.markdown(palette_html, unsafe_allow_html=True)
        
        if st.sidebar.button(f"Apply {theme_data['name']}", key=f"theme_{theme_key}", use_container_width=True):
            st.session_state.current_theme = theme_key
            theme_colors = get_theme_colors(theme_key)
            st.session_state.input_gradient = theme_colors["gradient"]
            st.session_state.border_color = theme_colors["border"]
            st.session_state.focus_color = theme_colors["focus"]
            
            if st.session_state.user_id:
                if theme_key == "random":
                    db.save_color_preferences(
                        st.session_state.user_id,
                        theme_key,
                        st.session_state.dark_mode,
                        None,
                        None,
                        None
                    )
                else:
                    db.save_color_preferences(
                        st.session_state.user_id,
                        theme_key,
                        st.session_state.dark_mode,
                        theme_colors["gradient"],
                        theme_colors["border"],
                        theme_colors["focus"]
                    )
            st.rerun()
    
    st.sidebar.markdown("---")
    
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        if st.session_state.automation_state.running:
            stop_automation(st.session_state.user_id)
        
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.username = None
        st.session_state.automation_running = False
        st.session_state.auto_start_checked = False
        st.rerun()
    
    user_config = db.get_user_config(st.session_state.user_id)
    
    if user_config:
        tab1, tab2 = st.tabs(["⚙️ Configuration", "🚀 Automation"])
        
        with tab1:
            st.markdown("### Your Configuration")
            
            chat_id = st.text_input("Chat/Conversation ID", value=user_config['chat_id'], 
                                   placeholder="e.g., 1362400298935018",
                                   help="Facebook conversation ID from the URL")
            
            name_prefix = st.text_input("Hatersname", value=user_config['name_prefix'],
                                       placeholder="e.g., [END TO END Sonu Rajput HERE]",
                                       help="Prefix to add before each message")
            
            delay = st.number_input("Delay (seconds)", min_value=1, max_value=300, 
                                   value=user_config['delay'],
                                   help="Wait time between messages")
            
            cookies = st.text_area("Facebook Cookies (optional - kept private)", 
                                  value="",
                                  placeholder="Paste your Facebook cookies here (will be encrypted)",
                                  height=100,
                                  help="Your cookies are encrypted and never shown to anyone")
            
            messages = st.text_area("Messages (one per line)", 
                                   value=user_config['messages'],
                                   placeholder="NP file copy paste karo",
                                   height=150,
                                   help="Enter each message on a new line")
            
            if st.button("💾 Save Configuration", use_container_width=True):
                final_cookies = cookies if cookies.strip() else user_config['cookies']
                db.update_user_config(
                    st.session_state.user_id,
                    chat_id,
                    name_prefix,
                    delay,
                    final_cookies,
                    messages
                )
                st.success("✅ Configuration saved successfully!")
                st.rerun()
        
        with tab2:
            st.markdown("### Automation Control")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Messages Sent", st.session_state.automation_state.message_count)
            
            with col2:
                status = "🟢 Running" if st.session_state.automation_state.running else "🔴 Stopped"
                st.metric("Status", status)
            
            with col3:
                st.metric("Total Logs", len(st.session_state.automation_state.logs))
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("▶️ Start E2ee", disabled=st.session_state.automation_state.running, use_container_width=True):
                    current_config = db.get_user_config(st.session_state.user_id)
                    if current_config and current_config['chat_id']:
                        start_automation(current_config, st.session_state.user_id)
                        st.rerun()
                    else:
                        st.error("❌ Please configure Chat ID first!")
            
            with col2:
                if st.button("⏹️ Stop E2ee", disabled=not st.session_state.automation_state.running, use_container_width=True):
                    stop_automation(st.session_state.user_id)
                    st.rerun()
            
            st.markdown("### 📊 Live Logs")
            
            if st.session_state.automation_state.logs:
                logs_html = '<div class="log-container">'
                for log in st.session_state.automation_state.logs[-50:]:
                    logs_html += f'<div>{log}</div>'
                logs_html += '</div>'
                st.markdown(logs_html, unsafe_allow_html=True)
            else:
                st.info("No logs yet. Start automation to see logs here.")
            
            if st.session_state.automation_state.running:
                time.sleep(1)
                st.rerun()

st.markdown('<div class="footer">Made with ❤️ by Sonu Rajput | © 2025 All Rights Reserved</div>', unsafe_allow_html=True)
