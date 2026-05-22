import os
import asyncio
import sys
import traceback
from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message

# --------------------------------------------------------
# 🛠️ خُدعة برمجية لحل تعارض المكتبات وضمان الاستقرار
# --------------------------------------------------------
import pyrogram.errors
if not hasattr(pyrogram.errors, "GroupcallForbidden"):
    class GroupcallForbidden(Exception):
        pass
    pyrogram.errors.GroupcallForbidden = GroupcallForbidden
# --------------------------------------------------------

from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream

# جلب إعدادات البيئة من Railway
API_ID = os.environ.get("API_ID", "").strip()
API_HASH = os.environ.get("API_HASH", "").strip()
BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip()
SESSION_STRING = os.environ.get("SESSION_STRING", "").strip()
OWNER_ID = os.environ.get("OWNER_ID", "").strip()

if not all([API_ID, API_HASH, BOT_TOKEN, SESSION_STRING]):
    print("❌ خطأ: تأكد من إضافة كافة المتغيرات الأساسية في Railway!", flush=True)
    sys.exit(1)

API_ID = int(API_ID)
OWNER_ID = int(OWNER_ID) if (OWNER_ID and OWNER_ID.isdigit()) else None

print("🤖 جاري تهيئة البوت والحساب المساعد بالنظام المطور الجديد...", flush=True)
bot = Client("tg_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
assistant = Client("tg_account", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)
pytgcalls = PyTgCalls(assistant)

user_states = {}

# 🎯 الموجه الرئيسي لجميع الرسائل النصية القادمة للبوت
async def main_bot_router(client: Client, message: Message):
    try:
        # طباعة فورية إجبارية في اللوجات لمعرفة إذا كانت الرسالة تصل السيرفر أم لا
        print(f"📥 [تحديث جديد] استقبلت رسالة نصية من: {message.from_user.id if message.from_user else 'مجهول'} | النص: {message.text}", flush=True)

        if not message.text or not message.from_user:
            return

        text = message.text.strip()
        user_id = message.from_user.id

        # 1️⃣ فحص أمر التشغيل /start
        if text.startswith("/start"):
            user_states[user_id] = {"step": "WAITING_FOR_CHANNEL"}
            welcome_text = (
                "👋 أهلاً بك في بوت تشغيل الإذاعة وبث القرآن الكريم المباشر!\n\n"
                "📥 لتشغيل البث في قناتك أو جروبك، من فضلك أرسل لي **يوزر القناة** (مثال: @MyChannel) أو الآيدي الرقمي الثابت لها:\n\n"
                "⚠️ *تأكد أولاً أن الحساب المساعد عضو داخل القناة والمكالمة الصوتية مفتوحة هناك.*"
            )
            await message.reply_text(welcome_text)
            print(f"✅ تم الرد بنجاح على أمر /start للمستخدم {user_id}", flush=True)
            return

        # 2️⃣ فحص أمر الإيقاف /stop
        elif text.startswith("/stop"):
            args = text.split(maxsplit=1)
            if len(args) < 2:
                await message.reply_text("❌ الصيغة خاطئة! أرسل الأمر هكذا لإيقاف البث:\n`/stop يوزر_أو_آيدي_القناة`")
                return

            channel_input = args[1].strip()
            status_msg = await message.reply_text("⏳ جاري إيقاف البث ومغادرة المكالمة...")

            try:
                try:
                    chat = await bot.get_chat(channel_input)
                    chat_id = chat.id
                except Exception:
                    chat_id = int(channel_input) if (channel_input.startswith("-100") or channel_input.isdigit()) else channel_input

                if isinstance(chat_id, str) and not chat_id.startswith("@"):
                    chat_id = int(chat_id)

                await pytgcalls.leave_group_call(chat_id)
                await status_msg.edit_text(f"🛑 تم إيقاف البث بنجاح ومغادرة المكالمة من: `{channel_input}`")
            except Exception as e:
                await status_msg.edit_text(f"❌ حدث خطأ أثناء محاولة الإيقاف: {e}")
            return

        # 3️⃣ التعامل مع نظام الخطوات وتلقي البيانات
        state = user_states.get(user_id)
        if not state:
            if not text.startswith("/"):
                await message.reply_text("💡 من فضلك أرسل الأمر `/start` للبدء في ضبط البث خطوة بخطوة.")
            return

        step = state.get("step")

        if step == "WAITING_FOR_CHANNEL":
            user_states[user_id] = {
                "step": "WAITING_FOR_URL",
                "channel": text
            }
            await message.reply_text(
                f"✅ تم استقبال معرف القناة: `{text}`\n\n"
                "📻 الآن، من فضلك أرسل **رابط الإذاعة أو البث الصوتي المباشر** (Stream URL) لتشغيله فوراً:"
            )

        elif step == "WAITING_FOR_URL":
            stream_url = text
            channel_input = state.get("channel")
            user_states.pop(user_id, None)
            
            status_msg = await message.reply_text("⏳ جاري التحقق وتوجيه الحساب المساعد لبدء البث المباشر...")
            
            try:
                try:
                    chat = await bot.get_chat(channel_input)
                    chat_id = chat.id
                except Exception:
                    chat_id = int(channel_input) if (channel_input.startswith("-100") or channel_input.isdigit()) else channel_input

                if isinstance(chat_id, str) and not chat_id.startswith("@"):
                    chat_id = int(chat_id)

                await pytgcalls.join_group_call(
                    chat_id,
                    MediaStream(stream_url)
                )
                
                await status_msg.edit_text(
                    f"🥳 **ممتاز! بدأ البث الصوتي بنجاح الآن!**\n\n"
                    f"📢 القناة/الجروب: `{channel_input}`\n"
                    f"📻 الرابط المشغل: {stream_url}\n\n"
                    f"💡 لإيقاف البث في أي وقت، أرسل لي: `/stop {channel_input}`"
                )
                
            except Exception as e:
                await status_msg.edit_text(
                    f"❌ **فشل بدء البث!**\n\n"
                    f"⚠️ **السبب:** {e}\n\n"
                    f"💡 **تأكد من:**\n"
                    f"1. فتح المكالمة الصوتية في قناتك يدوياً أولاً.\n"
                    f"2. انضمام الحساب المساعد داخل القناة وترقيته كمشرف."
                )

    except Exception:
        traceback.print_exc()

# 🎯 تسجيل الموجه بشكل صريح ومباشر في النظام
bot.add_handler(MessageHandler(main_bot_router, filters=filters.text))

# 🚀 تشغيل الخدمات بالتوازي وبشكل متزامن كامل
async def start_services():
    print("🚀 جاري تشغيل خدمات البوت والحساب المساعد...", flush=True)
    await bot.start()
    await assistant.start()
    
    # 🔥 [الحل الحاسم] تنظيف أي وب هوك معلق قديم وتصفير التحديثات لضمان التجاوب الفوري للـ Polling
    print("🧹 جاري تنظيف الـ Webhook وأي تراكمات قديمة لفرض الاستجابة...", flush=True)
    await bot.delete_webhook(drop_pending_updates=True)
    
    await pytgcalls.start()
    print("🌟 النظام جاهز بالكامل بنسبة 100% الآن!", flush=True)
    
    if OWNER_ID:
        try:
            await bot.send_message(
                chat_id=OWNER_ID,
                text="⚡ **تم إعادة التشغيل بنظام التنظيف الشامل!**\n\nقم بإرسال `/start` الآن وسيتم الرد عليك فوراً وبدون أي تجاهل برميجي."
            )
        except Exception as e:
            print(f"⚠️ فشل إرسال إشعار التشغيل للمالك: {e}", flush=True)
            
    # حلقة انتظار لانهائية مستقرة تماماً بديلة لـ idle لمنع أي تجمد في ريلواي
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(start_services())
