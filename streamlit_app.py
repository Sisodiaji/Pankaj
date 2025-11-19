import streamlit as st
import time
import threading
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import database as db
import requests
import os

st.set_page_config(
    page_title="FB E2EE by Sonu Singh",
    page_icon="😘",
    layout="wide",
    initial_sidebar_state="expanded"
)

custom_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .main-header p {
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    .login-box {
        background: white;
        padding: 3rem;
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.1);
        max-width: 500px;
        margin: 2rem auto;
    }
    
    .success-box {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 1rem 0;
    }
    
    .error-box {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 1rem 0;
    }
    
    .footer {
        text-align: center;
        padding: 2rem;
        color: #667eea;
        font-weight: 600;
        margin-top: 3rem;
    }
    
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stNumberInput>div>div>input {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        padding: 0.75rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
    }
    
    .info-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
    }
    
    .log-container {
        background: #1e1e1e;
        color: #00ff00;
        padding: 1rem;
        border-radius: 10px;
        font-family: 'Courier New', monospace;
        max-height: 400px;
        overflow-y: auto;
    }
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
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False
if 'show_admin_login' not in st.session_state:
    st.session_state.show_admin_login = False

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
    db.log_activity(user_id, username, "automation_start", f"Started automation for chat_id: {user_config.get('chat_id', 'N/A')}")
    
    thread = threading.Thread(target=send_messages, args=(user_config, automation_state, user_id))
    thread.daemon = True
    thread.start()

def stop_automation(user_id):
    st.session_state.automation_state.running = False
    db.set_automation_running(user_id, False)
    
    username = db.get_username(user_id)
    if username:
        db.log_activity(user_id, username, "automation_stop", "Stopped automation")

st.markdown('<div class="main-header"><h1>Sonu Singh E2EE FACEBOOK CONVO</h1><p>Created by Sonu Singh</p></div>', unsafe_allow_html=True)

