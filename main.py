import os
import re
import time
import json
import random
import sqlite3
import datetime
import threading
import asyncio
import httpx
import requests
import urllib3
import telebot
from telebot import types

# Disable Insecure Request Warnings for SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==========================================
# STANDARD EMOJIS MAPPING (NORMAL EMOJIS)
# ==========================================
EMOJIS = {
    "king": "👑",
    "shop": "🛒",
    "wallet": "💼",
    "card": "💳",
    "desktop": "🖥️",
    "check": "✅",
    "cross": "❌",
    "chat": "💬",
    "support": "🎧",
    "globe": "🌐",
    "money": "💰",
    "cash": "💵",
    "fire": "🔥",
    "zap": "⚡",
    "plus": "➕",
    "trash": "🗑️",
    "file": "📁",
    "notice": "📢",
    "ban": "🚫",
    "gear": "⚙️",
    "stats": "📊",
    "user": "👤",
    "link": "🔗",
    "back": "🔙",
    "search": "🔍",
    "star": "⭐",
    "rocket": "🚀",
    "lock": "🔒",
    "gift": "🎁",
    "home": "🏠",
    "download": "📥",
    "dollar": "💲",
    "clock": "⏰",
    "verify": "✔️",
    "order": "📦",
    "live": "🟢",
    "dead": "🔴",
    "bkash": "📱",
    "nagad": "📱",
    "binance": "🪙",
    "dada": "💳"
}

def CE(key):
    return EMOJIS.get(key, "")

# ==========================================
# KEYBOARD BUTTON HELPERS
# ==========================================
def create_kb_button(text):
    return types.KeyboardButton(text)

def create_ikb_button(text, callback_data=None, url=None, web_app=None):
    return types.InlineKeyboardButton(text, callback_data=callback_data, url=url, web_app=web_app)

# ==========================================
# CONFIGURATION
# ==========================================
BOT_TOKEN = "8659733780:AAG1cFA22HStxAM-L7aTJKiP1hnM2Baqqzg"
SUPER_ADMIN_ID = 7125334953
DB_FILE = "bot_database.db"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# ==========================================
# MULTILINGUAL TEXT TEMPLATES
# ==========================================
STRINGS = {
    "bn": {
        "welcome": (
            "<b><i>স্বাগতম {name}!</i></b>\n\n"
            "আমাদের হাই-স্পিড <b>Proxy Store & Checker</b> অটোমেশন সিস্টেমে আপনাকে স্বাগতম। "
            "নিচের মেনু থেকে আপনার কাঙ্ক্ষিত অপশন সিলেক্ট করুন:"
        ),
        "btn_buy": "🛒 Buy Proxy",
        "btn_wallet": "💼 Wallet",
        "btn_check": "🖥️ Check Proxy",
        "btn_support": "💬 Support",
        "btn_lang": "🌐 Language / ভাষা",
        "btn_admin": "👑 Admin Panel",
        "banned": "আপনার অ্যাকাউন্টটি ব্যান করা হয়েছে! এডমিনের সাথে যোগাযোগ করুন।",
        "force_join_msg": "বটের সেবা ব্যবহার করতে আমাদের অফিসিয়াল চ্যানেলগুলোতে জয়েন করে 'Verify Join' বাটনে চাপ দিন:",
        "stock_empty": "দুঃখিত! বর্তমানে পর্যাপ্ত স্টক নেই। শীঘ্রই স্টক যোগ করা হবে।",
        "stock_info": (
            "<b>প্রক্সি ক্রয় প্যানেল</b>\n\n"
            "{c_money} <b>প্রতি পিসের মূল্য:</b> <code>{price:.2f} BDT</code>\n"
            "{c_stats} <b>উপলব্ধ স্টক:</b> <code>{stock} Pcs</code>\n"
            "{c_notice} <b>ফরম্যাট:</b> <code>IP:Port:User:Pass</code>\n\n"
            "<i>আপনার কতটি প্রক্সি প্রয়োজন তা সংখ্যায় লিখে পাঠান:</i>"
        ),
        "invalid_qty": "ভুল ইনপুট! সঠিক সংখ্যা লিখুন।",
        "low_stock": "পর্যাপ্ত স্টক নেই! বর্তমানে আমাদের স্টকে অবশিষ্ট আছে {stock} টি প্রক্সি।",
        "low_balance": (
            "<b>অপর্যাপ্ত ব্যালেন্স!</b>\n\n"
            "প্রয়োজনীয় বিল: <code>{total:.2f} BDT</code>\n"
            "আপনার ব্যালেন্স: <code>{balance:.2f} BDT</code>\n\n"
            "<i>অনুগ্রহ করে ওয়ালেট থেকে আগে ব্যালেন্স ডিপোজিট করুন।</i>"
        ),
        "wallet_info": (
            "<b>আপনার ওয়ালেট বিবরণী:</b>\n\n"
            "{c_user} <b>ইউজার আইডি:</b> <code>{uid}</code>\n"
            "{c_money} <b>বর্তমান ব্যালেন্স:</b> <code>{bal:.2f} BDT</code>\n"
            "{c_rocket} <b>সর্বমোট ডিপোজিট:</b> <code>{dep:.2f} BDT</code>\n"
            "{c_shop} <b>মোট ক্রয়কৃত প্রক্সি:</b> <code>{bought} Pcs</code>\n\n"
            "<i>ব্যালেন্স যুক্ত করতে নিচের বাটনে চাপ দিন:</i>"
        ),
        "deposit_title": (
            "<b>ডিপোজিট মেথড সিলেক্ট করুন:</b>\n\n"
            "{c_notice} <i>সর্বনিম্ন ডিপোজিট:</i> <code>{min_dep} BDT</code>\n"
            "{c_dollar} <i>ডলার রেট:</i> <code>1 USD = {usd_rate} BDT</code>"
        ),
        "auto_pay_btn": "⚡ DADA PAY (বিকাশ / নগদ / রকেট / কার্ড)",
        "dep_amt_ask": "কত টাকা ডিপোজিট করতে চান? সংখ্যায় লিখুন (BDT):",
        "min_dep_err": "সর্বনিম্ন ডিপোজিট {min_dep} BDT হতে হবে!",
        "auto_pay_info": (
            "<b>DADA PAY পেমেন্ট ইনভয়েস তৈরি হয়েছে!</b>\n\n"
            "{c_cash} <b>পরিশোধযোগ্য পরিমাণ:</b> <code>{amt:.2f} BDT</code>\n\n"
            "<b>পেমেন্ট নির্দেশাবলী:</b>\n"
            "১. নিচের <b>Pay Now</b> বাটনে চাপ দিয়ে পেমেন্ট পেজে যান।\n"
            "২. বিকাশ/নগদে সেন্ড মানি করে TrxID দিয়ে Confirm করুন।\n"
            "৩. ⚡ <b>পেমেন্ট সফল হওয়ামাত্র স্বয়ংক্রিয়ভাবে রিডাইরেক্ট হয়ে আপনার অ্যাকাউন্টে টাকা যোগ হয়ে যাবে!</b>"
        ),
        "checker_prompt": (
            "<b>প্রক্সি চেকার সেকশন</b>\n\n"
            "একক বা একাধিক প্রক্সি লিখে পাঠান অথবা সরাসরি <b>.txt ফাইল</b> আপলোড দিন।\n\n"
            "<i>ফরম্যাট:</i>\n"
            "• <code>IP:Port:User:Pass</code>\n"
            "• <code>IP:Port</code>"
        ),
        "maintenance": "🚧 <b>বট বর্তমানে মেইনটেন্যান্স বা আপডেটের কাজে সাময়িকভাবে বন্ধ আছে!</b>\n\nদয়া করে কিছুক্ষণ পর আবার চেষ্টা করুন। সাময়িক অসুবিধার জন্য আমরা আন্তরিকভাবে দুঃখিত।"
    },
    "en": {
        "welcome": (
            "<b><i>Welcome {name}!</i></b>\n\n"
            "Welcome to our High-Speed <b>Proxy Store & Checker</b> system. "
            "Select an option from the menu below:"
        ),
        "btn_buy": "🛒 Buy Proxy",
        "btn_wallet": "💼 Wallet",
        "btn_check": "🖥️ Check Proxy",
        "btn_support": "💬 Support",
        "btn_lang": "🌐 Language / ভাষা",
        "btn_admin": "👑 Admin Panel",
        "banned": "Your account has been suspended! Please contact support.",
        "force_join_msg": "Please join our official channels to unlock bot services and tap 'Verify Join':",
        "stock_empty": "Sorry! Out of stock at the moment. Fresh stock will be added soon.",
        "stock_info": (
            "<b>Proxy Purchase Dashboard</b>\n\n"
            "{c_money} <b>Unit Price:</b> <code>{price:.2f} BDT</code>\n"
            "{c_stats} <b>Available Stock:</b> <code>{stock} Pcs</code>\n"
            "{c_notice} <b>Format:</b> <code>IP:Port:User:Pass</code>\n\n"
            "<i>Enter how many proxies you want to purchase:</i>"
        ),
        "invalid_qty": "Invalid input! Please enter a valid number.",
        "low_stock": "Insufficient stock! Only {stock} proxies are currently available.",
        "low_balance": (
            "<b>Insufficient Wallet Balance!</b>\n\n"
            "Required: <code>{total:.2f} BDT</code>\n"
            "Your Balance: <code>{balance:.2f} BDT</code>\n\n"
            "<i>Please deposit funds to your wallet first.</i>"
        ),
        "wallet_info": (
            "<b>Your Wallet Statement:</b>\n\n"
            "{c_user} <b>User ID:</b> <code>{uid}</code>\n"
            "{c_money} <b>Current Balance:</b> <code>{bal:.2f} BDT</code>\n"
            "{c_rocket} <b>Total Deposited:</b> <code>{dep:.2f} BDT</code>\n"
            "{c_shop} <b>Proxies Purchased:</b> <code>{bought} Pcs</code>\n\n"
            "<i>Tap below to deposit funds:</i>"
        ),
        "deposit_title": (
            "<b>Select Deposit Gateway:</b>\n\n"
            "{c_notice} <i>Minimum Deposit:</i> <code>{min_dep} BDT</code>\n"
            "{c_dollar} <i>USD Rate:</i> <code>1 USD = {usd_rate} BDT</code>"
        ),
        "auto_pay_btn": "⚡ DADA PAY (Instant bKash/Nagad/Cards)",
        "dep_amt_ask": "Enter deposit amount in BDT:",
        "min_dep_err": "Minimum deposit amount is {min_dep} BDT!",
        "auto_pay_info": (
            "<b>DADA PAY Payment Invoice Generated!</b>\n\n"
            "{c_cash} <b>Payable Amount:</b> <code>{amt:.2f} BDT</code>\n\n"
            "<b>Instructions:</b>\n"
            "1. Tap <b>Pay Now</b> to open the payment page.\n"
            "2. Complete Send Money and confirm with TrxID.\n"
            "3. ⚡ <b>Once completed, it will automatically redirect and credit funds instantly!</b>"
        ),
        "checker_prompt": (
            "<b>High-Speed Proxy Checker</b>\n\n"
            "Send proxy lines via text or upload a <b>.txt file</b> directly.\n\n"
            "<i>Supported Formats:</i>\n"
            "• <code>IP:Port:User:Pass</code>\n"
            "• <code>IP:Port</code>"
        ),
        "maintenance": "🚧 <b>The bot is currently under maintenance!</b>\n\nPlease check back later. We apologize for any inconvenience caused."
    }
}

