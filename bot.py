# =========================================================
# ULTRA PRO AI IMAGE GENERATOR BOT
# SINGLE FILE STABLE VERSION
# =========================================================

import telebot
from telebot import types
import sqlite3
import time
from urllib.parse import quote

# =========================================================
# CONFIG
# =========================================================

TOKEN = "8951724363:AAERDshtKMOeJlWyAyEqxxCnzv7Q5jd6Ehk"

CHANNEL_1 = "unknown_owner_info"
CHANNEL_2 = "mbtcyber"

ADMIN_ID = 7276206449

REF_BONUS = 5
VERIFY_BONUS = 2
GEN_COST = 1
START_POINTS = 5

# =========================================================
# BOT
# =========================================================

bot = telebot.TeleBot(
    TOKEN,
    parse_mode="HTML"
)

# =========================================================
# DATABASE
# =========================================================

db = sqlite3.connect(
    "bot.db",
    check_same_thread=False
)

cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY,
    points INTEGER,
    referrals INTEGER,
    verified INTEGER,
    banned INTEGER
)
""")

db.commit()

# =========================================================
# ADD USER
# =========================================================

def add_user(user_id):

    cursor.execute(
        "SELECT * FROM users WHERE user_id=?",
        (user_id,)
    )

    user = cursor.fetchone()

    if not user:

        cursor.execute(
            """
            INSERT INTO users
            VALUES(?,?,?,?,?)
            """,
            (
                user_id,
                START_POINTS,
                0,
                0,
                0
            )
        )

        db.commit()

# =========================================================
# GET USER
# =========================================================

def get_user(user_id):

    cursor.execute(
        "SELECT * FROM users WHERE user_id=?",
        (user_id,)
    )

    return cursor.fetchone()

# =========================================================
# ADD POINTS
# =========================================================

def add_points(user_id, amount):

    cursor.execute(
        """
        UPDATE users
        SET points = points + ?
        WHERE user_id=?
        """,
        (
            amount,
            user_id
        )
    )

    db.commit()

# =========================================================
# REMOVE POINTS
# =========================================================

def remove_points(user_id, amount):

    cursor.execute(
        """
        UPDATE users
        SET points = points - ?
        WHERE user_id=?
        """,
        (
            amount,
            user_id
        )
    )

    db.commit()

# =========================================================
# CHECK JOIN
# =========================================================

def joined(user_id):

    try:

        ch1 = bot.get_chat_member(
            f"@{CHANNEL_1}",
            user_id
        )

        ch2 = bot.get_chat_member(
            f"@{CHANNEL_2}",
            user_id
        )

        ok1 = ch1.status in [
            "member",
            "administrator",
            "creator"
        ]

        ok2 = ch2.status in [
            "member",
            "administrator",
            "creator"
        ]

        return ok1 and ok2

    except:

        return False

# =========================================================
# MENU
# =========================================================

def menu(user_id):

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        row_width=2
    )

    b1 = types.KeyboardButton("🎨 Generate")
    b2 = types.KeyboardButton("👤 Profile")

    b3 = types.KeyboardButton("💰 Points")
    b4 = types.KeyboardButton("👥 Refer")

    b5 = types.KeyboardButton("📊 Statistics")
    b6 = types.KeyboardButton("ℹ️ Help")

    markup.add(b1, b2)
    markup.add(b3, b4)
    markup.add(b5, b6)

    if user_id == ADMIN_ID:

        admin = types.KeyboardButton(
            "⚙️ Admin Panel"
        )

        markup.add(admin)

    return markup

# =========================================================
# WELCOME TEXT
# =========================================================

WELCOME = """
<blockquote>
🚀 <b>ULTRA AI IMAGE GENERATOR</b>

━━━━━━━━━━━━━━━━━━
🎨 Generate AI Images
⚡ Ultra Fast Engine
🧠 Smart AI System
💎 Premium Features
━━━━━━━━━━━━━━━━━━

🎁 Join Channels & Earn Bonus
</blockquote>
"""

# =========================================================
# START
# =========================================================

@bot.message_handler(commands=['start'])
def start(message):

    user_id = message.from_user.id

    add_user(user_id)

    user = get_user(user_id)

    # BAN CHECK

    if user[4] == 1:

        bot.send_message(
            message.chat.id,
            "🚫 You Are Banned"
        )

        return

    # JOIN CHECK

    if not joined(user_id):

        markup = types.InlineKeyboardMarkup()

        b1 = types.InlineKeyboardButton(
            "📢 CHANNEL 1",
            url=f"https://t.me/{CHANNEL_1}"
        )

        b2 = types.InlineKeyboardButton(
            "📢 CHANNEL 2",
            url=f"https://t.me/{CHANNEL_2}"
        )

        b3 = types.InlineKeyboardButton(
            "✅ VERIFY",
            callback_data="verify"
        )

        markup.add(b1)
        markup.add(b2)
        markup.add(b3)

        bot.send_message(
            message.chat.id,
            """
⚠️ JOIN BOTH CHANNELS

