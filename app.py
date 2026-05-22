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
# HEALTH SERVER
# =====================

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def server():
    HTTPServer(("0.0.0.0", int(os.getenv("PORT", 8080))), Handler).serve_forever()

threading.Thread(target=server, daemon=True).start()


# =====================
# USERBOT INIT (SMART)
# =====================

def create_client():

    # لو الجلسة مش موجودة → Login manual mode
    if not SESSION_STRING or SESSION_STRING.strip() == "":
        print("⚠️ No SESSION_STRING, switching to manual login...")
        return Client("userbot", api_id=API_ID, api_hash=API_HASH)

    # Session mode
    return Client(
        "userbot",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=SESSION_STRING
    )


user = create_client()
call = PyTgCalls(user)


# =====================
# AUTO STREAM
# =====================

async def start_stream():

    try:
        print("🚀 Connecting...")

        chat = await user.get_chat(CHANNEL)

        await call.join_group_call(
            chat.id,
            MediaStream(STREAM_URL)
        )

        print("🔊 STREAM STARTED")

    except Exception:
        traceback.print_exc()


# =====================
# MAIN
# =====================

async def main():

    await user.start()
    await call.start()

    print("USERBOT ONLINE ✅")

    await start_stream()

    await idle()

    await user.stop()
    await call.stop()


if __name__ == "__main__":
    asyncio.run(main())