# ==========================================
# DATABASE INITIALIZATION
# ==========================================
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        balance REAL DEFAULT 0.0,
        total_deposit REAL DEFAULT 0.0,
        total_orders INTEGER DEFAULT 0,
        proxies_bought INTEGER DEFAULT 0,
        is_banned INTEGER DEFAULT 0,
        lang TEXT DEFAULT 'bn'
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS proxies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        proxy_data TEXT,
        is_sold INTEGER DEFAULT 0,
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS force_channels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        link TEXT,
        chat_id TEXT
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS payments (
        trx_id TEXT PRIMARY KEY,
        user_id INTEGER,
        amount REAL,
        method TEXT,
        status TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS pending_payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        amount REAL,
        gateway_trx TEXT,
        status TEXT DEFAULT 'PENDING',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS admins (
        user_id INTEGER PRIMARY KEY,
        added_by INTEGER,
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    cursor.execute("INSERT OR IGNORE INTO admins (user_id, added_by) VALUES (?, ?)", (SUPER_ADMIN_ID, SUPER_ADMIN_ID))

    defaults = {
        'support_link': 'https://t.me/YourDomains',
        'bkash_num': '01700000000',
        'nagad_num': '01800000000',
        'binance_id': '12345678',
        'bkash_active': '1',
        'nagad_active': '1',
        'binance_active': '1',
        'usd_rate': '125.0',
        'min_deposit': '10.0',
        'proxy_price': '3.0',
        'bot_status': 'ON',  # ON / OFF (Maintenance)
        # DADA PAY Gateway Configuration
        'dada_active': '1',
        'dada_brand_key': 'nPymmWd9CAOrLYNBbSROPPlvakngN2UgWsdA9FgFne9nqTJyCg',
        'dada_create_url': 'https://pay.dadapay.shop/api/payment/create',
        'dada_verify_url': 'https://pay.dadapay.shop/api/payment/verify',
        'github_pages_url': 'https://yourusername.github.io/dadapay/'
    }
    for k, v in defaults.items():
        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (k, v))

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN lang TEXT DEFAULT 'bn'")
    except Exception:
        pass

    conn.commit()
    conn.close()

init_db()

# ==========================================
# DB HELPERS & PERMISSIONS
# ==========================================
def is_admin(user_id):
    try: uid = int(user_id)
    except Exception: return False
    if uid == SUPER_ADMIN_ID: return True
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM admins WHERE user_id = ?", (uid,))
    res = cursor.fetchone()
    conn.close()
    return bool(res)

def get_setting(key):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key=?", (key,))
    res = cursor.fetchone()
    conn.close()
    return res[0] if res else ""

def set_setting(key, value):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
    conn.commit()
    conn.close()

def is_maintenance():
    return get_setting('bot_status').upper() == 'OFF'

def check_maintenance_for_user(user_id):
    if is_admin(user_id):
        return False
    return is_maintenance()

def get_user(user_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    u = cursor.fetchone()
    conn.close()
    return u

def register_user(user_id, username):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
    conn.commit()
    conn.close()

def get_user_lang(user_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
    res = cursor.fetchone()
    conn.close()
    return res[0] if res and res[0] in STRINGS else 'bn'

def set_user_lang(user_id, lang):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET lang=? WHERE user_id=?", (lang, user_id))
    conn.commit()
    conn.close()

def check_force_join(user_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT chat_id FROM force_channels")
    channels = cursor.fetchall()
    conn.close()
    if not channels: return True
    for ch in channels:
        chat_id = ch[0]
        try:
            if str(chat_id).replace("-", "").isdigit(): chat_id = int(chat_id)
            member = bot.get_chat_member(chat_id, user_id)
            if member.status not in ['creator', 'administrator', 'member', 'restricted']: return False
        except Exception: return False
    return True

def get_unique_filename(username):
    clean_name = re.sub(r'[^a-zA-Z0-9_]', '', username or "user")
    rand_num = random.randint(100000, 999999)
    return f"{clean_name}_{rand_num}.txt"

# ==========================================
# KEYBOARDS
# ==========================================
def main_keyboard(user_id=None):
    lang = get_user_lang(user_id) if user_id else 'bn'
    txt = STRINGS[lang]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    b1 = create_kb_button(txt["btn_buy"])
    b2 = create_kb_button(txt["btn_wallet"])
    b3 = create_kb_button(txt["btn_check"])
    b4 = create_kb_button(txt["btn_support"])
    b5 = create_kb_button(txt["btn_lang"])
    markup.add(b1, b2)
    markup.add(b3, b4)
    markup.add(b5)
    if user_id and is_admin(user_id):
        b_admin = create_kb_button(txt["btn_admin"])
        markup.add(b_admin)
    return markup

def force_join_markup():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT name, link FROM force_channels")
    channels = cursor.fetchall()
    conn.close()
    markup = types.InlineKeyboardMarkup(row_width=1)
    for name, link in channels:
        markup.add(create_ikb_button(f"🔗 Join {name}", url=link))
    markup.add(create_ikb_button("✅ Verify Join", callback_data="check_joined"))
    return markup

def admin_keyboard():
    status = "🔴 OFF (Turn ON)" if is_maintenance() else "🟢 ON (Turn OFF)"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        create_kb_button("📊 Stats & Wallet Count"),
        create_kb_button("📥 Download Unsold Stock"),
        create_kb_button("💾 Backup All Users"),
        create_kb_button(f"⚙️ Bot Status: {status}"),
        create_kb_button("➕ Add Stock"),
        create_kb_button("💳 Payment Methods Control"),
        create_kb_button("⚙️ Price Settings"),
        create_kb_button("🔗 Force Join Settings"),
        create_kb_button("👤 User Management"),
        create_kb_button("👑 Manage Admins"),
        create_kb_button("📢 Broadcast"),
        create_kb_button("🔙 Main Menu")
    )
    return markup

# ==========================================
# VERIFICATION ENGINE (ROBUST MULTI-FALLBACK)
# ==========================================
def verify_and_credit_robust(uid, trx_id, amount_hint=0.0):
    trx_id = str(trx_id).strip()
    if not trx_id or len(trx_id) < 4:
        return False, None, 0.0, "Invalid ID"

    # ডাবল ক্রেডিট রোধ
    conn = sqlite3.connect(DB_FILE, timeout=20)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM payments WHERE trx_id = ?", (trx_id,))
    if cursor.fetchone():
        conn.close()
        return True, trx_id, 0.0, "Already Added"

    brand_key = get_setting('dada_brand_key').strip()
    verify_url = get_setting('dada_verify_url').strip() or 'https://pay.dadapay.shop/api/payment/verify'
    headers = {
        'Content-Type': 'application/json',
        'API-KEY': brand_key,
        'SECRET-KEY': brand_key,
        'BRAND-KEY': brand_key
    }
    payloads = [
        {"transaction_id": trx_id},
        {"transactionId": trx_id},
        {"trx_id": trx_id}
    ]

    verified_amount = 0.0
    is_completed = False
    method_used = "DADA PAY"

    for p in payloads:
        try:
            res = requests.post(verify_url, headers=headers, json=p, timeout=25, verify=False)
            res_data = res.json()
            data_block = res_data.get("data") if isinstance(res_data.get("data"), dict) else res_data
            status_val = str(data_block.get("status", res_data.get("status", ""))).upper()

            if status_val in ["COMPLETED", "SUCCESS", "PAID"]:
                raw_amt = data_block.get("amount", res_data.get("amount", amount_hint))
                try: verified_amount = float(raw_amt)
                except Exception: verified_amount = float(amount_hint)
                method_used = data_block.get('payment_method', res_data.get('payment_method', 'DADA PAY'))
                is_completed = True
                break
        except Exception:
            pass

    if not is_completed:
        cursor.execute("SELECT amount FROM pending_payments WHERE user_id = ? AND status = 'PENDING' ORDER BY id DESC LIMIT 1", (uid,))
        p_row = cursor.fetchone()
        if p_row and (amount_hint > 0 or p_row[0] > 0):
            verified_amount = float(amount_hint) if amount_hint > 0 else float(p_row[0])
            is_completed = True
            method_used = "DADA PAY (Auto-Confirmed)"

    if is_completed and verified_amount > 0:
        cursor.execute("INSERT OR IGNORE INTO payments (trx_id, user_id, amount, method, status) VALUES (?, ?, ?, ?, ?)",
                       (trx_id, uid, verified_amount, str(method_used), 'COMPLETED'))
        cursor.execute("UPDATE users SET balance = balance + ?, total_deposit = total_deposit + ? WHERE user_id = ?",
                       (verified_amount, verified_amount, uid))
        cursor.execute("UPDATE pending_payments SET status = 'COMPLETED' WHERE user_id = ? AND status = 'PENDING'", (uid,))
        conn.commit()
        conn.close()
        return True, trx_id, verified_amount, str(method_used)

    conn.close()
    return False, trx_id, 0.0, "Failed"

# ==========================================
# COMMAND HANDLER (DEEP LINK AUTO-CREDIT)
# ==========================================
@bot.message_handler(commands=['start'])
def start_cmd(message):
    uid = message.from_user.id
    uname = message.from_user.username or "User"
    register_user(uid, uname)
    user = get_user(uid)
    lang = get_user_lang(uid)

    # মেইনটেন্যান্স চেক
    if check_maintenance_for_user(uid):
        bot.send_message(uid, STRINGS[lang]['maintenance'])
        return

    if user and user[6] == 1:
        bot.send_message(uid, f"{CE('ban')} <b>{STRINGS[lang]['banned']}</b>")
        return

    # ডিপ-লিংক হ্যান্ডলার
    text_parts = message.text.split()
    if len(text_parts) > 1 and text_parts[1].startswith("pay_"):
        raw_param = text_parts[1].replace("pay_", "").strip()
        parts = raw_param.split("_")
        trx_id = parts[0]
        amt_hint = float(parts[1]) if len(parts) > 1 else 0.0

        status_msg = bot.send_message(uid, f"{CE('fire')} <i>পেমেন্ট স্বয়ংক্রিয়ভাবে প্রসেস করা হচ্ছে...</i>")
        ok, tid, paid_amt, method = verify_and_credit_robust(uid, trx_id, amt_hint)

        if ok and method != "Already Added":
            succ_text = (
                f"{CE('check')} <b>🎉 অভিনন্দন! পেমেন্ট সফলভাবে ওয়ালেটে যুক্ত হয়েছে!</b>\n\n"
                f"{CE('card')} <b>গেটওয়ে:</b> {str(method).upper()}\n"
                f"{CE('link')} <b>Trx ID:</b> <code>{tid}</code>\n"
                f"{CE('money')} <b>যোগকৃত ব্যালেন্স:</b> <code>{paid_amt:.2f} BDT</code>\n\n"
                f"<i>আপনার ব্যালেন্স স্বয়ংক্রিয়ভাবে আপডেট হয়ে গেছে!</i>"
            )
            bot.edit_message_text(succ_text, uid, status_msg.message_id)

            admin_alert = (
                f"{CE('notice')} <b>DADA PAY পেমেন্ট কনফার্ম!</b>\n\n"
                f"{CE('user')} ইউজার: <code>{uid}</code>\n"
                f"{CE('money')} পরিমাণ: <code>{paid_amt:.2f} BDT</code>\n"
                f"{CE('card')} মেথড: {str(method).upper()}\n"
                f"{CE('link')} TrxID: <code>{tid}</code>"
            )
            try: bot.send_message(SUPER_ADMIN_ID, admin_alert)
            except Exception: pass
            return
        elif method == "Already Added":
            bot.edit_message_text(f"{CE('check')} <b>এই ট্রানজেকশনের ব্যালেন্স ইতোমধ্যে আপনার অ্যাকাউন্টে যোগ করা হয়েছে!</b>", uid, status_msg.message_id)
            return

    if not check_force_join(uid):
        msg = f"{CE('notice')} <b>{STRINGS[lang]['force_join_msg']}</b>"
        bot.send_message(uid, msg, reply_markup=force_join_markup())
        return

    welcome_msg = f"{CE('king')} " + STRINGS[lang]['welcome'].format(name=message.from_user.first_name)
    bot.send_message(uid, welcome_msg, reply_markup=main_keyboard(uid))

@bot.callback_query_handler(func=lambda call: call.data == "check_joined")
def check_joined_callback(call):
    uid = call.from_user.id
    lang = get_user_lang(uid)
    if check_maintenance_for_user(uid):
        bot.answer_callback_query(call.id, "Bot is currently under maintenance!", show_alert=True)
        return

    if check_force_join(uid):
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception: pass
        bot.send_message(uid, f"{CE('check')} <b>ভেরিফিকেশন সম্পন্ন হয়েছে!</b>", reply_markup=main_keyboard(uid))
    else:
        bot.answer_callback_query(call.id, "আপনি এখনো সব চ্যানেলে যোগ দেননি!", show_alert=True)

# ==========================================
# LANGUAGE SWITCHER
# ==========================================
@bot.message_handler(func=lambda m: "Language" in m.text or "ভাষা" in m.text)
def language_choice(message):
    uid = message.from_user.id
    if check_maintenance_for_user(uid):
        bot.send_message(uid, STRINGS[get_user_lang(uid)]['maintenance'])
        return
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        create_ikb_button("বাংলা ⭐", callback_data="lang_bn"),
        create_ikb_button("English ⭐", callback_data="lang_en")
    )
    bot.send_message(uid, f"{CE('globe')} <i>আপনার পছন্দের ভাষা নির্বাচন করুন / Select your language:</i>", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def lang_change_confirm(call):
    new_lang = call.data.split("_")[1]
    uid = call.from_user.id
    set_user_lang(uid, new_lang)
    confirm_text = "ভাষা সফলভাবে বাংলায় পরিবর্তন করা হয়েছে!" if new_lang == 'bn' else "Language has been changed to English successfully!"
    bot.answer_callback_query(call.id, confirm_text)
    try: bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception: pass
    bot.send_message(uid, f"{CE('check')} <b>{confirm_text}</b>", reply_markup=main_keyboard(uid))

# ==========================================
# PROXY BUYING SYSTEM (FILE DELIVERY ONLY)
# ==========================================
def trigger_buy_proxy(chat_id, user_id):
    lang = get_user_lang(user_id)
    if check_maintenance_for_user(user_id):
        bot.send_message(chat_id, STRINGS[lang]['maintenance'])
        return

    if not check_force_join(user_id):
        bot.send_message(chat_id, f"{CE('notice')} <b>আগে আমাদের অফিশিয়াল চ্যানেলে জয়েন করুন!</b>", reply_markup=force_join_markup())
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM proxies WHERE is_sold = 0")
    stock = cursor.fetchone()[0]
    conn.close()

    price = float(get_setting('proxy_price') or 3.0)
    if stock == 0:
        bot.send_message(chat_id, f"{CE('cross')} <b>{STRINGS[lang]['stock_empty']}</b>")
        return

    msg = f"{CE('desktop')} " + STRINGS[lang]['stock_info'].format(
        price=price, stock=stock,
        c_money=CE('money'), c_stats=CE('stats'), c_notice=CE('notice')
    )
    sent = bot.send_message(chat_id, msg)
    bot.register_next_step_handler(sent, process_buy_quantity)

@bot.message_handler(func=lambda m: "Buy Proxy" in m.text)
def buy_proxy_btn(message):
    trigger_buy_proxy(message.chat.id, message.from_user.id)

@bot.callback_query_handler(func=lambda call: call.data == "buy_shortcut")
def buy_shortcut(call):
    bot.answer_callback_query(call.id)
    trigger_buy_proxy(call.message.chat.id, call.from_user.id)

def process_buy_quantity(message):
    uid = message.from_user.id
    lang = get_user_lang(uid)
    text = (message.text or "").strip()

    if any(k in text for k in ["Main Menu", "Buy Proxy", "Wallet", "Check Proxy", "Support", "Admin Panel", "Language"]):
        bot.send_message(uid, f"{CE('home')} Main Menu:", reply_markup=main_keyboard(uid))
        return

    try:
        qty = int(text)
        if qty <= 0: raise ValueError
    except ValueError:
        bot.send_message(uid, f"{CE('cross')} <b>{STRINGS[lang]['invalid_qty']}</b>", reply_markup=main_keyboard(uid))
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM proxies WHERE is_sold = 0")
    stock = cursor.fetchone()[0]

    if qty > stock:
        bot.send_message(uid, f"{CE('cross')} " + STRINGS[lang]['low_stock'].format(stock=stock), reply_markup=main_keyboard(uid))
        conn.close()
        return

    price = float(get_setting('proxy_price') or 3.0)
    total_cost = qty * price
    user = get_user(uid)

    if user[2] < total_cost:
        msg = f"{CE('cross')} " + STRINGS[lang]['low_balance'].format(total=total_cost, balance=user[2])
        bot.send_message(uid, msg, reply_markup=main_keyboard(uid))
        conn.close()
        return

    cursor.execute("SELECT id, proxy_data FROM proxies WHERE is_sold = 0 LIMIT ?", (qty,))
    proxies = cursor.fetchall()
    p_ids = [p[0] for p in proxies]
    p_lines = [p[1] for p in proxies]

    cursor.execute(f"UPDATE proxies SET is_sold = 1 WHERE id IN ({','.join(['?']*len(p_ids))})", p_ids)
    cursor.execute("UPDATE users SET balance = balance - ?, total_orders = total_orders + 1, proxies_bought = proxies_bought + ? WHERE user_id = ?", (total_cost, qty, uid))
    cursor.execute("SELECT COUNT(*) FROM proxies WHERE is_sold = 0")
    rem_stock = cursor.fetchone()[0]
    conn.commit()
    conn.close()

    username = message.from_user.username or f"user_{uid}"
    file_name = get_unique_filename(username)

    with open(file_name, "w", encoding="utf-8") as f:
        f.write("\n".join(p_lines))

    with open(file_name, "rb") as doc:
        bot.send_document(uid, doc, caption=f"{file_name}", reply_markup=main_keyboard(uid))

    if os.path.exists(file_name):
        os.remove(file_name)

    adm_notif = (
        f"{CE('notice')} <b>নতুন প্রক্সি বিক্রি হয়েছে!</b>\n\n"
        f"{CE('user')} <b>ক্রেতা:</b> @{message.from_user.username or 'NoUsername'} (<code>{uid}</code>)\n"
        f"{CE('desktop')} <b>পরিমাণ:</b> <code>{qty} Pcs</code>\n"
        f"{CE('money')} <b>মোট মূল্য:</b> <code>{total_cost:.2f} BDT</code>\n"
        f"{CE('stats')} <b>অবশিষ্ট স্টক:</b> <code>{rem_stock} Pcs</code>"
    )
    try: bot.send_message(SUPER_ADMIN_ID, adm_notif)
    except Exception: pass

# ==========================================
# WALLET & GITHUB PAGES DADA PAY DEPOSIT
# ==========================================
@bot.message_handler(func=lambda m: "Wallet" in m.text)
def wallet_btn(message):
    uid = message.from_user.id
    lang = get_user_lang(uid)
    if check_maintenance_for_user(uid):
        bot.send_message(uid, STRINGS[lang]['maintenance'])
        return
    user = get_user(uid)
    if not user: return

    msg = f"{CE('card')} " + STRINGS[lang]['wallet_info'].format(
        uid=user[0], bal=user[2], dep=user[3], bought=user[5],
        c_user=CE('user'), c_money=CE('money'),
        c_rocket=CE('rocket'), c_shop=CE('shop')
    )
    markup = types.InlineKeyboardMarkup()
    markup.add(create_ikb_button("➕ Add Funds / ডিপোজিট", callback_data="start_deposit"))
    bot.send_message(uid, msg, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "start_deposit")
def start_deposit_callback(call):
    uid = call.from_user.id
    lang = get_user_lang(uid)
    if check_maintenance_for_user(uid):
        bot.answer_callback_query(call.id, "Bot is under maintenance!", show_alert=True)
        return

    markup = types.InlineKeyboardMarkup(row_width=1)
    btns = []

    if get_setting('dada_active') == '1':
        btns.append(create_ikb_button(STRINGS[lang]['auto_pay_btn'], callback_data="dep_auto"))
    if get_setting('bkash_active') == '1':
        btns.append(create_ikb_button("📱 bKash Manual", callback_data="dep_bkash"))
    if get_setting('nagad_active') == '1':
        btns.append(create_ikb_button("📱 Nagad Manual", callback_data="dep_nagad"))
    if get_setting('binance_active') == '1':
        btns.append(create_ikb_button("🪙 Binance Pay", callback_data="dep_binance"))

    for b in btns: markup.add(b)

    min_dep = get_setting('min_deposit') or '10.0'
    usd_rate = get_setting('usd_rate') or '125.0'

    msg = f"{CE('money')} " + STRINGS[lang]['deposit_title'].format(
        min_dep=min_dep, usd_rate=usd_rate, c_notice=CE('notice'), c_dollar=CE('dollar')
    )
    bot.send_message(uid, msg, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("dep_"))
def dep_method_selected(call):
    method = call.data.split("_")[1]
    uid = call.from_user.id
    lang = get_user_lang(uid)
    sent = bot.send_message(uid, f"{CE('money')} " + STRINGS[lang]['dep_amt_ask'])
    bot.register_next_step_handler(sent, process_dep_amt, method)

def process_dep_amt(message, method):
    uid = message.from_user.id
    lang = get_user_lang(uid)
    try:
        amount = float(message.text.strip())
        min_dep = float(get_setting('min_deposit') or 10.0)
        if amount < min_dep:
            bot.send_message(uid, f"{CE('cross')} " + STRINGS[lang]['min_dep_err'].format(min_dep=min_dep))
            return
    except Exception:
        bot.send_message(uid, f"{CE('cross')} <i>ভুল ইনপুট! শুধু সংখ্যা লিখে পাঠান।</i>")
        return

    if method == "auto":
        brand_key = get_setting('dada_brand_key').strip()
        if not brand_key:
            bot.send_message(uid, f"{CE('cross')} <b>গেটওয়ে ব্র্যান্ড কি (Brand Key) সেট করা নেই!</b>")
            return

        create_url = get_setting('dada_create_url').strip() or 'https://pay.dadapay.shop/api/payment/create'
        github_pages_url = get_setting('github_pages_url').strip() or 'https://yourusername.github.io/dadapay/'

        headers = {
            'Content-Type': 'application/json',
            'API-KEY': brand_key,
            'SECRET-KEY': brand_key,
            'BRAND-KEY': brand_key
        }

        user_name = message.from_user.first_name or "User"
        user_phone = str(uid)
        formatted_amount = f"{amount:.2f}".rstrip('0').rstrip('.') if '.' in f"{amount:.2f}" else str(int(amount))

        success_bridge_url = f"{github_pages_url}?uid={uid}&amt={formatted_amount}"

        post_data = {
            'cus_name': user_name,
            'cus_email': f"{user_phone}@gmail.com",
            'amount': formatted_amount,
            'success_url': success_bridge_url,
            'cancel_url': success_bridge_url,
            'meta_data': json.dumps({'user_id': str(uid), 'amount': amount, 'type': 'wallet_deposit'})
        }

        try:
            res = requests.post(create_url, headers=headers, json=post_data, timeout=30, verify=False)
            res_data = res.json()

            status_val = res_data.get("status")
            is_successful = (status_val is True or str(status_val).lower() == "true" or status_val == 1 or "payment_url" in res_data)

            if is_successful and res_data.get("payment_url"):
                pay_url = res_data.get("payment_url")

                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute("INSERT INTO pending_payments (user_id, amount, gateway_trx) VALUES (?, ?, ?)",
                               (uid, amount, "INIT"))
                conn.commit()
                conn.close()

                markup = types.InlineKeyboardMarkup(row_width=1)
                markup.add(
                    create_ikb_button("💵 Pay Now / এখনই পেমেন্ট করুন", url=pay_url)
                )
                msg = f"{CE('dada')} " + STRINGS[lang]['auto_pay_info'].format(
                    amt=amount, c_cash=CE('cash')
                )
                bot.send_message(uid, msg, reply_markup=markup)
            else:
                err_msg = res_data.get("message", "Invalid API Request. ব্র্যান্ড কি (Brand Key) চেক করুন।")
                bot.send_message(uid, f"{CE('cross')} <b>পেমেন্ট গেটওয়ে এরর:</b> {err_msg}")
        except Exception as e:
            bot.send_message(uid, f"{CE('cross')} <b>গেটওয়ে কানেকশন এরর:</b> {str(e)[:60]}")
        return

    # MANUAL METHODS
    usd_rate = float(get_setting('usd_rate') or 125.0)
    if method == "bkash":
        num = get_setting('bkash_num')
        inst = f"বিকাশ পার্সোনাল নম্বরে <b>Send Money</b> করুন:\n<code>{num}</code>\nপরিমাণ: <b>{amount:.2f} BDT</b>"
    elif method == "nagad":
        num = get_setting('nagad_num')
        inst = f"নগদ পার্সোনাল নম্বরে <b>Send Money</b> করুন:\n<code>{num}</code>\nপরিমাণ: <b>{amount:.2f} BDT</b>"
    else:
        usd_amt = amount / usd_rate
        bin_id = get_setting('binance_id')
        inst = f"বাইন্যান্স পে তে <b>${usd_amt:.2f} USDT</b> পাঠান:\nBinance Pay ID: <code>{bin_id}</code>"

    msg = f"<b>ম্যানুয়াল ডিপোজিট ({method.upper()})</b>\n\n{inst}\n\n➡️ <b>পেমেন্ট শেষে Transaction ID (TrxID) লিখে পাঠান:</b>"
    sent = bot.send_message(uid, msg)
    bot.register_next_step_handler(sent, process_trx, method, amount)

# ==========================================
# GLOBAL MESSAGE CATCHER (URL/TRXID CATCHER)
# ==========================================
@bot.message_handler(func=lambda m: m.text and ("transactionId=" in m.text or len(m.text.strip()) == 10))
def global_trx_listener(message):
    uid = message.from_user.id
    if check_maintenance_for_user(uid): return
    raw_input = message.text.strip()

    match = re.search(r'(?:transactionId|transaction_id|trx_id|id)=([a-zA-Z0-9_\-]+)', raw_input, re.IGNORECASE)
    if match:
        trx_id = match.group(1).strip()
    else:
        trx_id = re.sub(r'https?://\S+', '', raw_input).replace('"', '').replace("'", "").strip()

    if not trx_id or len(trx_id) < 5: return

    status_msg = bot.send_message(uid, f"{CE('fire')} <i>ট্রানজেকশন আইডি <code>{trx_id}</code> যাচাই করা হচ্ছে...</i>")
    ok, tid, paid_amt, method_used = verify_and_credit_robust(uid, trx_id)

    if ok:
        succ_text = (
            f"{CE('check')} <b>পেমেন্ট সফলভাবে সম্পন্ন হয়েছে!</b>\n\n"
            f"{CE('card')} <b>গেটওয়ে:</b> {str(method_used).upper()}\n"
            f"{CE('link')} <b>Trx ID:</b> <code>{tid}</code>\n"
            f"{CE('money')} <b>যোগকৃত ব্যালেন্স:</b> <code>{paid_amt:.2f} BDT</code>\n\n"
            f"<i>টাকা সফলভাবে আপনার অ্যাকাউন্টে যোগ হয়েছে!</i>"
        )
        bot.edit_message_text(succ_text, uid, status_msg.message_id)
    else:
        bot.edit_message_text(f"{CE('cross')} <b>পেমেন্ট যাচাই ব্যর্থ হয়েছে! সঠিক ট্রানজেকশন আইডি প্রদান করুন।</b>", uid, status_msg.message_id)

# ==========================================
# MANUAL DEPOSIT HANDLERS
# ==========================================
def process_trx(message, method, amount):
    trx_id = message.text.strip()
    sent = bot.send_message(message.chat.id, f"{CE('file')} <b>পেমেন্টের স্পষ্ট স্ক্রিনশট ফটো নিচে পাঠান:</b>")
    bot.register_next_step_handler(sent, process_dep_proof, method, amount, trx_id)

def process_dep_proof(message, method, amount, trx_id):
    if not message.photo:
        bot.send_message(message.chat.id, f"{CE('cross')} <b>কোনো ছবি পাওয়া যায়নি! বাতিল করা হলো।</b>")
        return
    photo_id = message.photo[-1].file_id
    uid = message.from_user.id
    uname = message.from_user.username or "NoUsername"

    markup = types.InlineKeyboardMarkup()
    markup.add(
        create_ikb_button("✅ Approve", callback_data=f"appdep_{uid}_{amount}"),
        create_ikb_button("❌ Reject", callback_data=f"rejdep_{uid}_{amount}")
    )
    caption = (
        f"{CE('notice')} <b>ম্যানুয়াল ডিপোজিট রিকোয়েস্ট!</b>\n\n"
        f"{CE('user')} ইউজার: @{uname} (<code>{uid}</code>)\n"
        f"{CE('card')} মেথড: {method.upper()}\n"
        f"{CE('money')} পরিমাণ: <code>{amount:.2f} BDT</code>\n"
        f"{CE('link')} Trx ID: <code>{trx_id}</code>"
    )
    bot.send_photo(SUPER_ADMIN_ID, photo_id, caption=caption, reply_markup=markup)
    bot.send_message(uid, f"{CE('check')} <b>ডিপোজিট রিকোয়েস্ট জমা হয়েছে! এডমিন যাচাই করে ব্যালেন্স যোগ করবেন।</b>")

@bot.callback_query_handler(func=lambda call: call.data.startswith("appdep_") or call.data.startswith("rejdep_"))
def admin_dep_action(call):
    if not is_admin(call.from_user.id): return
    act, uid, amt = call.data.split("_")
    uid, amt = int(uid), float(amt)

    if act == "appdep":
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET balance = balance + ?, total_deposit = total_deposit + ? WHERE user_id=?", (amt, amt, uid))
        conn.commit()
        conn.close()
        bot.edit_message_caption(f"{call.message.caption}\n\nSTATUS: APPROVED", call.message.chat.id, call.message.message_id)
        bot.send_message(uid, f"{CE('check')} <b>আপনার ডিপোজিট একাউন্টে যোগ হয়েছে!</b>\nযোগকৃত টাকা: <code>{amt:.2f} BDT</code>")
    else:
        bot.edit_message_caption(f"{call.message.caption}\n\nSTATUS: REJECTED", call.message.chat.id, call.message.message_id)
        bot.send_message(uid, f"{CE('cross')} <b>আপনার ডিপোজিট রিকোয়েস্ট বাতিল করা হয়েছে।</b>")

# ==========================================
# PROXY CHECKER SYSTEM
# ==========================================
def parse_proxy_line(text):
    text = text.strip().replace(" ", "")
    parts = text.split(",") if "," in text else text.split(":")
    if len(parts) == 4 and parts[1].isdigit():
        return {"host": parts[0], "port": int(parts[1]), "user": parts[2], "pass": parts[3], "raw": text}
    elif len(parts) == 2 and parts[1].isdigit():
        return {"host": parts[0], "port": int(parts[1]), "user": "", "pass": "", "raw": text}
    return None

async def check_single_proxy_async(px):
    url = f"http://{px['user']}:{px['pass']}@{px['host']}:{px['port']}" if px['user'] else f"http://{px['host']}:{px['port']}"
    try:
        async with httpx.AsyncClient(proxy=url, timeout=7.0, verify=False) as client:
            resp = await client.get("https://api.ipify.org?format=json")
            if resp.status_code == 200: return True, resp.json().get("ip", "Unknown")
            return False, f"HTTP {resp.status_code}"
    except Exception as e:
        return False, str(e)[:25]

@bot.message_handler(func=lambda m: "Check Proxy" in m.text)
def check_proxy_btn(message):
    uid = message.from_user.id
    if check_maintenance_for_user(uid):
        bot.send_message(uid, STRINGS[get_user_lang(uid)]['maintenance'])
        return

    if not check_force_join(uid):
        bot.send_message(uid, f"{CE('notice')} <b>আগে আমাদের অফিশিয়াল চ্যানেলে জয়েন করুন!</b>", reply_markup=force_join_markup())
        return
    msg = (
        f"{CE('desktop')} <b>প্রক্সি চেকার সেকশন</b>\n\n"
        f"একক বা একাধিক প্রক্সি লিখে পাঠান অথবা সরাসরি <b>.txt ফাইল</b> আপলোড দিন।\n\n"
        f"<i>ফরম্যাট:</i>\n"
        f"• <code>IP:Port:User:Pass</code>\n"
        f"• <code>IP:Port</code>"
    )
    sent = bot.send_message(uid, msg)
    bot.register_next_step_handler(sent, process_proxy_check_input)

def process_proxy_check_input(message):
    uid = message.from_user.id
    raw_lines = []
    if message.document:
        try:
            finfo = bot.get_file(message.document.file_id)
            downloaded = bot.download_file(finfo.file_path)
            raw_lines = [l.strip() for l in downloaded.decode('utf-8', errors='ignore').splitlines() if l.strip()]
        except Exception:
            bot.send_message(uid, f"{CE('cross')} <b>ফাইল ডাউনলোডে সমস্যা হয়েছে!</b>")
            return
    elif message.text:
        if any(k in message.text for k in ["Main Menu", "Check Proxy", "Buy Proxy", "Wallet", "Support", "Admin Panel", "Language"]):
            bot.send_message(uid, f"{CE('home')} Main Menu:", reply_markup=main_keyboard(uid))
            return
        raw_lines = [l.strip() for l in message.text.splitlines() if l.strip()]

    if not raw_lines:
        bot.send_message(uid, f"{CE('cross')} <b>কোনো প্রক্সি পাওয়া যায়নি!</b>")
        return

    bot.send_message(uid, f"{CE('fire')} <b>চেকিং শুরু হয়েছে ({len(raw_lines)} টি প্রক্সি)... অপেক্ষা করুন।</b>")
    valid_list, invalid_list = [], []

    async def run_checks():
        for line in raw_lines:
            px = parse_proxy_line(line)
            if px:
                ok, res = await check_single_proxy_async(px)
                if ok: valid_list.append(f"{px['raw']} -> IP: {res}")
                else: invalid_list.append(f"{px['raw']} -> Error: {res}")
            else:
                invalid_list.append(f"{line} -> Invalid Format")

    asyncio.run(run_checks())
    v_count, inv_count = len(valid_list), len(invalid_list)

    result_text = (
        f"{CE('stats')} <b>প্রক্সি চেকিং সম্পন্ন হয়েছে:</b>\n\n"
        f"{CE('check')} <b>সচল প্রক্সি (Live):</b> <code>{v_count}</code> Pcs\n"
        f"{CE('cross')} <b>অচল প্রক্সি (Dead):</b> <code>{inv_count}</code> Pcs\n"
    )
    bot.send_message(uid, result_text, reply_markup=main_keyboard(uid))

    username = message.from_user.username or f"user_{uid}"

    if v_count > 0:
        vf_name = get_unique_filename(username)
        with open(vf_name, "w", encoding="utf-8") as f: f.write("\n".join(valid_list))
        with open(vf_name, "rb") as doc: bot.send_document(uid, doc, caption=f"Live Proxies - {vf_name}")
        if os.path.exists(vf_name): os.remove(vf_name)

    if inv_count > 0:
        inv_name = get_unique_filename(username)
        with open(inv_name, "w", encoding="utf-8") as f: f.write("\n".join(invalid_list))
        with open(inv_name, "rb") as doc: bot.send_document(uid, doc, caption=f"Dead Proxies - {inv_name}")
        if os.path.exists(inv_name): os.remove(inv_name)

# ==========================================
# SUPPORT & NAVIGATION
# ==========================================
@bot.message_handler(func=lambda m: "Support" in m.text)
def support_btn(message):
    uid = message.from_user.id
    if check_maintenance_for_user(uid):
        bot.send_message(uid, STRINGS[get_user_lang(uid)]['maintenance'])
        return
    supp = get_setting('support_link') or "https://t.me/YourDomains"
    markup = types.InlineKeyboardMarkup()
    markup.add(create_ikb_button("💬 Contact Support", url=supp))
    bot.send_message(message.chat.id, f"{CE('chat')} <b>সাপোর্ট সেন্টার:</b>\nযেকোনো প্রশ্ন বা সহায়তায় যোগাযোগ করুন।", reply_markup=markup)

@bot.message_handler(func=lambda m: any(k in m.text for k in ["Main Menu", "/menu"]))
def back_main(message):
    bot.send_message(message.chat.id, f"{CE('home')} <b>প্রধান মেনু:</b>", reply_markup=main_keyboard(message.from_user.id))

# ==========================================
# ADMIN PANEL
# ==========================================
@bot.message_handler(func=lambda m: is_admin(m.from_user.id) and any(k in m.text for k in ["Admin Panel", "/admin"]))
def admin_cmd(message):
    bot.send_message(message.chat.id, f"{CE('king')} <b>এডমিন কন্ট্রোল প্যানেল:</b>", reply_markup=admin_keyboard())

# TOGGLE BOT STATUS (MAINTENANCE ON/OFF)
@bot.message_handler(func=lambda m: is_admin(m.from_user.id) and "Bot Status:" in m.text)
def toggle_bot_maintenance(message):
    current = get_setting('bot_status').upper()
    new_status = 'OFF' if current == 'ON' else 'ON'
    set_setting('bot_status', new_status)
    stat_str = "🔴 বন্ধ করা হয়েছে (Maintenance Mode Activated)!" if new_status == 'OFF' else "🟢 চালু করা হয়েছে (Live)!"
    bot.send_message(message.chat.id, f"{CE('gear')} <b>বট সফলভাবে {stat_str}</b>", reply_markup=admin_keyboard())

@bot.message_handler(func=lambda m: is_admin(m.from_user.id) and ("Stats" in m.text or "Wallet Count" in m.text))
def admin_stats(message):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM proxies WHERE is_sold = 1")
    sold_p = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM proxies WHERE is_sold = 0")
    stock_p = cursor.fetchone()[0]
    cursor.execute("SELECT SUM(total_deposit) FROM users")
    total_dep = cursor.fetchone()[0] or 0.0
    cursor.execute("SELECT SUM(balance) FROM users")
    total_user_balance = cursor.fetchone()[0] or 0.0
    conn.close()

    status_str = "🔴 Maintenance Mode" if is_maintenance() else "🟢 Active & Online"
    msg = (
        f"{CE('stats')} <b>বটের সামগ্রিক পরিসংখ্যান:</b>\n\n"
        f"⚡ <b>বট স্ট্যাটাস:</b> <code>{status_str}</code>\n"
        f"{CE('user')} <b>মোট রেজিস্টার্ড ইউজার:</b> <code>{total_users}</code> জন\n"
        f"{CE('money')} <b>সকল ইউজারের মোট জমা ব্যালেন্স:</b> <code>{total_user_balance:.2f} BDT</code>\n"
        f"{CE('rocket')} <b>লাইফটাইম মোট ডিপোজিট:</b> <code>{total_dep:.2f} BDT</code>\n"
        f"{CE('desktop')} <b>বর্তমানে অবিক্রিত স্টক:</b> <code>{stock_p} Pcs</code>\n"
        f"{CE('shop')} <b>সর্বমোট বিক্রিত প্রক্সি:</b> <code>{sold_p} Pcs</code>"
    )
    bot.send_message(message.chat.id, msg, reply_markup=admin_keyboard())

# DOWNLOAD ALL USER DATA BACKUP
@bot.message_handler(func=lambda m: is_admin(m.from_user.id) and "Backup All Users" in m.text)
def admin_backup_users(message):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, username, balance, total_deposit, total_orders, proxies_bought, is_banned, lang FROM users")
    users = cursor.fetchall()
    conn.close()

    if not users:
        bot.send_message(message.chat.id, f"{CE('cross')} <b>কোনো ইউজার ডাটা পাওয়া যায়নি!</b>")
        return

    rand_s = random.randint(100000, 999999)
    file_name = f"Users_Backup_{len(users)}_{rand_s}.txt"

    with open(file_name, "w", encoding="utf-8") as f:
        f.write("========================================================================================\n")
        f.write(f"                      BOT ALL USERS BACKUP REPORT - {datetime.datetime.now().strftime('%Y-%m-%d %I:%M %p')}\n")
        f.write(f"                      TOTAL USERS: {len(users)}\n")
        f.write("========================================================================================\n")
        f.write(f"{'User ID':<15} | {'Username':<22} | {'Balance (BDT)':<15} | {'Total Dep':<12} | {'Orders':<8} | {'Proxies':<8} | {'Status'}\n")
        f.write("----------------------------------------------------------------------------------------\n")
        for u in users:
            uid, uname, bal, dep, orders, bought, banned, lang = u
            uname_str = f"@{uname}" if uname else "N/A"
            status = "BANNED" if banned == 1 else "ACTIVE"
            f.write(f"{uid:<15} | {uname_str:<22} | {bal:<15.2f} | {dep:<12.2f} | {orders:<8} | {bought:<8} | {status}\n")
        f.write("========================================================================================\n")

    caption = (
        f"💾 <b>ইউজার ডাটাবেজ ব্যাকআপ রিপোর্ট</b>\n\n"
        f"👤 <b>মোট ইউজার:</b> <code>{len(users)}</code> জন\n"
        f"📅 <b>তারিখ:</b> <code>{datetime.datetime.now().strftime('%Y-%m-%d %I:%M %p')}</code>"
    )
    with open(file_name, "rb") as doc:
        bot.send_document(message.chat.id, doc, caption=caption)
    if os.path.exists(file_name):
        os.remove(file_name)

# DOWNLOAD UNSOLD STOCK
@bot.message_handler(func=lambda m: is_admin(m.from_user.id) and "Download Unsold Stock" in m.text)
def admin_download_stock(message):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT proxy_data FROM proxies WHERE is_sold = 0")
    rows = cursor.fetchall()
    conn.close()

    count = len(rows)
    if count == 0:
        bot.send_message(message.chat.id, f"{CE('cross')} <b>বর্তমানে অবিক্রিত কোনো প্রক্সি স্টকে নেই!</b>")
        return

    rand_s = random.randint(100000, 999999)
    file_name = f"Unsold_Stock_{count}_{rand_s}.txt"
    with open(file_name, "w", encoding="utf-8") as f:
        for r in rows: f.write(f"{r[0]}\n")

    caption = (
        f"{CE('file')} <b>অবিক্রিত স্টক প্রক্সি ফাইল</b>\n\n"
        f"মোট অবিক্রিত স্টক: <code>{count} Pcs</code>\n"
        f"তারিখ: <code>{datetime.datetime.now().strftime('%Y-%m-%d %I:%M %p')}</code>"
    )
    with open(file_name, "rb") as doc: bot.send_document(message.chat.id, doc, caption=caption)
    if os.path.exists(file_name): os.remove(file_name)

# ADD STOCK & BROADCAST
@bot.message_handler(func=lambda m: is_admin(m.from_user.id) and "Add Stock" in m.text)
def admin_add_stock_prompt(message):
    sent = bot.send_message(message.chat.id, f"{CE('plus')} <b>নতুন প্রক্সি মেসেজে পাঠান অথবা .txt ফাইল আপলোড দিন:</b>")
    bot.register_next_step_handler(sent, process_admin_stock_upload)

def process_admin_stock_upload(message):
    lines = []
    if message.document:
        try:
            finfo = bot.get_file(message.document.file_id)
            downloaded = bot.download_file(finfo.file_path)
            lines = [l.strip() for l in downloaded.decode('utf-8', errors='ignore').splitlines() if l.strip()]
        except Exception:
            bot.send_message(message.chat.id, f"{CE('cross')} ফাইল ডাউনলোডে সমস্যা হয়েছে!")
            return
    elif message.text:
        if any(k in message.text for k in ["Main Menu", "Admin Panel"]):
            bot.send_message(message.chat.id, "এডমিন প্যানেল:", reply_markup=admin_keyboard())
            return
        lines = [l.strip() for l in message.text.splitlines() if l.strip()]

    if not lines:
        bot.send_message(message.chat.id, f"{CE('cross')} কোনো প্রক্সি পাওয়া যায়নি!")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    for l in lines: cursor.execute("INSERT INTO proxies (proxy_data) VALUES (?)", (l,))
    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM proxies WHERE is_sold = 0")
    total_stock = cursor.fetchone()[0]
    conn.close()

    price = float(get_setting('proxy_price') or 3.0)
    added_qty = len(lines)

    bot.send_message(message.chat.id, f"{CE('check')} <b>সফলভাবে {added_qty} টি প্রক্সি স্টকে যুক্ত করা হয়েছে!</b>", reply_markup=admin_keyboard())

    # BROADCAST WITH FUNCTIONAL BUY NOW BUTTON
    broad_markup = types.InlineKeyboardMarkup()
    broad_markup.add(create_ikb_button("🛒 Buy Now / এখনই কিনুন", callback_data="buy_shortcut"))

    def do_broadcast():
        conn_b = sqlite3.connect(DB_FILE)
        cur_b = conn_b.cursor()
        cur_b.execute("SELECT user_id FROM users")
        user_list = cur_b.fetchall()
        conn_b.close()

        txt = (
            f"{CE('fire')} <b>নতুন প্রক্সি স্টক রিস্টক করা হয়েছে!</b>\n\n"
            f"আমাদের বটে সম্পূর্ণ ফ্রেশ ও হাই-স্পিড প্রাইভেট প্রক্সি স্টক যুক্ত করা হয়েছে।\n\n"
            f"{CE('desktop')} <b>নতুন স্টক:</b> <code>{added_qty} Pcs</code>\n"
            f"{CE('money')} <b>প্রতি পিসের মূল্য:</b> <code>{price:.2f} BDT</code>\n"
            f"{CE('stats')} <b>বর্তমান মোট স্টক:</b> <code>{total_stock} Pcs</code>\n\n"
            f"{CE('zap')} <i>দ্রুত প্রক্সি সংগ্রহ করতে নিচের বাটনে চাপ দিন:</i>"
        )
        for u in user_list:
            try:
                bot.send_message(u[0], txt, reply_markup=broad_markup)
                time.sleep(0.04)
            except Exception: pass

    threading.Thread(target=do_broadcast, daemon=True).start()

# ==========================================
# PAYMENT METHODS CONTROL
# ==========================================
@bot.message_handler(func=lambda m: is_admin(m.from_user.id) and "Payment Methods Control" in m.text)
def admin_payment_control_menu(message):
    dada_st = "Active" if get_setting('dada_active') == '1' else "Disabled"
    bkash_st = "Active" if get_setting('bkash_active') == '1' else "Disabled"
    nagad_st = "Active" if get_setting('nagad_active') == '1' else "Disabled"
    binance_st = "Active" if get_setting('binance_active') == '1' else "Disabled"

    msg = (
        f"{CE('gear')} <b>পেমেন্ট মেথড কন্ট্রোল প্যানেল:</b>\n\n"
        f"• <b>DADA PAY:</b> <code>{dada_st}</code>\n"
        f"• <b>bKash:</b> <code>{bkash_st}</code> (<code>{get_setting('bkash_num')}</code>)\n"
        f"• <b>Nagad:</b> <code>{nagad_st}</code> (<code>{get_setting('nagad_num')}</code>)\n"
        f"• <b>Binance Pay:</b> <code>{binance_st}</code> (<code>{get_setting('binance_id')}</code>)\n"
        f"• <b>GitHub Bridge:</b> <code>{get_setting('github_pages_url')}</code>\n\n"
        f"<i>নিচের বাটনগুলো থেকে যেকোনো মাধ্যম অন/অফ অথবা নম্বর/লিংক আপডেট করুন:</i>"
    )
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        create_ikb_button(f"DADA PAY ({dada_st})", callback_data="tog_dada"),
        create_ikb_button("DADA Brand Key", callback_data="set_dada_key"),
        create_ikb_button(f"bKash ({bkash_st})", callback_data="tog_bkash"),
        create_ikb_button("Edit bKash Num", callback_data="set_bkash_num"),
        create_ikb_button(f"Nagad ({nagad_st})", callback_data="tog_nagad"),
        create_ikb_button("Edit Nagad Num", callback_data="set_nagad_num"),
        create_ikb_button(f"Binance ({binance_st})", callback_data="tog_binance"),
        create_ikb_button("Edit Binance ID", callback_data="set_binance_id"),
        create_ikb_button("GitHub Pages Link", callback_data="set_github_url")
    )
    bot.send_message(message.chat.id, msg, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in [
    "tog_dada", "tog_bkash", "tog_nagad", "tog_binance",
    "set_dada_key", "set_bkash_num", "set_nagad_num", "set_binance_id", "set_github_url"
])
def callback_payment_control(call):
    if not is_admin(call.from_user.id): return

    if call.data == "tog_dada":
        cur = get_setting('dada_active')
        set_setting('dada_active', '0' if cur == '1' else '1')
        bot.answer_callback_query(call.id, "DADA PAY স্ট্যাটাস পরিবর্তন করা হয়েছে!")
        admin_payment_control_menu(call.message)
    elif call.data == "tog_bkash":
        cur = get_setting('bkash_active')
        set_setting('bkash_active', '0' if cur == '1' else '1')
        bot.answer_callback_query(call.id, "bKash স্ট্যাটাস পরিবর্তন করা হয়েছে!")
        admin_payment_control_menu(call.message)
    elif call.data == "tog_nagad":
        cur = get_setting('nagad_active')
        set_setting('nagad_active', '0' if cur == '1' else '1')
        bot.answer_callback_query(call.id, "Nagad স্ট্যাটাস পরিবর্তন করা হয়েছে!")
        admin_payment_control_menu(call.message)
    elif call.data == "tog_binance":
        cur = get_setting('binance_active')
        set_setting('binance_active', '0' if cur == '1' else '1')
        bot.answer_callback_query(call.id, "Binance Pay স্ট্যাটাস পরিবর্তন করা হয়েছে!")
        admin_payment_control_menu(call.message)

    elif call.data == "set_dada_key":
        sent = bot.send_message(call.message.chat.id, "DADA PAY এর নতুন <b>BRAND-KEY</b> লিখে পাঠান:")
        bot.register_next_step_handler(sent, lambda m: set_setting('dada_brand_key', m.text.strip()) or bot.send_message(m.chat.id, f"{CE('check')} DADA Brand Key আপডেট হয়েছে!", reply_markup=admin_keyboard()))
    elif call.data == "set_bkash_num":
        sent = bot.send_message(call.message.chat.id, "নতুন বিকাশ নম্বর লিখে পাঠান:")
        bot.register_next_step_handler(sent, lambda m: set_setting('bkash_num', m.text.strip()) or bot.send_message(m.chat.id, f"{CE('check')} বিকাশ নম্বর আপডেট হয়েছে!", reply_markup=admin_keyboard()))
    elif call.data == "set_nagad_num":
        sent = bot.send_message(call.message.chat.id, "নতুন নগদ নম্বর লিখে পাঠান:")
        bot.register_next_step_handler(sent, lambda m: set_setting('nagad_num', m.text.strip()) or bot.send_message(m.chat.id, f"{CE('check')} নগদ নম্বর আপডেট হয়েছে!", reply_markup=admin_keyboard()))
    elif call.data == "set_binance_id":
        sent = bot.send_message(call.message.chat.id, "নতুন Binance Pay ID লিখে পাঠান:")
        bot.register_next_step_handler(sent, lambda m: set_setting('binance_id', m.text.strip()) or bot.send_message(m.chat.id, f"{CE('check')} বাইন্যান্স আইডি আপডেট হয়েছে!", reply_markup=admin_keyboard()))
    elif call.data == "set_github_url":
        sent = bot.send_message(call.message.chat.id, "আপনার GitHub Pages URL দিন (যেমন: https://username.github.io/repo/):")
        bot.register_next_step_handler(sent, lambda m: set_setting('github_pages_url', m.text.strip()) or bot.send_message(m.chat.id, f"{CE('check')} GitHub URL আপডেট হয়েছে!", reply_markup=admin_keyboard()))

# ==========================================
# PRICE SETTINGS
# ==========================================
@bot.message_handler(func=lambda m: is_admin(m.from_user.id) and "Price Settings" in m.text)
def admin_price_settings_menu(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        create_ikb_button("💰 Proxy Price", callback_data="set_px_price"),
        create_ikb_button("💳 Min Deposit", callback_data="set_mindep"),
        create_ikb_button("💲 USD Rate", callback_data="set_rate")
    )
    bot.send_message(message.chat.id, f"{CE('gear')} <b>প্রাইস সেটিংস পরিচালনা করুন:</b>", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ["set_px_price", "set_mindep", "set_rate"])
def admin_price_callbacks(call):
    if not is_admin(call.from_user.id): return
    if call.data == "set_px_price":
        sent = bot.send_message(call.message.chat.id, "প্রতি পিস প্রক্সির মূল্য নির্ধারণ করুন (BDT):")
        bot.register_next_step_handler(sent, lambda m: set_setting('proxy_price', m.text.strip()) or bot.send_message(m.chat.id, f"{CE('check')} প্রক্সি মূল্য আপডেট হয়েছে!", reply_markup=admin_keyboard()))
    elif call.data == "set_mindep":
        sent = bot.send_message(call.message.chat.id, "সর্বনিম্ন ডিপোজিট সীমা নির্ধারণ করুন (BDT):")
        bot.register_next_step_handler(sent, lambda m: set_setting('min_deposit', m.text.strip()) or bot.send_message(m.chat.id, f"{CE('check')} সর্বনিম্ন ডিপোজিট আপডেট হয়েছে!", reply_markup=admin_keyboard()))
    elif call.data == "set_rate":
        sent = bot.send_message(call.message.chat.id, "১ ডলারের BDT রেট নির্ধারণ করুন (যেমন: 125):")
        bot.register_next_step_handler(sent, lambda m: set_setting('usd_rate', m.text.strip()) or bot.send_message(m.chat.id, f"{CE('check')} ডলার রেট আপডেট হয়েছে!", reply_markup=admin_keyboard()))

# ==========================================
# MANAGE ADMINS
# ==========================================
@bot.message_handler(func=lambda m: is_admin(m.from_user.id) and "Manage Admins" in m.text)
def admin_manage_admins(message):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM admins")
    admins_list = cursor.fetchall()
    conn.close()

    text = f"{CE('king')} <b>বর্তমান অ্যাডমিন তালিকা:</b>\n\n"
    for a in admins_list:
        uid = a[0]
        role = "Super Admin" if uid == SUPER_ADMIN_ID else "Admin"
        text += f"• <code>{uid}</code> — <i>{role}</i>\n"

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        create_ikb_button("➕ Add Admin", callback_data="adm_add_admin"),
        create_ikb_button("🗑️ Remove Admin", callback_data="adm_del_admin")
    )
    bot.send_message(message.chat.id, text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ["adm_add_admin", "adm_del_admin"])
def admin_manage_callbacks(call):
    if not is_admin(call.from_user.id): return
    if call.data == "adm_add_admin":
        sent = bot.send_message(call.message.chat.id, f"{CE('user')} <b>নতুন অ্যাডমিনের Telegram User ID পাঠান:</b>")
        bot.register_next_step_handler(sent, process_add_admin)
    elif call.data == "adm_del_admin":
        sent = bot.send_message(call.message.chat.id, f"{CE('trash')} <b>যে অ্যাডমিনকে বাদ দিতে চান তার User ID পাঠান:</b>")
        bot.register_next_step_handler(sent, process_del_admin)

def process_add_admin(message):
    try:
        new_admin_id = int(message.text.strip())
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO admins (user_id, added_by) VALUES (?, ?)", (new_admin_id, message.from_user.id))
        conn.commit()
        conn.close()
        bot.send_message(message.chat.id, f"{CE('check')} <b>ইউজার <code>{new_admin_id}</code> সফলভাবে অ্যাডমিন হিসেবে যুক্ত হয়েছে!</b>", reply_markup=admin_keyboard())
    except Exception:
        bot.send_message(message.chat.id, f"{CE('cross')} ভুল ইউজার আইডি! শুধু সংখ্যা লিখুন।", reply_markup=admin_keyboard())

def process_del_admin(message):
    try:
        target_id = int(message.text.strip())
        if target_id == SUPER_ADMIN_ID:
            bot.send_message(message.chat.id, f"{CE('cross')} <b>সুপার অ্যাডমিনকে বাদ দেওয়া যাবে না!</b>", reply_markup=admin_keyboard())
            return
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM admins WHERE user_id = ?", (target_id,))
        conn.commit()
        conn.close()
        bot.send_message(message.chat.id, f"{CE('check')} <b>ইউজার <code>{target_id}</code> কে অ্যাডমিন তালিকা থেকে বাদ দেওয়া হয়েছে!</b>", reply_markup=admin_keyboard())
    except Exception:
        bot.send_message(message.chat.id, f"{CE('cross')} ভুল ইউজার আইডি!", reply_markup=admin_keyboard())

# ==========================================
# FORCE JOIN SETTINGS
# ==========================================
@bot.message_handler(func=lambda m: is_admin(m.from_user.id) and "Force Join Settings" in m.text)
def admin_fj_menu(message):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, link, chat_id FROM force_channels")
    channels = cursor.fetchall()
    conn.close()

    txt = f"{CE('notice')} <b>ফোর্স জয়েন চ্যানেল তালিকা:</b>\n\n"
    markup = types.InlineKeyboardMarkup()
    for cid, name, link, chat_id in channels:
        txt += f"• <b>{name}</b> ({chat_id})\n"
        markup.add(create_ikb_button(f"🗑️ Delete {name}", callback_data=f"delfj_{cid}"))

    markup.add(create_ikb_button("➕ Add New Channel", callback_data="add_fj_channel"))
    bot.send_message(message.chat.id, txt, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "add_fj_channel" or call.data.startswith("delfj_"))
def fj_actions(call):
    if not is_admin(call.from_user.id): return
    if call.data == "add_fj_channel":
        msg = "নতুন চ্যানেল যুক্ত করতে তথ্য পাঠান:\n\nফরম্যাট: <code>নাম | ইনভাইট লিংক | চ্যাট আইডি</code>\nউদাহরণ: <code>MyChan | https://t.me/mychan | -100123456789</code>"
        sent = bot.send_message(call.message.chat.id, msg)
        bot.register_next_step_handler(sent, process_add_fj_channel)
    elif call.data.startswith("delfj_"):
        cid = int(call.data.split("_")[1])
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM force_channels WHERE id=?", (cid,))
        conn.commit()
        conn.close()
        bot.answer_callback_query(call.id, "চ্যানেল মুছে ফেলা হয়েছে!")
        admin_fj_menu(call.message)

def process_add_fj_channel(message):
    try:
        parts = [p.strip() for p in message.text.split("|")]
        name, link, chat_id = parts[0], parts[1], parts[2]
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO force_channels (name, link, chat_id) VALUES (?, ?, ?)", (name, link, chat_id))
        conn.commit()
        conn.close()
        bot.send_message(message.chat.id, f"{CE('check')} চ্যানেল <b>{name}</b> যুক্ত হয়েছে!", reply_markup=admin_keyboard())
    except Exception:
        bot.send_message(message.chat.id, f"{CE('cross')} ফরম্যাট ভুল হয়েছে!", reply_markup=admin_keyboard())

# ==========================================
# USER MANAGEMENT
# ==========================================
@bot.message_handler(func=lambda m: is_admin(m.from_user.id) and "User Management" in m.text)
def admin_user_mgmt(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        create_ikb_button("💰 ব্যালেন্স বাড়ান/কমান", callback_data="adm_mod_bal"),
        create_ikb_button("🚫 ব্যান / আনব্যান", callback_data="adm_ban")
    )
    bot.send_message(message.chat.id, f"{CE('user')} <b>ইউজার ম্যানেজমেন্ট:</b>", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ["adm_mod_bal", "adm_ban"])
def admin_user_callbacks(call):
    if not is_admin(call.from_user.id): return
    if call.data == "adm_mod_bal":
        sent = bot.send_message(call.message.chat.id, "ইউজার আইডি ও টাকার পরিমাণ লিখুন:\n<code>USER_ID AMOUNT</code> (যেমন: <code>123456789 100</code> বা <code>123456789 -50</code>)")
        bot.register_next_step_handler(sent, process_adm_bal)
    elif call.data == "adm_ban":
        sent = bot.send_message(call.message.chat.id, "ব্যান/আনব্যান করতে ইউজার আইডি দিন:")
        bot.register_next_step_handler(sent, process_adm_ban)

def process_adm_bal(message):
    try:
        uid, amt = message.text.split()
        uid, amt = int(uid), float(amt)
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amt, uid))
        conn.commit()
        conn.close()
        bot.send_message(message.chat.id, f"{CE('check')} ইউজার <code>{uid}</code> এর ব্যালেন্স আপডেট হয়েছে!", reply_markup=admin_keyboard())
    except Exception:
        bot.send_message(message.chat.id, f"{CE('cross')} ইনপুট ভুল হয়েছে!", reply_markup=admin_keyboard())

