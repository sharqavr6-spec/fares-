import os
import sys
import asyncio
import traceback
import threading
import subprocess

from http.server import BaseHTTPRequestHandler, HTTPServer
from pyrogram import Client, filters, idle

# =====================
# Health server
# =====================

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_server():
    port = int(os.environ.get("PORT", 8080))
    HTTPServer(("0.0.0.0", port), HealthHandler).serve_forever()

threading.Thread(target=run_server, daemon=True).start()

# =====================
# ENV
# =====================

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

user_states = {}

# =====================
# تشغيل صوت (بديل pytgcalls)
# =====================

def start_stream(chat_id, url):
    cmd = [
        "ffmpeg",
        "-re",
        "-i", url,
        "-f", "mp3",
        "pipe:1"
    ]
    return subprocess.Popen(cmd)

streams = {}

# =====================
# Bot logic
# =====================

@bot.on_message(filters.private & filters.text)
async def handler(client, message):

    text = message.text.strip()
    uid = message.from_user.id

    if text == "/start":
        user_states[uid] = {"step": "channel"}
        await message.reply("أرسل القناة")
        return

    state = user_states.get(uid)
    if not state:
        return

    if state["step"] == "channel":
        user_states[uid] = {"step": "url", "channel": text}
        await message.reply("أرسل رابط البث")
        return

    if state["step"] == "url":
        channel = state["channel"]
        url = text

        streams[channel] = start_stream(channel, url)

        await message.reply("✅ تم تشغيل البث (FFMPEG MODE)")
        user_states.pop(uid, None)

async def main():
    await bot.start()
    print("BOT ONLINE")
    await idle()
    await bot.stop()

if __name__ == "__main__":
    asyncio.run(main())
