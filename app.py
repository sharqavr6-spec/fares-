import os
import asyncio
import sys
import traceback
from pyrogram import Client, filters
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

# 1. جلب إعدادات البيئة من Railway
API_ID = os.environ.get("API_ID", "").strip()
API_HASH = os.environ.get("API_HASH", "").strip()
BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip()
SESSION_STRING = os.environ.get("SESSION_STRING", "").strip()
OWNER_ID = os.environ.get("OWNER_ID", "").strip()

if not all([API_ID, API_HASH, BOT_TOKEN, SESSION_STRING]):
    print("❌ خطأ: تأكد من إضافة كافة المتغيرات الأساسية في Railway!", flush=True)
    sys.exit(1)

API_ID = int(API_ID)
if OWNER_ID:
    try:
        OWNER_ID = int(OWNER_ID)
    except ValueError:
        OWNER_ID = None

# 2. تهيئة نظام العميل المزدوج
print("🤖 جاري تهيئة البوت الذكي بنظام المعالج الموحد...", flush=True)
bot = Client("tg_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
assistant = Client("tg_account", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)
pytgcalls = PyTgCalls(assistant)

# قاموس لحفظ خطوات المستخدمين
user_states = {}

# --------------------------------------------------------
# 🎯 المُعالج الموحّد لجميع رسائل الخاص (متاح للجميع)
# --------------------------------------------------------
@bot.on_message(filters.private & filters.text)
async def main_bot_router(client: Client, message: Message):
    try:
        text = message.text.strip()
        user_id = message.from_user.id

        # 1️⃣ أولاً: فحص إذا كان المستخدم أرسل أمر التشغيل /start
        if text.startswith("/start"):
            user_states[user_id] = {"step": "WAITING_FOR_CHANNEL"}
            welcome_text = (
                "👋 أهلاً بك في بوت تشغيل الإذاعة وبث القرآن الكريم المباشر!\n\n"
                "📥 لتشغيل البث في قناتك أو جروبك، من فضلك أرسل لي **يوزر القناة** (مثال: @MyChannel) أو الآيدي الرقمي الثابت لها:\n\n"
                "⚠️ *تأكد أولاً أن الحساب المساعد عضو داخل القناة والمكالمة المرئية/الصوتية مفتوحة هناك.*"
            )
            await message.reply_text(welcome_text)
            return

        # 2️⃣ ثانياً: فحص إذا كان المستخدم أرسل أمر الإيقاف /stop
        elif text.startswith("/stop"):
            args = text.split(maxsplit=1)
            if len(args) < 2:
                await message.reply_text("❌ الصيغة خاطئة! أرسل الأمر هكذا لإيقاف البث:\n`/stop يوزر_أو_آيدي_القناة`")
                return

            channel_input = args[1].strip()
            status_msg = await message.reply_text("⏳ جاري إيقاف البث ومغادرة المكالمة الصخرية...")

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

        # 3️⃣ ثالثاً: التعامل مع نظام الخطوات لتلقي البيانات
        state = user_states.get(user_id)
        if not state:
            # إذا أرسل نص عادي بدون أن يبدأ بـ /start
            await message.reply_text("💡 من فضلك أرسل الأمر `/start` للبدء في ضبط البث خطوة بخطوة.")
            return

        step = state.get("step")

        # الخطوة أ: استلام القناة والطلب التالي (رابط الإذاعة)
        if step == "WAITING_FOR_CHANNEL":
            user_states[user_id] = {
                "step": "WAITING_FOR_URL",
                "channel": text
            }
            await message.reply_text(
                f"✅ تم استقبال معرف القناة: `{text}`\n\n"
                "📻 الآن، من فضلك أرسل **رابط الإذاعة أو البث الصوتي المباشر** (Stream URL) لتشغيله فوراً:"
            )

        # الخطوة ب: استلام الرابط والتشغيل الفعلي في القناة
        elif step == "WAITING_FOR_URL":
            stream_url = text
            channel_input = state.get("channel")
            
            # مسح حالة المستخدم بعد اكتمال البيانات
            user_states.pop(user_id, None)
            
            status_msg = await message.reply_text("⏳ جاري التحقق وتوجيه الحساب المساعد لبدء البث المباشر...")
            
            try:
                try:
                    chat = await bot.get_chat(channel_input)
                    chat_id = chat.id
                except Exception:
                    if channel_input.startswith("-100") or channel_input.isdigit():
                        chat_id = int(channel_input)
                    else:
                        channel_input = channel_input

                if isinstance(chat_id, str) and not chat_id.startswith("@"):
                    chat_id = int(chat_id)

                # تشغيل البث الصوتي
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
        # طباعة أي خطأ غير متوقع في سجلات ريلواي لسهولة المتابعة
        traceback.print_exc()

# --------------------------------------------------------
# 🚀 تشغيل الخدمات وإرسال الإشعار الخاص بك
# --------------------------------------------------------
async def start_services():
    print("🚀 جاري تشغيل البوت والحساب المساعد معاً...", flush=True)
    await bot.start()
    await assistant.start()
    await pytgcalls.start()
    print("🌟 النظام جاهز بالكامل ومستقر الآن!", flush=True)
    
    # رسالة الإشعار الخاصة بك أنت فقط عند إقلاع السيرفر
    if OWNER_ID:
        try:
            await bot.send_message(
                chat_id=OWNER_ID,
                text="🙋‍♂️ **انا جاهز يا باشا!**\n\nالسيرفر اشتغل تمام وبنظام المعالج الموحد السريع. البوت الآن جاهز للرد على كل الناس فوراً بدون أي تجاهل."
            )
            print("🔔 تم إرسال إشعار التشغيل للمالك بنجاح.", flush=True)
        except Exception as e:
            print(f"⚠️ فشل إرسال الإشعار للمالك: {e}", flush=True)
            
    await pyrogram.idle()

if __name__ == "__main__":
    asyncio.run(start_services())
