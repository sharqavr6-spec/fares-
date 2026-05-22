import os
import time
import ntplib
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped

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
    
    print("🚨 فشل جميع محاولات مزامنة الوقت عبر NTP.")
    return False

sync_time_via_ntp()

api_id = os.environ.get("API_ID")
api_hash = os.environ.get("API_HASH")
radio_url = os.environ.get("RADIO_URL")
session_string = os.environ.get("SESSION")
chat_username = os.environ.get("CHAT_ID")

app = Client("my_account", api_id=int(api_id), api_hash=api_hash, session_string=session_string)
call = PyTgCalls(app)

@app.on_message(filters.command("start_stream") & filters.me)
async def start_stream(client, message):
    try:
        await call.join_group_call(
            chat_username,
            AudioPiped(radio_url)
        )
        await message.reply_text("✅ تم بدء بث الراديو بنجاح.")
    except Exception as e:
        await message.reply_text(f"❌ فشل بدء البث: {e}")

@app.on_message(filters.command("stop_stream") & filters.me)
async def stop_stream(client, message):
    try:
        await call.leave_group_call(chat_username)
        await message.reply_text("⏹️ تم إيقاف بث الراديو.")
    except Exception as e:
        await message.reply_text(f"❌ فشل إيقاف البث: {e}")

@app.on_message(filters.command("pause_stream") & filters.me)
async def pause_stream(client, message):
    try:
        await call.pause_stream(chat_username)
        await message.reply_text("⏸️ تم إيقاف البث مؤقتاً.")
    except Exception as e:
        await message.reply_text(f"❌ فشل الإيقاف المؤقت: {e}")

@app.on_message(filters.command("resume_stream") & filters.me)
async def resume_stream(client, message):
    try:
        await call.resume_stream(chat_username)
        await message.reply_text("▶️ تم استئناف البث.")
    except Exception as e:
        await message.reply_text(f"❌ فشل استئناف البث: {e}")

@app.on_message(filters.command("change_radio_url") & filters.me)
async def change_radio_url(client, message):
    global radio_url
    if len(message.command) > 1:
        radio_url = message.command[1]
        await message.reply_text(f"تم تحديث الرابط إلى: {radio_url}")
        if call.is_connected:
            await start_stream(client, message)
    else:
        await message.reply_text("يرجى إرسال الرابط الجديد.")

with app:
    app.run()
