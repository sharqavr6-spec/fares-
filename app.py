import os
import asyncio
import os
from pyrogram import Client, idle
from pytgcalls.group_call_factory import GroupCallFactory

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
call_py = GroupCallFactory(app).get_group_call()
async def main():
    await app.start()
    print("✅ الحساب المساعد سجل دخول بنجاح!")
    
    call_py = GroupCallFactory(app).get_group_call()
    
    try:
        try:
            chat_id = int(CHAT_ID)
        except ValueError:
            chat_id = CHAT_ID

            # ... الكود اللي فوق زي ما هو
    print("🎙️ البث المباشر في القناة/المجموعة..")
    print(f"🔗 رابط الإذاعة المستخدم {RADIO_URL}")
    
    # التعديل الصح للمسافات:
    call_py.input_filename = RADIO_URL
    await app.get_chat(chat_id)
    
    await call_py.start(
        chat_id,
        AudioPiped(RADIO_URL)
    )
    
    print("🎉 24/7 البث يعمل الآن بنجاح وبدون انقطاع")
    await idle()
    
except Exception as e:
    print(f"❌ حدث خطأ أثناء تشغيل البث: {e}")

app.run(main())
