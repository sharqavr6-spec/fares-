import os
import asyncio
import sys
import ntplib  # ✅ تم إصلاح الخطأ: إضافة المكتبة الناقصة لمزامنة الوقت
from pyrogram import Client
from pytgcalls.group_call_factory import GroupCallFactory
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
            ntp_time = response.tx_time
            offset = response.offset
            print(f"✅ تم الاتصال بنجاح بـ {server}. الفارق المكتشف: {offset} ثانية.")
            
            try:
                import ctypes
                CLOCK_REALTIME = 0
                class timespec(ctypes.Structure):
                    _fields_ = [("tv_sec", ctypes.c_long), ("tv_nsec", ctypes.c_long)]
                ts = timespec(int(ntp_time), int((ntp_time - int(ntp_time)) * 1e9))
                libc = ctypes.CDLL('libc.so.6')
                libc.clock_settime(CLOCK_REALTIME, ctypes.byref(ts))
                print("🎯 تم إعادة ضبط ساعة النظام الداخلية بنجاح!")
            except Exception:
                print("⚠️ لا توجد صلاحيات Root لتغيير ساعة النظام مباشرة، سيتم استخدام التوقيت الافتراضي المحدث برمجياً.")
            
            return True
        except Exception as e:
            print(f"❌ فشل الاتصال بالسيرفر {server}: {e}")
            continue
    return False

# تشغيل مزامنة الوقت قبل بدء البوت لتفادي مشاكل الـ Session Expired
sync_time_via_ntp()

# ----------------------------------------
# 2. جلب إعدادات البيئة (Environment Variables)
# ----------------------------------------
API_ID = int(os.environ.get("API_ID", 123456))          # استبدله بـ API ID الخاص بك
API_HASH = os.environ.get("API_HASH", "your_api_hash")  # استبدله بـ API HASH الخاص بك

# إذا كنت تستخدم حساب شخصي (وهو الأفضل للمكالمات الصوتية) استخدم كود الجلسة (String Session)
SESSION_STRING = os.environ.get("SESSION_STRING", None)
BOT_TOKEN = os.environ.get("BOT_TOKEN", None)            # إذا كنت تستخدم بوت عادي بدلاً من الحساب

# معرف الدردشة (الجروب أو القناة) ورابط البث الصوتي
CHAT_ID = int(os.environ.get("CHAT_ID", -100123456789)) 
STREAM_URL = os.environ.get("STREAM_URL", "http://stream.zeno.fm/f97vpt67v0uuv") # كمثال لرابط راديو أو ملف صوتي

# ----------------------------------------
# 3. تهيئة وتجهيز العميل ومصنع الاتصال
# ----------------------------------------
if SESSION_STRING:
    app = Client("tg_account", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)
else:
    app = Client("tg_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# إنشاء كائن المكالمة من خلال الفاكتوري المتوافق مع إصدارك
group_call_factory = GroupCallFactory(app)
group_call = group_call_factory.get_group_call()

# ----------------------------------------
# 4. دالة التشغيل الرئيسية والتحكم في البث
# ----------------------------------------
async def main():
    print("🚀 جاري تشغيل عميل تليجرام...")
    await app.start()
    
    print("🎵 جاري تشغيل محرك PyTgCalls...")
    await group_call.start()
    
    try:
        print(f"📞 جاري الانضمام إلى المكالمة الصوتية في المجموعه: {CHAT_ID}...")
        await group_call.join(CHAT_ID)
        
        # تجهيز رابط البث الصوتي وتمريره للمكالمة
        audio_stream = AudioPiped(STREAM_URL)
        await group_call.change_stream(audio_stream)
        print(f"▶️ بدأ البث الصوتي بنجاح الآن!")
        
        # إبقاء البوت يعمل بشكل مستمر دون توقف
        await asyncio.Event().wait()
        
    except Exception as e:
        print(f"❌ حدث خطأ أثناء تشغيل البث أو الانضمام: {e}")
    finally:
        # إغلاق آمن للاتصالات في حال توقف السكريبت
        print("🛑 جاري إيقاف التشغيل وإغلاق الجلسات...")
        try:
            await group_call.stop()
            await app.stop()
        except Exception:
            pass

if __name__ == "__main__":
    # تشغيل حلقة asyncio لتشغيل البوت بالكامل
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("👋 تم إيقاف البوت يدوياً.")
