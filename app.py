import os
import asyncio
import ntplib  
from pyrogram import Client
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped

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
        except Exception as e:
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
# 3. تهيئة وتجهيز العميل ومحرك الصوت الحديث
# ----------------------------------------
if SESSION_STRING:
    app = Client("tg_account", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)
else:
    app = Client("tg_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# الطريقة الحديثة والمستقرة لاستدعاء المحرك
pytgcalls = PyTgCalls(app)

# ----------------------------------------
# 4. دالة التشغيل الرئيسية والتحكم في البث
# ----------------------------------------
async def main():
    print("🚀 جاري تشغيل عميل تليجرام...")
    await app.start()
    
    print("🎵 جاري تشغيل محرك PyTgCalls...")
    await pytgcalls.start()
    
    try:
        print(f"📞 جاري الانضمام والبث المباشر في المجموعة: {CHAT_ID}...")
        # في النظام الحديث بنعمل انضمام وتشغيل للبث في نفس السطر بشكل مباشر ومستقر
        await pytgcalls.join_group_call(
            CHAT_ID,
            AudioPiped(STREAM_URL)
        )
        print(f"▶️ بدأ البث الصوتي بنجاح الآن!")
        
        # إبقاء البوت يعمل بشكل مستمر دون توقف
        await asyncio.Event().wait()
        
    except Exception as e:
        print(f"❌ حدث خطأ أثناء تشغيل البث أو الانضمام: {e}")
    finally:
        print("🛑 جاري إيقاف التشغيل وإغلاق الجلسات...")
        try:
            await pytgcalls.stop()
            await app.stop()
        except Exception:
            pass

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("👋 تم إيقاف البوت يدوياً.")
