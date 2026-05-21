import os
import asyncio

from pyrogram import Client
from pytgcalls import PyTgCalls, idle

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SESSION_STRING = os.environ["SESSION_STRING"]
CHAT_ID = int(os.environ["CHAT_ID"])
RADIO_URL = os.environ.get("RADIO_URL", "https://stream.quranrad.io/abdulbasit")

app = Client(
    SESSION_STRING,
    api_id=API_ID,
    api_hash=API_HASH
)

call_py = PyTgCalls(app)

async def main():
    await app.start()
    await call_py.start()
    call_py.play(CHAT_ID, RADIO_URL)
    print("🎧 البث الصوتي شغال")
    await idle()

asyncio.run(main())
