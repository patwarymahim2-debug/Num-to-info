# =========================================================
# PROFESSIONAL TELEGRAM LOOKUP BOT
# SINGLE FILE VERSION
# CREATED FOR EDUCATIONAL PURPOSES
# =========================================================

import os
import re
import time
import json
import random
import sqlite3
import logging
import requests
import telebot

from datetime import datetime
from telebot import types
from telebot.util import escape_markdown

# =========================================================
# CONFIGURATION
# =========================================================

BOT_TOKEN = "8342978260:AAFDSO6yYa2xIpLXkghFBLcodfy4GBPS-lc"
ADMIN_ID = 7276206449

CHANNELS = [
    "@mbtcyber",
    "@unknown_owner_info"
]

BOT_NAME = "PRO LOOKUP BOT"
BOT_VERSION = "v5.0"

LOOKUP_COST = 5
REF_BONUS = 10
START_BONUS = 10
COOLDOWN = 10

# =========================================================
# LOGGING
# =========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# =========================================================
# BOT INIT
# =========================================================

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

# =========================================================
# DATABASE
# =========================================================

conn = sqlite3.connect(
    "pro_users.db",
    check_same_thread=False
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    balance INTEGER DEFAULT 10,
    referrals INTEGER DEFAULT 0,
    total_search INTEGER DEFAULT 0,
    join_date TEXT,
    is_banned INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS logs(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    number TEXT,
    time TEXT
)
""")

conn.commit()

# =========================================================
# CACHE
# =========================================================

cooldowns = {}

# =========================================================
# UI THEMES
# =========================================================

WELCOME_TEXT = """
🌈 *WELCOME TO PRO LOOKUP BOT*

✨ Premium User Interface
⚡ Fast Number Lookup
🛡️ Secure System
🔥 Professional Features

👇 Choose an option below
"""

# =========================================================
# DATABASE FUNCTIONS
# =========================================================


def add_user(user_id, username):

    cursor.execute(
        "SELECT user_id FROM users WHERE user_id=?",
        (user_id,)
    )

    data = cursor.fetchone()

    if not data:

        cursor.execute(
            """
            INSERT INTO users(
                user_id,
                username,
                balance,
                referrals,
                total_search,
                join_date
            )
            VALUES(?,?,?,?,?,?)
            """,
            (
                user_id,
                username,
                START_BONUS,
                0,
                0,
                str(datetime.now())
            )
        )

        conn.commit()


def get_user(user_id):

    cursor.execute(
        "SELECT * FROM users WHERE user_id=?",
        (user_id,)
    )

    return cursor.fetchone()


def update_balance(user_id, amount):

    cursor.execute(
        "UPDATE users SET balance=balance+? WHERE user_id=?",
        (amount, user_id)
    )

    conn.commit()


def add_referral(user_id):

    cursor.execute(
        "UPDATE users SET referrals=referrals+1 WHERE user_id=?",
        (user_id,)
    )

    conn.commit()


def add_search(user_id):

    cursor.execute(
        "UPDATE users SET total_search=total_search+1 WHERE user_id=?",
        (user_id,)
    )

    conn.commit()


def ban_user(user_id):

    cursor.execute(
        "UPDATE users SET is_banned=1 WHERE user_id=?",
        (user_id,)
    )

    conn.commit()


def unban_user(user_id):

    cursor.execute(
        "UPDATE users SET is_banned=0 WHERE user_id=?",
        (user_id,)
    )

    conn.commit()

# =========================================================
# RATE LIMIT
# =========================================================


def can_use(user_id):

    now = time.time()

    if user_id in cooldowns:

        last = cooldowns[user_id]

        if now - last < COOLDOWN:
            return False

    cooldowns[user_id] = now

    return True

# =========================================================
# CHANNEL CHECK
# =========================================================


def joined(user_id):

    try:

        for ch in CHANNELS:

            member = bot.get_chat_member(ch, user_id)

            if member.status in ["left", "kicked"]:
                return False

        return True

    except Exception as e:

        print(e)
        return False

# =========================================================
# MAIN MENU
# =========================================================


def menu(user_id):

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        row_width=2
    )

    b1 = types.KeyboardButton("🔍 Number Lookup")
    b2 = types.KeyboardButton("👤 Profile")
    b3 = types.KeyboardButton("💰 Balance")
    b4 = types.KeyboardButton("👥 Refer")
    b5 = types.KeyboardButton("🎁 Bonus")
    b6 = types.KeyboardButton("📊 Statistics")
    b7 = types.KeyboardButton("ℹ️ Help")

    markup.add(b1)
    markup.add(b2, b3)
    markup.add(b4, b5)
    markup.add(b6, b7)

    if user_id == ADMIN_ID:

        admin = types.KeyboardButton("⚙️ Admin Panel")
        markup.add(admin)

    return markup

# =========================================================
# ANIMATED LOADING
# =========================================================

loading_frames = [
    "⏳ Loading.",
    "⏳ Loading..",
    "⏳ Loading...",
    "⚡ Processing.",
    "⚡ Processing..",
    "⚡ Processing..."
]

# =========================================================
# START
# =========================================================

@bot.message_handler(commands=['start'])
def start(message):

    user_id = message.from_user.id
    username = message.from_user.username

    add_user(
        user_id,
        f"@{username}" if username else "N/A"
    )

    args = message.text.split()

    if len(args) > 1:

        ref = args[1]

        if ref.isdigit():

            ref = int(ref)

            if ref != user_id:

                update_balance(ref, REF_BONUS)
                add_referral(ref)

                try:

                    bot.send_message(
                        ref,
                        "🎉 New referral joined!\n💰 +10 Balance Added"
                    )

                except:
                    pass

    markup = types.InlineKeyboardMarkup(row_width=1)

    join1 = types.InlineKeyboardButton(
        "📢 JOIN MAIN CHANNEL",
        url="https://t.me/NumerToInfo"
    )

    join2 = types.InlineKeyboardButton(
        "📢 JOIN BACKUP CHANNEL",
        url="https://t.me/NumerToInfo2"
    )

    verify = types.InlineKeyboardButton(
        "✅ VERIFY NOW",
        callback_data="verify"
    )

    markup.add(join1)
    markup.add(join2)
    markup.add(verify)

    bot.send_message(
        user_id,
        WELCOME_TEXT,
        reply_markup=markup
    )

# =========================================================
# VERIFY
# =========================================================

@bot.callback_query_handler(func=lambda c: c.data == "verify")
def verify(c):

    user_id = c.from_user.id

    if joined(user_id):

        bot.send_message(
            user_id,
            "✅ Verification Successful!",
            reply_markup=menu(user_id)
        )

    else:

        bot.answer_callback_query(
            c.id,
            "❌ Join all channels first",
            show_alert=True
        )

# =========================================================
# PROFILE
# =========================================================


def profile_text(user_id):

    data = get_user(user_id)

    balance = data[2]
    refs = data[3]
    searches = data[4]
    join_date = data[5]

    text = f"""
🌟 *USER PROFILE*

🆔 User ID: `{user_id}`
💰 Balance: `{balance}`
👥 Referrals: `{refs}`
🔍 Total Searches: `{searches}`
📅 Join Date:
`{join_date}`

🔥 Premium User
"""

    return text

# =========================================================
# BONUS SYSTEM
# =========================================================

@bot.message_handler(func=lambda m: m.text == "🎁 Bonus")
def bonus(message):

    user_id = message.from_user.id

    bonus_amount = random.randint(1, 5)

    update_balance(user_id, bonus_amount)

    bot.send_message(
        user_id,
        f"🎉 You received {bonus_amount} bonus points!"
    )

# =========================================================
# HELP
# =========================================================

@bot.message_handler(func=lambda m: m.text == "ℹ️ Help")
def help_menu(message):

    text = """
📘 *HELP MENU*

🔍 Send Bangladeshi number
📱 Example: `017XXXXXXXX`

💰 Each lookup costs 5 points
👥 Invite friends for bonus
⚡ Fast server support
🛡️ Secure lookup system

👨‍💻 Developer: TEAM BMT
"""

    bot.send_message(
        message.chat.id,
        text
    )

# =========================================================
# PROFILE BUTTON
# =========================================================

@bot.message_handler(func=lambda m: m.text == "👤 Profile")
def profile(message):

    bot.send_message(
        message.chat.id,
        profile_text(message.from_user.id)
    )

# =========================================================
# BALANCE
# =========================================================

@bot.message_handler(func=lambda m: m.text == "💰 Balance")
def balance(message):

    data = get_user(message.from_user.id)

    bot.send_message(
        message.chat.id,
        f"💰 Your Balance: `{data[2]}`"
    )

# =========================================================
# REFER
# =========================================================

@bot.message_handler(func=lambda m: m.text == "👥 Refer")
def refer(message):

    user_id = message.from_user.id

    bot_username = bot.get_me().username

    link = f"https://t.me/{bot_username}?start={user_id}"

    text = f"""
👥 *REFERRAL SYSTEM*

🔗 Your Link:
`{link}`

🎁 Earn 10 points per referral
"""

    bot.send_message(
        user_id,
        text
    )

# =========================================================
# STATS
# =========================================================

@bot.message_handler(func=lambda m: m.text == "📊 Statistics")
def stats(message):

    cursor.execute(
        "SELECT COUNT(*) FROM users"
    )

    total_users = cursor.fetchone()[0]

    cursor.execute(
        "SELECT SUM(total_search) FROM users"
    )

    total_searches = cursor.fetchone()[0]

    if total_searches is None:
        total_searches = 0

    text = f"""
📊 *BOT STATISTICS*

👤 Total Users: `{total_users}`
🔍 Total Searches: `{total_searches}`
⚡ Bot Version: `{BOT_VERSION}`
🟢 Status: `ONLINE`
"""

    bot.send_message(
        message.chat.id,
        text
    )

# =========================================================
# LOOKUP BUTTON
# =========================================================

@bot.message_handler(func=lambda m: m.text == "🔍 Number Lookup")
def lookup(message):

    bot.send_message(
        message.chat.id,
        "📱 Send Bangladeshi number now"
    )

# =========================================================
# NUMBER LOOKUP
# =========================================================

@bot.message_handler(func=lambda m: True)
def all_message(message):

    user_id = message.from_user.id
    text = message.text

    data = get_user(user_id)

    if not data:
        return

    if data[6] == 1:

        bot.send_message(
            user_id,
            "🚫 You are banned"
        )

        return

    pattern = r"^(01[3-9]\d{8})$"

    if re.match(pattern, text):

        if not can_use(user_id):

            bot.send_message(
                user_id,
                "⏳ Wait a few seconds"
            )

            return

        balance = data[2]

        if balance < LOOKUP_COST:

            bot.send_message(
                user_id,
                "❌ Not enough balance"
            )

            return

        loading = bot.send_message(
            user_id,
            loading_frames[0]
        )

        try:

            for frame in loading_frames:

                bot.edit_message_text(
                    frame,
                    user_id,
                    loading.message_id
                )

                time.sleep(0.3)

        except:
            pass

        try:

            url = f"https://black-herix-num-lookup.vercel.app/api/lookup?number={text}"

            response = requests.get(
                url,
                timeout=15
            )

            result = response.json()

            if result.get("success"):

                update_balance(user_id, -LOOKUP_COST)
                add_search(user_id)

                name = escape_markdown(
                    str(result.get("name", "Unknown"))
                )

                number = escape_markdown(
                    str(result.get("international_format", "N/A"))
                )

                country = escape_markdown(
                    str(result.get("country", "N/A"))
                )

                carrier = escape_markdown(
                    str(result.get("carrier", "N/A"))
                )

                timestamp = escape_markdown(
                    str(result.get("timestamp", "N/A"))
                )

                cursor.execute(
                    "INSERT INTO logs(user_id, number, time) VALUES(?,?,?)",
                    (
                        user_id,
                        text,
                        str(datetime.now())
                    )
                )

                conn.commit()

                buttons = types.InlineKeyboardMarkup(row_width=2)

                full_num = "880" + text[-10:]

                whatsapp = types.InlineKeyboardButton(
                    "💬 WhatsApp",
                    url=f"https://wa.me/{full_num}"
                )

                facebook = types.InlineKeyboardButton(
                    "👥 Facebook",
                    url=f"https://facebook.com/search/top/?q={name}"
                )

                google = types.InlineKeyboardButton(
                    "🌍 Google",
                    url=f"https://google.com/search?q={text}"
                )

                share = types.InlineKeyboardButton(
                    "📤 Share",
                    switch_inline_query=text
                )

                buttons.add(whatsapp, facebook)
                buttons.add(google, share)

                final_text = f"""
╔══════════════════╗
      🔥 LOOKUP RESULT 🔥
╚══════════════════╝

👤 *NAME*
`{name}`

📞 *NUMBER*
`{number}`

🌍 *COUNTRY*
`{country}`

📡 *CARRIER*
`{carrier}`

⏰ *TIME*
`{timestamp}`

━━━━━━━━━━━━━━━
⚡ Powered By PRO LOOKUP
━━━━━━━━━━━━━━━
"""

                bot.edit_message_text(
                    final_text,
                    user_id,
                    loading.message_id,
                    reply_markup=buttons
                )

            else:

                bot.edit_message_text(
                    "❌ No information found",
                    user_id,
                    loading.message_id
                )

        except Exception as e:

            print(e)

            bot.send_message(
                user_id,
                "⚠️ Server error"
            )

# =========================================================
# ADMIN PANEL
# =========================================================

@bot.message_handler(func=lambda m: m.text == "⚙️ Admin Panel")
def admin(message):

    if message.from_user.id != ADMIN_ID:
        return

    markup = types.InlineKeyboardMarkup(row_width=2)

    b1 = types.InlineKeyboardButton(
        "📊 Users",
        callback_data="admin_users"
    )

    b2 = types.InlineKeyboardButton(
        "🎁 Gift",
        callback_data="admin_gift"
    )

    b3 = types.InlineKeyboardButton(
        "🚫 Ban",
        callback_data="admin_ban"
    )

    b4 = types.InlineKeyboardButton(
        "✅ Unban",
        callback_data="admin_unban"
    )

    b5 = types.InlineKeyboardButton(
        "📜 Logs",
        callback_data="admin_logs"
    )

    markup.add(b1, b2)
    markup.add(b3, b4)
    markup.add(b5)

    bot.send_message(
        ADMIN_ID,
        "⚙️ Professional Admin Panel",
        reply_markup=markup
    )

# =========================================================
# ADMIN CALLBACKS
# =========================================================

@bot.callback_query_handler(func=lambda c: c.data.startswith("admin_"))
def admin_callbacks(c):

    if c.from_user.id != ADMIN_ID:
        return

    action = c.data.split("_")[1]

    if action == "users":

        cursor.execute(
            "SELECT COUNT(*) FROM users"
        )

        total = cursor.fetchone()[0]

        bot.send_message(
            ADMIN_ID,
            f"👤 Total Users: {total}"
        )

    elif action == "logs":

        cursor.execute(
            "SELECT * FROM logs ORDER BY id DESC LIMIT 10"
        )

        logs = cursor.fetchall()

        text = "📜 Latest Logs\n\n"

        for log in logs:

            text += f"🆔 {log[1]}\n"
            text += f"📞 {log[2]}\n"
            text += f"⏰ {log[3]}\n\n"

        bot.send_message(
            ADMIN_ID,
            text
        )

    elif action == "gift":

        msg = bot.send_message(
            ADMIN_ID,
            "Send user ID"
        )

        bot.register_next_step_handler(
            msg,
            gift_user_id
        )

    elif action == "ban":

        msg = bot.send_message(
            ADMIN_ID,
            "Send user ID to ban"
        )

        bot.register_next_step_handler(
            msg,
            ban_process
        )

    elif action == "unban":

        msg = bot.send_message(
            ADMIN_ID,
            "Send user ID to unban"
        )

        bot.register_next_step_handler(
            msg,
            unban_process
        )

# =========================================================
# GIFT PROCESS
# =========================================================


def gift_user_id(message):

    try:

        user_id = int(message.text)

        msg = bot.send_message(
            ADMIN_ID,
            "Send amount"
        )

        bot.register_next_step_handler(
            msg,
            lambda m: gift_amount(m, user_id)
        )

    except:

        bot.send_message(
            ADMIN_ID,
            "Invalid ID"
        )


def gift_amount(message, user_id):

    try:

        amount = int(message.text)

        update_balance(user_id, amount)

        bot.send_message(
            ADMIN_ID,
            "✅ Gift Sent"
        )

        bot.send_message(
            user_id,
            f"🎁 Admin sent {amount} points"
        )

    except:

        bot.send_message(
            ADMIN_ID,
            "Error"
        )

# =========================================================
# BAN
# =========================================================


def ban_process(message):

    try:

        user_id = int(message.text)

        ban_user(user_id)

        bot.send_message(
            ADMIN_ID,
            "🚫 User Banned"
        )

    except:

        bot.send_message(
            ADMIN_ID,
            "Error"
        )

# =========================================================
# UNBAN
# =========================================================


def unban_process(message):

    try:

        user_id = int(message.text)

        unban_user(user_id)

        bot.send_message(
            ADMIN_ID,
            "✅ User Unbanned"
        )

    except:

        bot.send_message(
            ADMIN_ID,
            "Error"
        )

# =========================================================
# ERROR HANDLER
# =========================================================

while True:

    try:

        print("BOT RUNNING...")

        bot.infinity_polling(
            timeout=30,
            long_polling_timeout=10
        )

    except Exception as e:

        print(e)

        time.sleep(5)