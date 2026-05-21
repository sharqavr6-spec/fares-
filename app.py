import os
import asyncio

from pyrogram import Client
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SESSION = os.environ["SESSION"]
CHAT_ID = int(os.environ["CHAT_ID"])

RADIO_URL = "https://stream.quranrad.io/abdulbasit"

app = Client(
    SESSION,
    api_id=API_ID,
    api_hash=API_HASH
)

call_py = PyTgCalls(app)

async def main():
    await app.start()
    print("✅ تم تشغيل الحساب")

    await call_py.start()
    print("✅ تم تشغيل الكول")

    await call_py.join_group_call(
        CHAT_ID,
        AudioPiped(RADIO_URL)
    )

    print("🎧 بث القرآن يعمل الآن")

    await asyncio.Event().wait()

asyncio.run(main())