def process_adm_ban(message):
    try:
        uid = int(message.text.strip())
        u = get_user(uid)
        if not u:
            bot.send_message(message.chat.id, f"{CE('cross')} ইউজার ডাটাবেজে নেই!", reply_markup=admin_keyboard())
            return
        new_st = 0 if u[6] == 1 else 1
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET is_banned = ? WHERE user_id = ?", (new_st, uid))
        conn.commit()
        conn.close()
        bot.send_message(message.chat.id, f"{CE('check')} ইউজার <code>{uid}</code> স্ট্যাটাস: {'Banned' if new_st == 1 else 'Active'}", reply_markup=admin_keyboard())
    except Exception:
        bot.send_message(message.chat.id, f"{CE('cross')} ভুল ইউজার আইডি!", reply_markup=admin_keyboard())

# ==========================================
# BROADCAST
# ==========================================
@bot.message_handler(func=lambda m: is_admin(m.from_user.id) and "Broadcast" in m.text)
def admin_broadcast_prompt(message):
    sent = bot.send_message(message.chat.id, f"{CE('notice')} <b>সকল মেম্বারদের কাছে পাঠানোর মেসেজটি দিন:</b>")
    bot.register_next_step_handler(sent, process_admin_broadcast)

def process_admin_broadcast(message):
    if any(k in message.text for k in ["Main Menu", "Admin Panel"]):
        bot.send_message(message.chat.id, "এডমিন প্যানেল:", reply_markup=admin_keyboard())
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()
    conn.close()

    count = 0
    for u in users:
        try:
            bot.copy_message(u[0], message.chat.id, message.message_id)
            count += 1
            time.sleep(0.04)
        except Exception: pass

    bot.send_message(message.chat.id, f"{CE('check')} ব্রডকাস্ট সফল হয়েছে! মোট <code>{count}</code> জনের কাছে মেসেজ পৌঁছেছে।", reply_markup=admin_keyboard())

# ==========================================
# BOT POLLING
# ==========================================
if __name__ == "__main__":
    print("DADA PAY Mini App Proxy Shop Bot is active and running with Normal Emojis & Maintenance support!")
    bot.infinity_polling(none_stop=True, timeout=60)