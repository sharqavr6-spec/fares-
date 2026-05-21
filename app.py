import os
import asyncio
import sys
from pyrogram import Client
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
    print("⏳ ...جاري بدء تشغيل حساب المساعد")
    await app.start()
    print("✅ تسجيل الدخول بنجاح إلى حساب تيليجرام")

    print("⏳ جاري تشغيل محرك البث الصوتي...")

    try:

        # التأكد من تحويل الـ ID لرقم لو كان أرقام عشان المكتبة تقبله
            try:
            chat_id = int(CHAT_ID)
        except ValueError:
            chat_id = CHAT_ID

        # 👇 السطرين دول لازم يتزقوا لجوه كده عشان يبقوا تحت الـ try الكبيرة
        print("🎙️ ..جاري بدء البث المباشر في القناة/المجموعة")
        print(f"🔗 رابط الإذاعة المستخدم: {RADIO_URL}")

        await call_py.start(
            chat_id,
            MediaStream(
                RADIO_URL,
                video_flags=MediaStream.Flags.IGNORE,
            )
        )

        print("🎉 البث يعمل الآن بنجاح وبدون انقطاع 24/7")
        await idle()

