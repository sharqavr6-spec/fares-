import os
import asyncio

from pyrogram import Client
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream.audio_piped import AudioPiped

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")
CHAT_ID = int(os.environ.get("CHAT_ID"))

RADIO_URL = os.environ.get(
    "RADIO_URL",
    "https://stream.quranrad.io/abdulbasit"
)

app = Client(
    "radio-bot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

call_py = PyTgCalls(app)

async def main():
    await app.start()
    print("✅ تم تشغيل الحساب")

    await call_py.start()

    await call_py.join_group_call(
        CHAT_ID,
        AudioPiped(RADIO_URL)
    )

    print("🎧 البث الصوتي يعمل الآن")

    await asyncio.Event().wait()

asyncio.run(main())
