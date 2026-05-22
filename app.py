import os
import sys
import asyncio
import traceback
import threading

from http.server import BaseHTTPRequestHandler, HTTPServer

from pyrogram import Client, filters, idle
from pyrogram.types import Message

# ✅ الصحيح للنسخة القديمة المستقرة
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream


# =========================
# Railway Health Check
# =========================

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()


# =========================
# ENV
# =========================

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
SESSION_STRING = os.getenv("SESSION_STRING")
OWNER_ID = os.getenv("OWNER_ID")

if not all([API_ID, API_HASH, BOT_TOKEN, SESSION_STRING]):
    print("Missing env", flush=True)
    sys.exit(1)

API_ID = int(API_ID)

OWNER_ID = int(OWNER_ID) if OWNER_ID and OWNER_ID.isdigit() else None

print("Starting bot...", flush=True)


# =========================
# Clients
# =========================

bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

assistant = Client("assistant", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

call = PyTgCalls(assistant)


# =========================
# State
# =========================

states = {}


# =========================
# Debug
# =========================

@bot.on_message(filters.all)
async def debug(_, msg):
    try:
        print("MSG:", msg.text, flush=True)
    except:
        pass


# =========================
# Main
# =========================

@bot.on_message(filters.private & filters.text)
async def handler(_, message: Message):

    try:
        text = message.text.strip()
        uid = message.from_user.id

        if text.startswith("/start"):
            states[uid] = {"step": "ch"}
            await message.reply_text("أرسل القناة")
            return

        if text.startswith("/stop"):
            args = text.split(maxsplit=1)
            chat = await bot.get_chat(args[1])
            await call.leave_group_call(chat.id)
            await message.reply_text("تم الإيقاف")
            return

        state = states.get(uid)
        if not state:
            return

        if state["step"] == "ch":
            states[uid] = {"step": "url", "ch": text}
            await message.reply_text("أرسل الرابط")
            return

        if state["step"] == "url":
            ch = state["ch"]
            url = text

            chat = await bot.get_chat(ch)

            await call.join_group_call(
                chat.id,
                MediaStream(url)
            )

            await message.reply_text("تم التشغيل")
            states.pop(uid, None)

    except Exception:
        traceback.print_exc()


# =========================
# RUN
# =========================

async def main():

    await bot.start()
    await assistant.start()
    await call.start()

    print("BOT ONLINE", flush=True)

    await idle()

    await bot.stop()
    await assistant.stop()
    await call.stop()


if __name__ == "__main__":
    asyncio.run(main())