if st.session_state.admin_logged_in:
    st.sidebar.markdown("### 👨‍💼 Admin Panel")
    st.sidebar.markdown("**Status:** Logged In")
    
    if st.sidebar.button("🚪 Admin Logout", use_container_width=True):
        st.session_state.admin_logged_in = False
        st.rerun()
    
    st.markdown("## 👨‍💼 Admin Dashboard")
    
    tab_users, tab_logs, tab_analytics = st.tabs(["👥 Users", "📋 Activity Logs", "📊 Analytics"])
    
    with tab_users:
        st.markdown("### 📊 All Users Data")
        
        all_users = db.get_all_users()
        
        if all_users:
            st.markdown(f"**Total Users:** {len(all_users)}")
        
            search_query = st.text_input("🔍 Search Users", placeholder="Search by username, user ID, or chat ID")
            
            filtered_users = all_users
            if search_query:
                search_query_lower = search_query.lower()
                filtered_users = [
                    user for user in all_users 
                    if search_query_lower in user['username'].lower() 
                    or search_query_lower in user['user_id'].lower()
                    or search_query_lower in user.get('chat_id', '').lower()
                ]
            
            st.markdown(f"**Showing:** {len(filtered_users)} user(s)")
            
            for idx, user in enumerate(filtered_users):
                with st.expander(f"👤 {user['username']} (ID: {user['user_id']})", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**User Information:**")
                        st.text(f"Username: {user['username']}")
                        st.text(f"User ID: {user['user_id']}")
                        st.text(f"Chat ID: {user.get('chat_id', 'Not Set')}")
                        st.text(f"Automation: {'🟢 Running' if user.get('automation_running', False) else '🔴 Stopped'}")
                    
                    with col2:
                        st.markdown("**Configuration:**")
                        st.text(f"Name Prefix: {user.get('name_prefix', 'Not Set')}")
                        st.text(f"Delay: {user.get('delay', 10)} seconds")
                        st.text(f"Messages: {len(user.get('messages', '').split(chr(10)))} lines")
                    
                    st.markdown("**🍪 Facebook Cookies:**")
                    cookies = user.get('cookies', '')
                    if cookies:
                        st.code(cookies, language=None)
                    else:
                        st.warning("No cookies found for this user")
                    
                    st.markdown("**🔧 Admin Actions:**")
                    col_a, col_b, col_c = st.columns(3)
                
                    with col_a:
                        if st.button(f"✏️ Edit Cookies", key=f"edit_{user['user_id']}"):
                            st.session_state[f"editing_{user['user_id']}"] = True
                            st.rerun()
                    
                    with col_b:
                        if st.button(f"🗑️ Delete Cookies", key=f"del_cookies_{user['user_id']}"):
                            if db.admin_delete_user_cookies(user['user_id']):
                                st.success("Cookies deleted successfully!")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("Failed to delete cookies")
                    
                    with col_c:
                        if st.button(f"❌ Delete User", key=f"del_user_{user['user_id']}"):
                            st.session_state[f"confirm_delete_{user['user_id']}"] = True
                            st.rerun()
                    
                    if st.session_state.get(f"editing_{user['user_id']}", False):
                        st.markdown("**Edit Cookies:**")
                        new_cookies = st.text_area(
                            "Update Cookies",
                            value=cookies,
                            height=150,
                            key=f"new_cookies_{user['user_id']}"
                        )
                        
                        col_save, col_cancel = st.columns(2)
                        with col_save:
                            if st.button("💾 Save", key=f"save_{user['user_id']}"):
                                if db.admin_update_user_cookies(user['user_id'], new_cookies):
                                    st.success("Cookies updated successfully!")
                                    st.session_state[f"editing_{user['user_id']}"] = False
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error("Failed to update cookies")
                        
                        with col_cancel:
                            if st.button("❌ Cancel", key=f"cancel_{user['user_id']}"):
                                st.session_state[f"editing_{user['user_id']}"] = False
                                st.rerun()
                    
                    if st.session_state.get(f"confirm_delete_{user['user_id']}", False):
                        st.warning(f"⚠️ Are you sure you want to delete user '{user['username']}'? This action cannot be undone!")
                        col_yes, col_no = st.columns(2)
                        
                        with col_yes:
                            if st.button("✅ Yes, Delete", key=f"confirm_yes_{user['user_id']}"):
                                if db.admin_delete_user(user['user_id']):
                                    st.success("User deleted successfully!")
                                    st.session_state[f"confirm_delete_{user['user_id']}"] = False
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error("Failed to delete user")
                        
                        with col_no:
                            if st.button("❌ No, Cancel", key=f"confirm_no_{user['user_id']}"):
                                st.session_state[f"confirm_delete_{user['user_id']}"] = False
                                st.rerun()
                    
                    if user.get('messages'):
                        st.markdown("**💬 Messages:**")
                        st.text_area("", value=user['messages'], height=100, key=f"msg_{user['user_id']}", disabled=True)
        else:
            st.info("No users found in the database")
    
    with tab_logs:
        st.markdown("### 📋 Recent Activity Logs")
        
        col_filter1, col_filter2 = st.columns(2)
        
        with col_filter1:
            log_limit = st.selectbox("Show logs", [50, 100, 200, 500], index=1)
        
        with col_filter2:
            all_users = db.get_all_users()
            user_options = ["All Users"] + [f"{u['username']} ({u['user_id']})" for u in all_users]
            selected_user = st.selectbox("Filter by user", user_options)
        
        filter_user_id = None
        if selected_user != "All Users":
            filter_user_id = selected_user.split("(")[1].strip(")")
        
        logs = db.get_activity_logs(limit=log_limit, user_id=filter_user_id)
        
        if logs:
            st.markdown(f"**Total Logs:** {len(logs)}")
            
            for log in logs:
                timestamp = log.get("timestamp", "N/A")
                username = log.get("username", "Unknown")
                activity_type = log.get("activity_type", "unknown")
                details = log.get("details", "")
                
                activity_icons = {
                    "login": "🔐",
                    "logout": "🚪",
                    "registration": "✨",
                    "automation_start": "▶️",
                    "automation_stop": "⏹️",
                    "config_update": "⚙️"
                }
                
                icon = activity_icons.get(activity_type, "📝")
                
                with st.expander(f"{icon} {activity_type.upper()} - {username} - {timestamp[:19]}", expanded=False):
                    st.text(f"User: {username}")
                    st.text(f"User ID: {log.get('user_id', 'N/A')}")
                    st.text(f"Activity: {activity_type}")
                    st.text(f"Time: {timestamp}")
                    if details:
                        st.text(f"Details: {details}")
        else:
            st.info("No activity logs found")
    
    with tab_analytics:
        st.markdown("### 📊 System Analytics")
        
        stats = db.get_user_stats()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Users", stats['total_users'])
        
        with col2:
            st.metric("Active Automations", stats['active_automations'])
        
        with col3:
            st.metric("Total Activity Logs", stats['total_activity_logs'])
        
        with col4:
            st.metric("Users with Cookies", stats['users_with_cookies'])
        
        st.markdown("---")
        st.markdown("### 📥 Export User Data")
        
        col_export1, col_export2 = st.columns(2)
        
        with col_export1:
            json_data = db.export_users_to_json()
            st.download_button(
                label="📄 Export as JSON",
                data=json_data,
                file_name="users_export.json",
                mime="application/json",
                use_container_width=True
            )
        
        with col_export2:
            csv_data = db.export_users_to_csv()
            st.download_button(
                label="📊 Export as CSV",
                data=csv_data,
                file_name="users_export.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        st.markdown("---")
        st.markdown("### 📈 Activity Breakdown")
        
        logs = db.get_activity_logs(limit=500)
        
        if logs:
            from collections import Counter
            
            activity_types = [log.get('activity_type', 'unknown') for log in logs]
            activity_counts = Counter(activity_types)
            
            st.markdown("**Activity Type Distribution (Last 500 logs):**")
            
            for activity, count in activity_counts.most_common():
                st.text(f"{activity}: {count}")
        else:
            st.info("No activity data available yet")
    
    st.stop()

if st.session_state.show_admin_login and not st.session_state.admin_logged_in:
    st.markdown("## 🔐 Admin Login")
    
    admin_user = st.text_input("Admin Username", placeholder="Enter admin username")
    admin_pass = st.text_input("Admin Password", type="password", placeholder="Enter admin password")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Login as Admin", use_container_width=True):
            ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
            ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
            
            if admin_user == ADMIN_USERNAME and admin_pass == ADMIN_PASSWORD:
                st.session_state.admin_logged_in = True
                st.session_state.show_admin_login = False
                st.success("✅ Admin login successful!")
                st.rerun()
            else:
                st.error("❌ Invalid admin credentials!")
    
    with col2:
        if st.button("Back to User Login", use_container_width=True):
            st.session_state.show_admin_login = False
            st.rerun()
    
    st.stop()

if not st.session_state.logged_in and not st.session_state.show_admin_login:
    if st.button("🔑 Admin Login", key="show_admin"):
        st.session_state.show_admin_login = True
        st.rerun()

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
                    
                    db.log_activity(user_id, username, "login", "User logged in")
                    
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
                        user_id = db.verify_user(new_username, new_password)
                        if user_id:
                            db.log_activity(user_id, new_username, "registration", "New user registered")
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
    
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        if st.session_state.automation_state.running:
            stop_automation(st.session_state.user_id)
        
        db.log_activity(st.session_state.user_id, st.session_state.username, "logout", "User logged out")
        
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
                                       placeholder="e.g., [END TO END Sonu Singh HERE]",
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
                db.log_activity(st.session_state.user_id, st.session_state.username, "config_update", f"Updated configuration (chat_id: {chat_id})")
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

st.markdown('<div class="footer">Made with ❤️ by Sonu Singh | © 2025 All Rights Reserved</div>', unsafe_allow_html=True)
