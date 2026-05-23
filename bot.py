import telebot
from telebot import types
import requests
import json
import os
import time
from datetime import datetime

# =====================================================
# CONFIG
# =====================================================

TOKEN = "8837587726:AAHREWqlL8jGK2FGDtHrXg1j-M8IoNcX0Is"
CHANNEL = "unknown_owner_info"
ADMIN_ID = 7276206449

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# =====================================================
# DATABASE
# =====================================================

DB = "users.json"

if not os.path.exists(DB):
    with open(DB, "w") as f:
        json.dump({}, f)


def load_users():
    with open(DB, "r") as f:
        return json.load(f)


def save_users(data):
    with open(DB, "w") as f:
        json.dump(data, f, indent=4)


# =====================================================
# PREMIUM TEXT
# =====================================================

WELCOME = """
<blockquote>
🚀 <b>ULTRA PRO IP LOOKUP SYSTEM</b>
━━━━━━━━━━━━━━━━━━
🌍 Smart IP Intelligence
📡 ISP Detection System
🛰 Geo Tracking Engine
⚡ Lightning Fast Response
🔒 Premium Security Interface
━━━━━━━━━━━━━━━━━━
💎 NEXT GENERATION TELEGRAM BOT
</blockquote>
"""

HELP_TEXT = """
<b>ℹ️ HELP CENTER</b>

🌍 IP Lookup → Search Any IP
👤 Profile → Your Account
👥 Refer → Invite Friends
🎁 Bonus → Claim Rewards
📊 Statistics → Bot Stats

💬 Support: @yourusername
"""

# =====================================================
# FORCE JOIN
# =====================================================


def joined(user_id):
    try:
        member = bot.get_chat_member(f"@{CHANNEL}", user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


# =====================================================
# SAVE USER
# =====================================================


# =====================================================
# SAVE USER
# =====================================================

def add_user(user_id, ref=None):

    users = load_users()
    uid = str(user_id)

    # Create New User
    if uid not in users:

        users[uid] = {
            "balance": 0,
            "referral": 0,
            "bonus": "no",
            "joined": str(datetime.now())
        }

        if ref and ref != uid:

            if ref in users:
                users[ref]["referral"] += 1
                users[ref]["balance"] += 1

    # Fix Old User Data
    else:

        if "balance" not in users[uid]:
            users[uid]["balance"] = 0

        if "referral" not in users[uid]:
            users[uid]["referral"] = 0

        if "bonus" not in users[uid]:
            users[uid]["bonus"] = "no"

        if "joined" not in users[uid]:
            users[uid]["joined"] = str(datetime.now())

    save_users(users)

# =====================================================
# MAIN MENU
# =====================================================


def main_menu(user_id):

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        row_width=2
    )

    b1 = types.KeyboardButton("🌍 IP Lookup")
    b2 = types.KeyboardButton("👤 Profile")
    b3 = types.KeyboardButton("💰 Balance")
    b4 = types.KeyboardButton("👥 Refer")
    b5 = types.KeyboardButton("🎁 Bonus")
    b6 = types.KeyboardButton("📊 Statistics")
    b7 = types.KeyboardButton("ℹ️ Help")

    markup.add(b1, b2)
    markup.add(b3, b4)
    markup.add(b5, b6)
    markup.add(b7)

    if user_id == ADMIN_ID:
        admin = types.KeyboardButton("⚙️ Admin Panel")
        markup.add(admin)

    return markup


# =====================================================
# START COMMAND
# =====================================================


@bot.message_handler(commands=['start'])
def start(message):

    user_id = message.from_user.id

    ref = None

    args = message.text.split()

    if len(args) > 1:
        ref = args[1]

    add_user(user_id, ref)

    if not joined(user_id):

        markup = types.InlineKeyboardMarkup()

        btn1 = types.InlineKeyboardButton(
            "📢 JOIN CHANNEL",
            url=f"https://t.me/{CHANNEL}"
        )

        btn2 = types.InlineKeyboardButton(
            "✅ CHECK JOIN",
            callback_data="check"
        )

        markup.add(btn1)
        markup.add(btn2)

        bot.send_message(
            message.chat.id,
            "⚠️ Join Channel First",
            reply_markup=markup
        )

        return

    gif = "https://media.giphy.com/media/ICOgUNjpvO0PC/giphy.gif"

    try:
        bot.send_animation(message.chat.id, gif)
    except:
        pass

    bot.send_message(
        message.chat.id,
        WELCOME,
        reply_markup=main_menu(user_id)
    )


