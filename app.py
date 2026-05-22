import os
import asyncio
import sys
import traceback
from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message

# --------------------------------------------------------
# 🛠️ حل تعارض مكتبة المكالمات مع تحديثات بايروجرام
# --------------------------------------------------------
import pyrogram.errors
if not hasattr(pyrogram.errors, "GroupcallForbidden"):
    class GroupcallForbidden(Exception):
        pass
    pyrogram.errors.GroupcallForbidden = GroupcallForbidden
# --------------------------------------------------------

from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream

# جلب الإعدادات من بيئة تشغيل Railway
API_ID = os.environ.get("API_ID", "").strip()
API_HASH = os.environ.get("API_HASH", "").strip()
BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip()
SESSION_STRING = os.environ.get("SESSION_STRING", "").strip()
OWNER_ID = os.environ.get("OWNER_ID", "").strip()

if not all([API_ID, API_HASH, BOT_TOKEN, SESSION_STRING]):
    print("❌ خطأ: هناك متغيرات ناقصة في إعدادات Railway!", flush=True)
    sys.exit(1)

API_ID = int(API_ID)
OWNER_ID = int(OWNER_ID) if (OWNER_ID and OWNER_ID.isdigit()) else None

print("🤖 جاري بدء تشغيل النظام المستقر...", flush=True)
bot = Client("tg_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
assistant = Client("tg_account", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)
pytgcalls = PyTgCalls(assistant)

user_states = {}

# 🎯 الموجه الرئيسي المستقر لاستقبال الرسائل
async def main_bot_router(client: Client, message: Message):
    try:
        if not message.text or not message.from_user:
            return

        text = message.text.strip()
        user_id = message.from_user.id

        print(f"📥 استقبلت أمر من {user_id}: {text}", flush=True)

        # 1️⃣ أمر التشغيل الترحيبي
        if text.startswith("/start"):
            user_states[user_id] = {"step": "WAITING_FOR_CHANNEL"}
            welcome_text = (
                "👋 أهلاً بك في بوت تشغيل الإذاعة وبث القرآن الكريم المباشر!\n\n"
                "📥 لتشغيل البث، أرسل لي الآن **يوزر القناة** (مثال: @MyChannel) أو الآيدي الرقمي لها:\n\n"
                "⚠️ *تأكد أن الحساب المساعد عضو داخل القناة والمكالمة الصوتية مفتوحة هناك.*"
            )
            await message.reply_text(welcome_text)
            return

        # 2️⃣ أمر إيقاف البث
        elif text.startswith("/stop"):
            args = text.split(maxsplit=1)
            if len(args) < 2:
                await message.reply_text("❌ الصيغة خاطئة! أرسل الأمر هكذا: `/stop يوزر_القناة`")
                return

            channel_input = args[1].strip()
            status_msg = await message.reply_text("⏳ جاري إيقاف البث المباشر...")

            try:
                try:
                    chat = await bot.get_chat(channel_input)
                    chat_id = chat.id
                except Exception:
                    chat_id = int(channel_input) if (channel_input.startswith("-100") or channel_input.isdigit()) else channel_input

                if isinstance(chat_id, str) and not chat_id.startswith("@"):
                    chat_id = int(chat_id)

                await pytgcalls.leave_group_call(chat_id)
                await status_msg.edit_text(f"🛑 تم إيقاف البث ومغادرة المكالمة بنجاح من القناة: `{channel_input}`")
            except Exception as e:
                await status_msg.edit_text(f"❌ حدث خطأ أثناء محاولة الإيقاف: {e}")
            return

        # 3️⃣ معالجة الخطوات المتتالية للتشغيل
        state = user_states.get(user_id)
        if not state:
            return

        step = state.get("step")

        if step == "WAITING_FOR_CHANNEL":
            user_states[user_id] = {"step": "WAITING_FOR_URL", "channel": text}
            await message.reply_text(
                f"✅ تم حفظ القناة: `{text}`\n\n"
                "📻 الآن، أرسل **رابط الإذاعة المباشر** (Stream URL) لبدء البث فوراً:"
            )

        elif step == "WAITING_FOR_URL":
            stream_url = text
            channel_input = state.get("channel")
            user_states.pop(user_id, None)
            
            status_msg = await message.reply_text("⏳ جاري ربط الحساب المساعد بالمكالمة وبدء البث...")
            
            try:
                try:
                    chat = await bot.get_chat(channel_input)
                    chat_id = chat.id
                except Exception:
                    chat_id = int(channel_input) if (channel_input.startswith("-100") or channel_input.isdigit()) else channel_input

                if isinstance(chat_id, str) and not chat_id.startswith("@"):
                    chat_id = int(chat_id)

                await pytgcalls.join_group_call(chat_id, MediaStream(stream_url))
                await status_msg.edit_text(
                    f"📻 **ممتاز! بدأ البث الصوتي بنجاح الآن!**\n\n"
                    f"📢 القناة: `{channel_input}`\n"
                    f"💡 لإيقاف البث في أي وقت، أرسل: `/stop {channel_input}`"
                )
            except Exception as e:
                await status_msg.edit_text(f"❌ **فشل بدء البث!**\n\n⚠️ السبب: {e}")

    except Exception:
        traceback.print_exc()

# تسجيل المعالج تلقائياً في البوت
bot.add_handler(MessageHandler(main_bot_router, filters=filters.text))

# دالة التشغيل المتزامنة
async def start_services():
    print("🚀 جاري ربط الحسابات وتشغيل السيرفر الموحد...", flush=True)
    await bot.start()
    await assistant.start()
    await pytgcalls.start()
    print("🌟 النظام يعمل الآن واستقبال الرسائل نشط بالكامل!", flush=True)
    
    if OWNER_ID:
        try:
            await bot.send_message(chat_id=OWNER_ID, text="⚡ **البوت جاهز تماماً الآن ومستقر برمجياً! جرب إرسال /start وسيتم الرد فوراً.**")
        except Exception as e:
            print(f"⚠️ لم يتم إرسال إشعار للمالك: {e}", flush=True)
            
    # إبقاء السيرفر حياً ومستقراً لاستقبال الأحداث بدون انقطاع
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(start_services())
