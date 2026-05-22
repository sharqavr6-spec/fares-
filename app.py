import os
import sys
import asyncio
import traceback
import threading

from http.server import BaseHTTPRequestHandler, HTTPServer

from pyrogram import Client, filters, idle
from pyrogram.types import Message

# ✅ الاستيراد الصحيح والمتوافق
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped

# =========================
# Railway Health Server
# =========================

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    print(f"🌐 Server running on {port}", flush=True)
    server.serve_forever()

threading.Thread(target=run_web_server, daemon=True).start()

# =========================
# ENV
# =========================

API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
SESSION_STRING = os.environ.get("SESSION_STRING")
OWNER_ID = os.environ.get("OWNER_ID")

if not all([API_ID, API_HASH, BOT_TOKEN, SESSION_STRING]):
    print("❌ Missing ENV vars", flush=True)
    sys.exit(1)

API_ID = int(API_ID)

if OWNER_ID and OWNER_ID.isdigit():
    OWNER_ID = int(OWNER_ID)
else:
    OWNER_ID = None

print("🚀 Bot starting...", flush=True)

# =========================
# Clients
# =========================

bot = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

assistant = Client(
    "assistant",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

call = PyTgCalls(assistant)

# =========================
# State
# =========================

user_states = {}

# =========================
# Debug all messages
# =========================

@bot.on_message(filters.all)
async def debug(client, message):
    try:
        print(f"📩 {message.text}", flush=True)
    except:
        pass

# =========================
# Main handler
# =========================

@bot.on_message(filters.private & filters.text)
async def handler(client: Client, message: Message):

    try:
        text = message.text.strip()
        user_id = message.from_user.id

        print(f"⚡ {text}", flush=True)

        # ================= START =================
        if text.startswith("/start"):
            user_states[user_id] = {"step": "channel"}
            await message.reply_text("📌 ابعت يوزر القناة")
            return

        # ================= STOP =================
        if text.startswith("/stop"):

            args = text.split(maxsplit=1)
            if len(args) < 2:
                await message.reply_text("اكتب /stop @channel")
                return

            chat = await bot.get_chat(args[1])

            await call.leave_group_call(chat.id)

            await message.reply_text("🛑 تم الإيقاف")
            return

        # ================= STATE =================
        state = user_states.get(user_id)
        if not state:
            return

        # ================= CHANNEL =================
        if state["step"] == "channel":

            user_states[user_id] = {
                "step": "url",
                "channel": text
            }

            await message.reply_text("🔗 ابعت رابط البث")
            return

        # ================= URL =================
        if state["step"] == "url":

            channel = state["channel"]
            url = text

            user_states.pop(user_id, None)

            chat = await bot.get_chat(channel)

            await call.join_group_call(
                chat.id,
                AudioPiped(url)
            )

            await message.reply_text("✅ تم تشغيل البث")

    except Exception:
        traceback.print_exc()


# =========================
# STARTUP
# =========================

async def main():

    print("🤖 starting bot...", flush=True)

    await bot.start()
    await assistant.start()
    await call.start()

    print("✅ BOT IS ONLINE", flush=True)

    if OWNER_ID:
        try:
            await bot.send_message(OWNER_ID, "✅ Bot is online")
        except:
            pass

    await idle()

    await bot.stop()
    await assistant.stop()
    await call.stop()


if __name__ == "__main__":
    asyncio.run(main())
