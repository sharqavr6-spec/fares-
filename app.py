import os
import asyncio
from pyrogram import Client, idle
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped

# جلب الإعدادات من متغياتالبيئة (Environment Variables) لحماية حسابك
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")
CHAT_ID = os.environ.get("CHAT_ID")
# رابط إذاعة القرآن الكريم (افتراضياً إذاعة الترتيل، ويمكن تغييره من إعدادات رايلي)
RADIO_URL = os.environ.get("RADIO_URL", "https://backup.qurango.net/radio/tarteel")

# التحقق من وجود المتغيرات الأساسية لمنع انهيار السكربت
if not all([API_ID, API_HASH, SESSION_STRING, CHAT_ID]):
    print("❌ خطأ: لم يتم العثور على جميع متغيرات البيئة المطلوبة!")
    print("تأكد من إضافة: API_ID, API_HASH, SESSION_STRING, CHAT_ID في منصة Railway.")
    sys.exit(1)

try:
    API_ID = int(API_ID)
    CHAT_ID = int(CHAT_ID)
except ValueError:
    print("❌ خطأ: يجب أن تكون قيم API_ID و CHAT_ID أرقاماً صالحة!")
    sys.exit(1)

# تهيئة حساب المساعد عبر Pyrogram
app = Client(
    "QuranStreamBot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

# تهيئة حزمة البث الصوتي
call_py = PyTgCalls(app)
async def main():
    await app.start()
    print("✅ الحساب المساعد سجل دخول بنجاح!")

    call_py = PyTgCalls(app)

    try:
        try:
            chat_id = int(CHAT_ID)
        except ValueError:
            chat_id = CHAT_ID

        await call_py.start()

        await call_py.join_group_call(
            chat_id,
            AudioPiped(RADIO_URL)
        )

        print("🎙️ البث المباشر شغال")

    except Exception as e:
        print(f"❌ حدث خطأ: {e}")

    await idle()

asyncio.run(main())
