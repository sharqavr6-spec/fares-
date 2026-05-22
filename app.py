import os
import asyncio
import sys
import traceback
from pyrogram import Client, filters
from pyrogram.types import Message

# --- حل تعارض مكتبة المكالمات ---
import pyrogram.errors
if not hasattr(pyrogram.errors, "GroupcallForbidden"):
    class GroupcallForbidden(Exception): pass
    pyrogram.errors.GroupcallForbidden = GroupcallForbidden

from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream

# جلب الإعدادات من بيئة التشغيل
API_ID = os.environ.get("API_ID", "").strip()
API_HASH = os.environ.get("API_HASH", "").strip()
BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip()
SESSION_STRING = os.environ.get("SESSION_STRING", "").strip()
OWNER_ID = os.environ.get("OWNER_ID", "").strip()

if not all([API_ID, API_HASH, BOT_TOKEN, SESSION_STRING]):
    print("❌ خطأ: هناك متغيرات ناقصة في إعدادات ريلواي!", flush=True)
    sys.exit(1)

API_ID = int(API_ID)
OWNER_ID = int(OWNER_ID) if (OWNER_ID and OWNER_ID.isdigit()) else None

print("⚙️ جاري تشغيل السيرفر بنظام الحقن المباشر للموجه...", flush=True)

# تعريف الكلاينت
bot = Client("tg_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
assistant = Client("tg_account", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)
pytgcalls = PyTgCalls(assistant)

user_states = {}

# 🎯 استخدام الـ Decorator الصريح لضمان التقاط الرسائل رغماً عن أي تعارض
@bot.on_message(filters.text & filters.private)
async def main_bot_router(client: Client, message: Message):
    try:
        text = message.text.strip()
        user_id = message.from_user.id

        print(f"📥 وصل أمر مؤكد للسيرفر من {user_id}: {text}", flush=True)

        # 1️⃣ أمر البدء
        if text.startswith("/start"):
            user_states[user_id] = {"step": "WAITING_FOR_CHANNEL"}
            await message.reply_text(
                "👋 أهلاً بك في نظام تشغيل الإذاعة المستقر والجديد!\n\n"
                "📥 أرسل لي الآن **معرف القناة أو الجروب** (مثال: @MyChannel) أو الآيدي الرقمي للمكان الذي تريد البث فيه:"
            )
            return

        # 2️⃣ أمر الإيقاف
        elif text.startswith("/stop"):
            args = text.split(maxsplit=1)
            if len(args) < 2:
                await message.reply_text("❌ أرسل الأمر هكذا: `/stop يوزر_القناة`")
                return

            channel_input = args[1].strip()
            status_msg = await message.reply_text("⏳ جاري إيقاف البث...")

            try:
                try:
                    chat = await bot.get_chat(channel_input)
                    chat_id = chat.id
                except Exception:
                    chat_id = int(channel_input) if (channel_input.startswith("-100") or channel_input.isdigit()) else channel_input

                await pytgcalls.leave_group_call(chat_id)
                await status_msg.edit_text(f"🛑 تم إيقاف البث بنجاح من: `{channel_input}`")
            except Exception as e:
                await status_msg.edit_text(f"❌ حدث خطأ أثناء الإيقاف: {e}")
            return

        # 3️⃣ تتبع الخطوات المتتالية
        state = user_states.get(user_id)
        if not state:
            return

        step = state.get("step")

        if step == "WAITING_FOR_CHANNEL":
            user_states[user_id] = {"step": "WAITING_FOR_URL", "channel": text}
            await message.reply_text(
                f"✅ تم حفظ القناة: `{text}`\n\n"
                "📻 الآن أرسل **رابط البث المباشر (Stream URL)** للإذاعة لبدء التشغيل:"
            )

        elif step == "WAITING_FOR_URL":
            stream_url = text
            channel_input = state.get("channel")
            user_states.pop(user_id, None)
            
            status_msg = await message.reply_text("⏳ جاري تشغيل البث المباشر للمكالمة...")
            
            try:
                try:
                    chat = await bot.get_chat(channel_input)
                    chat_id = chat.id
                except Exception:
                    chat_id = int(channel_input) if (channel_input.startswith("-100") or channel_input.isdigit()) else channel_input

                await pytgcalls.join_group_call(chat_id, MediaStream(stream_url))
                await status_msg.edit_text(
                    f"📻 **ممتاز! البث يعمل الآن بنجاح وبدون انقطاع!**\n\n"
                    f"📢 القناة: `{channel_input}`\n"
                    f"🛑 لإيقافه في أي وقت أرسل: `/stop {channel_input}`"
                )
            except Exception as e:
                await status_msg.edit_text(f"❌ **فشل التشغيل!**\n\n⚠️ السبب: {e}")

    except Exception:
        traceback.print_exc()


async def start_services():
    print("🚀 جاري تشغيل التطبيقات بالتوازي الحقيقي...", flush=True)
    
    # تشغيل الحسابات
    await bot.start()
    await assistant.start()
    await pytgcalls.start()
    
    print("🌟 تم تشغيل البوت والحساب والمكالمات بنجاح!", flush=True)
    
    if OWNER_ID:
        try:
            await bot.send_message(
                chat_id=OWNER_ID, 
                text="⚡ **تم تحديث النظام بالكامل بنظام الـ Decorator المحقون! جرب الآن إرسال /start مجدداً وسأرد عليك فوراً رغماً عن أي تعارض.**"
            )
        except Exception as e:
            print(f"⚠️ إشعار المالك لم يرسل: {e}", flush=True)

    # تشغيل نظام الاستماع الفيدرالي المستمر للبوت ومنعه من الخمول أو التعارض
    await asyncio.gather(
        asyncio.Event().wait()
    )

if __name__ == "__main__":
    asyncio.run(start_services())