🎁 Earn 2 Bonus Points
""",
            reply_markup=markup
        )

        return

    bot.send_message(
        message.chat.id,
        WELCOME,
        reply_markup=menu(user_id)
    )

# =========================================================
# PROFILE
# =========================================================

@bot.message_handler(func=lambda m: m.text == "👤 Profile")
def profile(message):

    user = get_user(message.from_user.id)

    text = f"""
╔══════════════╗
   👤 PROFILE
╚══════════════╝

🆔 ID:
<code>{message.from_user.id}</code>

💰 Points:
{user[1]}

👥 Referrals:
{user[2]}

💎 Status:
Free User
"""

    bot.send_message(
        message.chat.id,
        text
    )

# =========================================================
# POINTS
# =========================================================

@bot.message_handler(func=lambda m: m.text == "💰 Points")
def points(message):

    user = get_user(message.from_user.id)

    bot.send_message(
        message.chat.id,
        f"💰 Your Points: {user[1]}"
    )

# =========================================================
# REFER
# =========================================================

@bot.message_handler(func=lambda m: m.text == "👥 Refer")
def refer(message):

    user = get_user(message.from_user.id)

    link = (
        f"https://t.me/"
        f"{bot.get_me().username}"
        f"?start={message.from_user.id}"
    )

    text = f"""
👥 <b>REFERRAL SYSTEM</b>

🔗 Your Link:
<code>{link}</code>

🎁 Reward:
{REF_BONUS} Points

👤 Total Referrals:
{user[2]}
"""

    bot.send_message(
        message.chat.id,
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

    total = cursor.fetchone()[0]

    bot.send_message(
        message.chat.id,
        f"""
📊 BOT STATISTICS

👥 Users: {total}

⚡ Status: Online
🚀 System: Stable
"""
    )

# =========================================================
# HELP
# =========================================================

@bot.message_handler(func=lambda m: m.text == "ℹ️ Help")
def help_cmd(message):

    bot.send_message(
        message.chat.id,
        """
ℹ️ HELP CENTER

🎨 Generate AI Images
💰 Cost: 1 Point

👥 Invite Friends
🎁 Earn 5 Points

📢 Verify Channels
🎉 Earn 2 Bonus

☠️ DEVELOPER: @Unkonwn_BMT
"""
    )

# =========================================================
# GENERATE BUTTON
# =========================================================

@bot.message_handler(func=lambda m: m.text == "🎨 Generate")
def ask_prompt(message):

    user = get_user(message.from_user.id)

    # BAN CHECK

    if user[4] == 1:

        bot.send_message(
            message.chat.id,
            "🚫 You Are Banned"
        )

        return

    # POINT CHECK

    if user[1] < GEN_COST:

        bot.send_message(
            message.chat.id,
            """
❌ Not Enough Points

👥 Refer Friends To Earn More
"""
        )

        return

    msg = bot.send_message(
        message.chat.id,
        "🎨 Send Your Prompt:"
    )

    bot.register_next_step_handler(
        msg,
        generate
    )

# =========================================================
# GENERATE IMAGE
# =========================================================

def generate(message):

    user_id = message.from_user.id

    prompt = message.text

    loading = bot.send_message(
        message.chat.id,
        "⚡ Generating..."
    )

    frames = [
        "🧠 Processing...",
        "🎨 Drawing...",
        "🌌 Rendering...",
        "⚡ Finalizing...",
        "✅ Done"
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

        remove_points(
            user_id,
            GEN_COST
        )

        encoded = quote(prompt)

        image_url = (
            "https://img.jalam946262.workers.dev/?prompt="
            + encoded
        )

        markup = types.InlineKeyboardMarkup()

        b1 = types.InlineKeyboardButton(
            "🔁 Generate Again",
            callback_data="regen"
        )

        b2 = types.InlineKeyboardButton(
            "📢 Channel",
            url=f"https://t.me/{CHANNEL_1}"
        )

        markup.add(b1)
        markup.add(b2)

        caption = f"""
🎨 <b>AI IMAGE GENERATED</b>

✨ Prompt:
<code>{prompt}</code>

💰 -1 Point Used

☠️ DEVELOPER: @Unkonwn_BMT
"""

        bot.send_photo(
            message.chat.id,
            image_url,
            caption=caption,
            reply_markup=markup
        )

    except Exception as e:

        bot.send_message(
            message.chat.id,
            f"❌ Error:\n<code>{e}</code>"
        )

# =========================================================
# ADMIN PANEL
# =========================================================

@bot.message_handler(func=lambda m: m.text == "⚙️ Admin Panel")
def admin_panel(message):

    if message.from_user.id != ADMIN_ID:
        return

    markup = types.InlineKeyboardMarkup(
        row_width=2
    )

    b1 = types.InlineKeyboardButton(
        "📢 Broadcast",
        callback_data="broadcast"
    )

    b2 = types.InlineKeyboardButton(
        "👥 Users",
        callback_data="users"
    )

    b3 = types.InlineKeyboardButton(
        "💰 Give Points",
        callback_data="givepoints"
    )

    b4 = types.InlineKeyboardButton(
        "🚫 Ban",
        callback_data="ban"
    )

    b5 = types.InlineKeyboardButton(
        "✅ Unban",
        callback_data="unban"
    )

    markup.add(b1, b2)
    markup.add(b3, b4)
    markup.add(b5)

    bot.send_message(
        message.chat.id,
        """