# =====================================================
# CALLBACKS
# =====================================================


@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):

    if call.data == "check":

        if joined(call.from_user.id):
            bot.answer_callback_query(call.id, "✅ Verified")
            start(call.message)
        else:
            bot.answer_callback_query(call.id, "❌ Join First")


# =====================================================
# PROFILE
# =====================================================


@bot.message_handler(func=lambda m: m.text == "👤 Profile")
def profile(message):

    users = load_users()
    uid = str(message.from_user.id)

    bal = users[uid]['balance']
    ref = users[uid]['referral']

    text = f"""
╔══════════════╗
   👤 USER PROFILE
╚══════════════╝

🆔 ID: <code>{uid}</code>
👤 Name: {message.from_user.first_name}
💰 Balance: {bal}
👥 Referrals: {ref}

💎 Premium User: No
"""

    bot.send_message(message.chat.id, text)


# =====================================================
# BALANCE
# =====================================================


@bot.message_handler(func=lambda m: m.text == "💰 Balance")
def balance(message):

    users = load_users()
    uid = str(message.from_user.id)

    bal = users[uid]['balance']

    bot.send_message(
        message.chat.id,
        f"💰 Your Balance: {bal} Coins"
    )


# =====================================================
# REFERRAL
# =====================================================


@bot.message_handler(func=lambda m: m.text == "👥 Refer")
def refer(message):

    users = load_users()
    uid = str(message.from_user.id)

    refs = users[uid]['referral']

    link = f"https://t.me/{bot.get_me().username}?start={uid}"

    text = f"""
👥 <b>REFERRAL SYSTEM</b>

🔗 Your Link:
<code>{link}</code>

👤 Total Referrals: {refs}

🎁 Earn 1 Coin Per Invite
"""

    bot.send_message(message.chat.id, text)


# =====================================================
# BONUS
# =====================================================


@bot.message_handler(func=lambda m: m.text == "🎁 Bonus")
def bonus(message):

    users = load_users()
    uid = str(message.from_user.id)

    if users[uid]['bonus'] == "yes":
        bot.send_message(
            message.chat.id,
            "❌ Daily Bonus Already Claimed"
        )
        return

    users[uid]['bonus'] = "yes"
    users[uid]['balance'] += 5

    save_users(users)

    bot.send_message(
        message.chat.id,
        "🎉 You Received 5 Coins"
    )


# =====================================================
# STATISTICS
# =====================================================


@bot.message_handler(func=lambda m: m.text == "📊 Statistics")
def stats(message):

    users = load_users()

    text = f"""
📊 <b>BOT STATISTICS</b>

👥 Total Users: {len(users)}
⚡ Status: Online
🚀 Version: Ultra Pro
"""

    bot.send_message(message.chat.id, text)


# =====================================================
# HELP
# =====================================================


@bot.message_handler(func=lambda m: m.text == "ℹ️ Help")
def help_cmd(message):
    bot.send_message(message.chat.id, HELP_TEXT)


# =====================================================
# ADMIN PANEL
# =====================================================


@bot.message_handler(func=lambda m: m.text == "⚙️ Admin Panel")
def admin(message):

    if message.from_user.id != ADMIN_ID:
        return

    markup = types.InlineKeyboardMarkup()

    b1 = types.InlineKeyboardButton(
        "📢 Broadcast",
        callback_data="broadcast"
    )

    b2 = types.InlineKeyboardButton(
        "📊 Users",
        callback_data="users"
    )

    markup.add(b1)
    markup.add(b2)

    bot.send_message(
        message.chat.id,
        "⚙️ ADMIN CONTROL PANEL",
        reply_markup=markup
    )


