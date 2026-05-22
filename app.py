import os
import asyncio
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SESSION = os.environ["SESSION"]
CHAT_ID = int(os.environ["CHAT_ID"])
RADIO_URL = os.environ["RADIO_URL"]

app = Client("my_account", api_id=API_ID, api_hash=API_HASH, session_string=SESSION)
call_py = PyTgCalls(app)

@app.on_message(filters.command("set_url", prefixes="/") & filters.me)
async def change_radio_url(client, message):
    global RADIO_URL
    if len(message.command) > 1:
        RADIO_URL = message.command[1]
        await call_py.change_stream(
            CHAT_ID,
            audio_source=AudioPiped(RADIO_URL),
        )
        await message.edit_text(f"تم تغيير رابط الإذاعة إلى: {RADIO_URL}")

@app.on_message(filters.command("stop", prefixes="/") & filters.me)
async def stop_stream(client, message):
    await call_py.pause_stream(CHAT_ID)
    await message.edit_text("تم إيقاف البث مؤقتاً.")

@app.on_message(filters.command("resume", prefixes="/") & filters.me)
async def resume_stream(client, message):
    await call_py.resume_stream(CHAT_ID)
    await message.edit_text("تم استئناف البث.")

async def main():
    await app.start()
    await call_py.start()
    await call_py.join_group_call(
        chat_id=CHAT_ID, audio_source=AudioPiped(RADIO_URL)
    )

with app:
    app.run(main())

