import os
import sys
import asyncio
import traceback
import threading

from http.server import BaseHTTPRequestHandler, HTTPServer

from pyrogram import Client, filters, idle
from pyrogram.types import Message

from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import InputAudioStream

# =========================
# Web Server لـ Railway
# =========================

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    print(f"🌐 Web server running on port {port}", flush=True)
    server.serve_forever()

threading.Thread(target=run_web_server, daemon=True).start()

# =========================
# Environment Variables
# =========================

API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
SESSION_STRING = os.environ.get("SESSION_STRING")
OWNER_ID = os.environ.get("OWNER_ID")

if not all([API_ID, API_HASH, BOT_TOKEN, SESSION_STRING]):
    print("❌ Missing environment variables", flush=True)
    sys.exit(1)

API_ID = int(API_ID)

if OWNER_ID and OWNER_ID.isdigit():
    OWNER_ID = int(OWNER_ID)
else:
    OWNER_ID = None

print("🚀 Starting Bot...", flush=True)

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

call_py = PyTgCalls(assistant)

# =========================
# User States
# =========================

user_states = {}

# =========================
# Debug Messages
# =========================

@bot.on_message(filters.all)
async def debug_all(client, message):
    try:
        print(
            f"📩 Message Received: {message.text}",
            flush=True
        )
    except:
        pass

# =========================
# Main Router
# =========================

@bot.on_message(filters.private & filters.text)
async def main_router(client: Client, message: Message):

    try:

        text = message.text.strip()
        user_id = message.from_user.id

        print(f"⚡ Processing: {text}", flush=True)

        # =========================
        # START
        # =========================

        if text.startswith("/start"):

            user_states[user_id] = {
                "step": "WAITING_CHANNEL"
            }

            await message.reply_text(
                "📢 أرسل يوزر القناة أو الآيدي"
            )

            return

        # =========================
        # STOP
        # =========================

        if text.startswith("/stop"):

            args = text.split(maxsplit=1)

            if len(args) < 2:
                await message.reply_text(
                    "❌ الاستخدام:\n/stop @channel"
                )
                return

            channel_input = args[1]

            try:

                chat = await bot.get_chat(channel_input)

                await call_py.leave_group_call(chat.id)

                await message.reply_text(
                    "🛑 تم إيقاف البث"
                )

            except Exception as e:

                await message.reply_text(
                    f"❌ Error:\n{e}"
                )

            return

        # =========================
        # States
        # =========================

        state = user_states.get(user_id)

        if not state:
            return

        step = state.get("step")

        # =========================
        # Channel Step
        # =========================

        if step == "WAITING_CHANNEL":

            user_states[user_id] = {
                "step": "WAITING_URL",
                "channel": text
            }

            await message.reply_text(
                "🔗 أرسل رابط البث المباشر"
            )

            return

        # =========================
        # URL Step
        # =========================

        if step == "WAITING_URL":

            stream_url = text
            channel_input = state.get("channel")

            user_states.pop(user_id, None)

            try:

                chat = await bot.get_chat(channel_input)

                print(f"🎵 Joining VC: {chat.id}", flush=True)

                await call_py.join_group_call(
                    chat.id,
                    InputAudioStream(stream_url)
                )

                await message.reply_text(
                    f"✅ تم تشغيل البث في:\n{channel_input}"
                )

            except Exception as e:

                traceback.print_exc()

                await message.reply_text(
                    f"❌ فشل التشغيل:\n{e}"
                )

    except Exception:

        traceback.print_exc()

# =========================
# Start Services
# =========================

async def start_bot():

    try:

        print("🤖 Starting BOT...", flush=True)

        await bot.start()

        print("👤 Starting Assistant...", flush=True)

        await assistant.start()

        print("📞 Starting PyTgCalls...", flush=True)

        await call_py.start()

        print("✅ BOT IS ONLINE", flush=True)

        if OWNER_ID:

            try:

                await bot.send_message(
                    OWNER_ID,
                    "✅ البوت اشتغل بنجاح"
                )

            except:
                pass

        await idle()

    except Exception:

        traceback.print_exc()

# =========================
# Run
# =========================

if __name__ == "__main__":
    asyncio.run(start_bot())
