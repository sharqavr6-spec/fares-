import os
import asyncio
import sys
from pyrogram import Client
from pytgcalls.pytgcalls import PyTgCalls
 

# المتغيرات الثابتة مباشرة بدلاً من os.environ.get
API_ID = 24941393
API_HASH = "fb8473813ae24db4da4c3723afa377c6"
SESSION_STRING = "BAId-rwATeCKfSw6YePztKzAMaUUSOpeFF-ODVzlht06wUbqXVE6gfuh6AHBY3vnfRgiQ4HBoZkf3HJjFmpbTls07S1QVEFv8T_IkdkwM0ppa-HOjlFZQ7dei6-CvKhSZd0qGQbPN6jW6Tuwy9kE_QH21MPa4FPrDJulTgpW2YUXt48xVaXg7mkInNhW05a4GMrt3benXfuxIrUxHQKfG5G8q0_InIyZdBUXse_VKnNn-caAW7dumnzOnHj_jEDVnx17b_oLtk7HUd2SFCfF050CxmQ463FAIS5qeIcYFBZG3QZAY8uYV05wxMJQKYFIbCj3-K_DWAX6FGIiSNspqrr11TZW9QAAAAIGJJ1TAA"
CHAT_ID = -1001888647282
RADIO_URL = "https://backup.qurango.net/radio/tarteel"

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
