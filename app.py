import os
import asyncio
import traceback
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from pyrogram import Client, idle

from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream


# =====================
# ENV
# =====================

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")

CHANNEL = os.getenv("CHANNEL")
STREAM_URL = os.getenv("STREAM_URL")


# =====================
# Health Server
# =====================

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_server():
    port = int(os.getenv("PORT", 8080))
    HTTPServer(("0.0.0.0", port), HealthHandler).serve_forever()

threading.Thread(target=run_server, daemon=True).start()


# =====================
# USERBOT
# =====================

user = Client(
    "userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

call = PyTgCalls(user)


# =====================
# AUTO START FUNCTION
# =====================

async def start_stream():

    try:

        print("🚀 Joining channel...", flush=True)

        chat = await user.get_chat(CHANNEL)

        await call.join_group_call(
            chat.id,
            MediaStream(STREAM_URL)
        )

        print("🔊 STREAM STARTED AUTOMATICALLY", flush=True)

    except Exception:
        traceback.print_exc()


# =====================
# MAIN
# =====================

async def main():

    await user.start()
    await call.start()

    print("USERBOT ONLINE ✅", flush=True)

    # 🔥 يبدأ تلقائي بدون أي أوامر
    await start_stream()

    await idle()

    await user.stop()
    await call.stop()


if __name__ == "__main__":
    asyncio.run(main())
