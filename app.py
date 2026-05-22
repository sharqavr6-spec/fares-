import os
import asyncio
import ntplib  
from pyrogram import Client
from pytgcalls import GroupCallFactory

# ----------------------------------------
# 1. دالة مزامنة وقت السيرفر
# ----------------------------------------
def sync_time_via_ntp():
    print("⏳ جاري محاولة مزامنة الوقت مع خوادم NTP...")
    ntp_servers = ['pool.ntp.org', 'time.google.com', 'time.windows.com']
    client = ntplib.NTPClient()
    for server in ntp_servers:
        try:
            response = client.request(server, version=3, timeout=5)
            print(f"✅ تم الاتصال بنجاح بـ {server}.")
            return True
        except Exception:
            continue
    return False

sync_time_via_ntp()

# ----------------------------------------
# 2. جلب إعدادات البيئة
# ----------------------------------------
API_ID = int(os.environ.get("API_ID", 123456))          
API_HASH = os.environ.get("API_HASH", "your_api_hash")  
SESSION_STRING = os.environ.get("SESSION_STRING", None)
BOT_TOKEN = os.environ.get("BOT_TOKEN", None)            
CHAT_ID = int(os.environ.get("CHAT_ID", -100123456789)) 
STREAM_URL = os.environ.get("STREAM_URL", "http://stream.zeno.fm/f97vpt67v0uuv") 

# ----------------------------------------
# 3. تهيئة العميل ومحرك الصوت لنسخة dev24 القديمة
# ----------------------------------------
if SESSION_STRING:
    app = Client("tg_account", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)
else:
    app = Client("tg_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# طريقة استدعاء المحرك الخاصة بنسخة 3.0.0.dev24
group_call_factory = GroupCallFactory(app)
group_call = group_call_factory.get_group_call()

# ----------------------------------------
# 4. دالة التشغيل الرئيسية والتحكم في البث
# ----------------------------------------
async def main():
    print("🚀 جاري تشغيل عميل تليجرام...")
    await app.start()
    
    try:
        print(f"📞 جاري الانضمام للمجموعة: {CHAT_ID}...")
        await group_call.join(CHAT_ID)
        
        print(f"🎵 جاري بدء البث الصوتي من الرابط مباشرة...")
        # في نسخة dev24 نمرر رابط البث المباشر داخل دالة start_audio فوراً
        await group_call.start_audio(STREAM_URL)
        print(f"✅ بدأ البث الصوتي بنجاح الآن!")
        
        # إبقاء السكريبت يعمل بشكل مستمر دون توقف
        while True:
            await asyncio.sleep(60)
            
    except Exception as e:
        print(f"❌ حدث خطأ أثناء تشغيل البث أو الانضمام: {e}")
    finally:
        print("🛑 جاري إيقاف التشغيل وإغلاق الجلسات...")
        try:
            await group_call.stop()
            await app.stop()
        except Exception:
            pass

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("👋 تم إيقاف البوت يدوياً.")