# =====================================================
# ADMIN CALLBACKS
# =====================================================


@bot.callback_query_handler(func=lambda c: c.data == "users")
def user_count(call):

    users = load_users()

    bot.send_message(
        call.message.chat.id,
        f"👥 Total Users: {len(users)}"
    )


@bot.callback_query_handler(func=lambda c: c.data == "broadcast")
def bc(call):

    msg = bot.send_message(
        call.message.chat.id,
        "📢 Send Broadcast Message"
    )

    bot.register_next_step_handler(msg, send_bc)


# =====================================================
# SEND BROADCAST
# =====================================================



def send_bc(message):

    if message.from_user.id != ADMIN_ID:
        return

    users = load_users()

    sent = 0

    for uid in users:

        try:
            bot.send_message(uid, message.text)
            sent += 1
        except:
            pass

    bot.send_message(
        message.chat.id,
        f"✅ Broadcast Sent To {sent} Users"
    )


# =====================================================
# IP LOOKUP BUTTON
# =====================================================


@bot.message_handler(func=lambda m: m.text == "🌍 IP Lookup")
def ask_ip(message):

    msg = bot.send_message(
        message.chat.id,
        "🌍 Send Target IP Address"
    )

    bot.register_next_step_handler(msg, ip_lookup)


# =====================================================
# IP LOOKUP SYSTEM
# =====================================================



def ip_lookup(message):

    ip = message.text.strip()

    loading = bot.send_message(
        message.chat.id,
        "⚡ Starting Scan..."
    )

    frames = [
        "🌍 Connecting To Database...",
        "📡 Scanning ISP...",
        "🛰 Fetching Geo Location...",
        "⚡ Building Report...",
        "✅ Scan Completed"
    ]

    for frame in frames:
        time.sleep(1)

        try:
            bot.edit_message_text(
                frame,
                message.chat.id,
                loading.message_id
            )
        except:
            pass

    try:

        url = f"http://ip-api.com/json/{ip}"

        data = requests.get(url).json()

        if data['status'] != 'success':
            bot.send_message(
                message.chat.id,
                "❌ Invalid IP Address"
            )
            return

        country = data.get('country', 'N/A')
        city = data.get('city', 'N/A')
        isp = data.get('isp', 'N/A')
        org = data.get('org', 'N/A')
        lat = data.get('lat', 'N/A')
        lon = data.get('lon', 'N/A')
        timezone = data.get('timezone', 'N/A')
        region = data.get('regionName', 'N/A')
        zipc = data.get('zip', 'N/A')

        maps = f"https://maps.google.com/?q={lat},{lon}"

        text = f"""
╔════════════════╗
    🌍 IP RESULT
╚════════════════╝

🧠 IP Address
┗ <code>{ip}</code>

🌎 Country
┗ {country}

🏙 City
┗ {city}

📍 Region
┗ {region}

📡 ISP
┗ {isp}

🏢 Organization
┗ {org}

🕒 Timezone
┗ {timezone}

📮 ZIP Code
┗ {zipc}

📍 Latitude
┗ {lat}

📍 Longitude
┗ {lon}

🗺 Maps Link
┗ {maps}

━━━━━━━━━━━━━━━━━━
⚡ Ultra Pro Scan Completed
━━━━━━━━━━━━━━━━━━
"""

        markup = types.InlineKeyboardMarkup()

        btn = types.InlineKeyboardButton(
            "🗺 OPEN MAPS",
            url=maps
        )

        markup.add(btn)

        bot.send_message(
            message.chat.id,
            text,
            reply_markup=markup,
            disable_web_page_preview=True
        )

    except Exception as e:

        bot.send_message(
            message.chat.id,
            f"❌ Error: {e}"
        )


# =====================================================
# UNKNOWN MESSAGE
# =====================================================


@bot.message_handler(func=lambda m: True)
def unknown(message):

    bot.send_message(
        message.chat.id,
        "❌ Unknown Command"
    )


# =====================================================
# RUN BOT
# =====================================================


print("BOT RUNNING...")

bot.infinity_polling()
