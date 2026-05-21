import os
import asyncio

from pyrogram import Client
from pytgcalls import PyTgCalls

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SESSION_STRING = os.environ["SESSION_STRING"]
CHAT_ID = int(os.environ["CHAT_ID"])

RADIO_URL = os.environ.get("RADIO_URL", "https://stream.quranrad.io/abdulbasit")

app = Client(
    "quran-radio",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

call_py = PyTgCalls(app)

async def main():
    await app.start()
    print("✅ تم تشغيل الحساب")

    await call_py.start()
    print("✅ تم تشغيل PyTgCalls")

    call_py.play(CHAT_ID, RADIO_URL)
    print("🎧 بدأ بث إذاعة القرآن الكريم")

    await asyncio.Event().wait()

asyncio.run(main())
