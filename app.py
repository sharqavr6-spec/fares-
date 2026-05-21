import os
import asyncio
import sys
from pyrogram import Client
from pytgcalls import PyTgCalls, idle
from pytgcalls.types import MediaStream

# جلب الإعدادات من متغيرات البيئة (Environment Variables) لحماية حسابك
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
    print("⏳ جاري بدء تشغيل حساب المساعد...")
    await app.start()
    print("✅ تم تسجيل الدخول بنجاح إلى حساب تيليجرام!")
    
    print("⏳ جاري تشغيل محرك البث الصوتي...")
    await call_py.start()
    print("✅ محرك البث جاهز تماماً!")
    
    try:
        print(f"🎙️ جاري بدء البث المباشر في القناة/المجموعة: {CHAT_ID}")
        print(f"🔗 رابط الإذاعة المستخدم: {RADIO_URL}")
        
        # تشغيل البث المباشر للإذاعة مع تجاهل الفيديو لتقليل الموارد وضمان الاستقرار
        await call_py.play(
            CHAT_ID,
            MediaStream(
                RADIO_URL,
                video_flags=MediaStream.Flags.IGNORE
            )
        )
        print("🎉 البث يعمل الآن بنجاح وبدون انقطاع 24/7!")
        await idle()  # إبقاء السكربت يعمل باستمرار
        
    except Exception as e:
        print(f"❌ حدث خطأ غير متوقع أثناء البث: {e}")
    finally:
        print("👋 جاري إغلاق السكربت...")

if __name__ == "__main__":
    # تشغيل الحلقة البرمجية غير المتزامنة لضمان استقرار الاتصال
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
