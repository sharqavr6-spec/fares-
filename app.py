import os
import asyncio
import sys
from pyrogram import Client
from pytgcalls.group_call_factory import GroupCallFactory
from pytgcalls.types import AudioPiped

API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")
CHAT_ID = os.environ.get("CHAT_ID")
RADIO_URL = os.environ.get("RADIO_URL")

if not all([API_ID, API_HASH, SESSION_STRING, CHAT_ID, RADIO_URL]):
    print("خطأ: يرجى التأكد من إضافة جميع متغيرات البيئة.")
    sys.exit(1)

try:
    API_ID = int(API_ID)
    CHAT_ID = int(CHAT_ID)
except ValueError:
    print("خطأ: يجب أن تكون قيم API ID و CHAT ID أرقاماً.")
    sys.exit(1)

app = Client(
    "QuranStreamBot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

call_py = PyTgCalls(app)

async def main():
    await app.start()
    await call_py.start()
    
    print("جاري بدء البث المباشر...")
    
    try:
        await call_py.join_group_call(
            CHAT_ID,
            AudioPiped(RADIO_URL)
        )
        print("البث يعمل الآن بنجاح.")
        await asyncio.Event().wait()
    except Exception as e:
        print(f"حدث خطأ أثناء الانضمام أو تشغيل البث: {e}")
    finally:
        await call_py.stop()
        await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
