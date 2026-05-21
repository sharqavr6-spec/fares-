import os
import asyncio
from pyrogram import Client, idle
from pytgcalls import PyTgCalls
from pyrogram import Client, idle
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream.audio_piped import AudioPiped

# بيانات تيليجرام
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")

# ايدي الجروب أو القناة
CHAT_ID = int(os.environ.get("CHAT_ID"))

# رابط إذاعة القرآن
RADIO_URL = os.environ.get(
    "RADIO_URL",
    "https://stream.quranrad.io/abdulbasit"
)

# تشغيل الحساب المساعد
app = Client(
    "QuranRadio",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

# تشغيل المكالمات الصوتية
call_py = PyTgCalls(app)


async def main():
    # تشغيل الحساب
    await app.start()
    print("✅ تم تسجيل دخول الحساب")

    # تشغيل PyTgCalls
    await call_py.start()
    print("✅ تم تشغيل المكالمة الصوتية")

    # دخول الكول وتشغيل الصوت فقط
    await call_py.join_group_call(
        CHAT_ID,
        AudioPiped(RADIO_URL)
    )

    print("🎙️ إذاعة القرآن الكريم تعمل الآن")

    # إبقاء البوت شغال
    await idle()


asyncio.run(main())
