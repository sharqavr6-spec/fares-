import os
import asyncio

# --------------------------------------------------------
# 🛠️ خُدعة برمجية لحل تعارض الإصدارات وحقن الكلاس المفقود
# --------------------------------------------------------
import pyrogram.errors
if not hasattr(pyrogram.errors, "GroupcallForbidden"):
    class GroupcallForbidden(Exception):
        pass
    pyrogram.errors.GroupcallForbidden = GroupcallForbidden
# --------------------------------------------------------

from pyrogram import Client
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream

# 1. جلب إعدادات البيئة (Variables)
API_ID = int(os.environ.get("API_ID", 123456))          
API_HASH = os.environ.get("API_HASH", "your_api_hash")  
SESSION_STRING = os.environ.get("SESSION_STRING", None)
BOT_TOKEN = os.environ.get("BOT_TOKEN", None)            
CHAT_ID = int(os.environ.get("CHAT_ID", -100123456789)) 
STREAM_URL = os.environ.get("STREAM_URL", "http://stream.zeno.fm/f97vpt67v0uuv") 

# 2. تهيئة عميل تليجرام (Pyrogram)
if SESSION_STRING:
    app = Client("tg_account", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)
else:
    app = Client("tg_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# 3. تهيئة محرك الصوت الجديد (PyTgCalls)
pytgcalls = PyTgCalls(app)

# 4. الدالة الرئيسية للتشغيل والبث
async def main():
    print("🚀 جاري تشغيل عميل تليجرام ومحرك الصوت الحديِث...")
    await app.start()
    await pytgcalls.start()
    
    try:
        print(f"📞 جاري الانضمام للمكالمة وبدء البث في المجموعة: {CHAT_ID}...")
        
        await pytgcalls.join_group_call(
            CHAT_ID,
            MediaStream(STREAM_URL)
        )
        
        print(f"✅ بدأ البث الصوتي بنجاح وبدون أي مشاكل!")
        await asyncio.Event().wait()
            
    except Exception as e:
        print(f"❌ حدث خطأ أثناء تشغيل البث: {e}")
    finally:
        print("🛑 جاري إيقاف التشغيل وإغلاق الجلسات النظيفة...")
        try:
            await pytgcalls.leave_group_call(CHAT_ID)
        except Exception:
            pass
        try:
            await app.stop()
        except Exception:
            pass

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("👋 تم إيقاف البوت يدوياً.")