⚙️ ADMIN PANEL

🧠 Full Control System
""",
        reply_markup=markup
    )

# =========================================================
# CALLBACK HANDLER
# =========================================================

@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):

    user_id = call.from_user.id

    # VERIFY

    if call.data == "verify":

        if joined(user_id):

            user = get_user(user_id)

            if user[3] == 0:

                add_points(
                    user_id,
                    VERIFY_BONUS
                )

                cursor.execute(
                    """
                    UPDATE users
                    SET verified=1
                    WHERE user_id=?
                    """,
                    (user_id,)
                )

                db.commit()

                bot.answer_callback_query(
                    call.id,
                    "🎉 Verification Success"
                )

            else:

                bot.answer_callback_query(
                    call.id,
                    "✅ Already Verified"
                )

            bot.send_message(
                call.message.chat.id,
                WELCOME,
                reply_markup=menu(user_id)
            )

        else:

            bot.answer_callback_query(
                call.id,
                "❌ Join Both Channels"
            )

    # REGENERATE

    elif call.data == "regen":

        msg = bot.send_message(
            call.message.chat.id,
            "🎨 Send Prompt"
        )

        bot.register_next_step_handler(
            msg,
            generate
        )

    # ADMIN ONLY

    elif user_id == ADMIN_ID:

        # USERS

        if call.data == "users":

            cursor.execute(
                "SELECT COUNT(*) FROM users"
            )

            total = cursor.fetchone()[0]

            bot.send_message(
                call.message.chat.id,
                f"👥 Total Users: {total}"
            )

        # BROADCAST

        elif call.data == "broadcast":

            msg = bot.send_message(
                call.message.chat.id,
                "📢 Send Broadcast Message"
            )

            bot.register_next_step_handler(
                msg,
                send_broadcast
            )

        # GIVE POINTS

        elif call.data == "givepoints":

            msg = bot.send_message(
                call.message.chat.id,
                "💰 Send:\nUserID Points"
            )

            bot.register_next_step_handler(
                msg,
                give_points
            )

        # BAN

        elif call.data == "ban":

            msg = bot.send_message(
                call.message.chat.id,
                "🚫 Send User ID"
            )

            bot.register_next_step_handler(
                msg,
                ban_user
            )

        # UNBAN

        elif call.data == "unban":

            msg = bot.send_message(
                call.message.chat.id,
                "✅ Send User ID"
            )

            bot.register_next_step_handler(
                msg,
                unban_user
            )

# =========================================================
# BROADCAST
# =========================================================

def send_broadcast(message):

    cursor.execute(
        "SELECT user_id FROM users"
    )

    users = cursor.fetchall()

    sent = 0

    for user in users:

        try:

            bot.send_message(
                user[0],
                f"📢 ADMIN MESSAGE\n\n{message.text}"
            )

            sent += 1

        except:
            pass

    bot.send_message(
        message.chat.id,
        f"✅ Sent To {sent} Users"
    )

# =========================================================
# GIVE POINTS
# =========================================================

def give_points(message):

    try:

        data = message.text.split()

        user_id = int(data[0])
        amount = int(data[1])

        add_points(
            user_id,
            amount
        )

        bot.send_message(
            message.chat.id,
            "✅ Points Added"
        )

    except:

        bot.send_message(
            message.chat.id,
            "❌ Invalid Format"
        )

# =========================================================
# BAN USER
# =========================================================

def ban_user(message):

    try:

        user_id = int(message.text)

        cursor.execute(
            """
            UPDATE users
            SET banned=1
            WHERE user_id=?
            """,
            (user_id,)
        )

        db.commit()

        bot.send_message(
            message.chat.id,
            "🚫 User Banned"
        )

    except:

        bot.send_message(
            message.chat.id,
            "❌ Invalid ID"
        )

# =========================================================
# UNBAN USER
# =========================================================

def unban_user(message):

    try:

        user_id = int(message.text)

        cursor.execute(
            """
            UPDATE users
            SET banned=0
            WHERE user_id=?
            """,
            (user_id,)
        )

        db.commit()

        bot.send_message(
            message.chat.id,
            "✅ User Unbanned"
        )

    except:

        bot.send_message(
            message.chat.id,
            "❌ Invalid ID"
        )

# =========================================================
# UNKNOWN
# =========================================================

@bot.message_handler(func=lambda m: True)
def unknown(message):

    bot.send_message(
        message.chat.id,
        "❌ Use Menu Buttons"
    )

# =========================================================
# RUN
# =========================================================

print("BOT RUNNING...")

bot.infinity_polling()
