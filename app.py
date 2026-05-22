import os
import asyncio
import sys
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

if not all([API_ID, API_HASH, BOT_TOKEN, SESSION_STRING]):
    print("❌ خطأ: تأكد من إضافة (API_ID, API_HASH, BOT_TOKEN, SESSION_STRING) في Railway!", flush=True)
    sys.exit(1)

API_ID = int(API_ID)

# 2. إنشاء العميلين (البوت الموجه والحساب المساعد للبث)
print("🤖 جاري تهيئة نظام العميل المزدوج التفاعلي...", flush=True)
bot = Client("tg_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
assistant = Client("tg_account", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

# ربط محرك الصوت بالحساب المساعد
pytgcalls = PyTgCalls(assistant)

# قاموس لحفظ خطوات المستخدمين (لوحة تحكم مؤقتة في الذاكرة)
user_states = {}

# --- [ 1. أمر البداية /start ] ---
@bot.on_message(filters.command("start") & filters.private)
async def start_cmd(client: Client, message: Message):
    user_id = message.from_user.id
    # حفظ حالة المستخدم الحالية: منتظرين يوزر القناة
    user_states[user_id] = {"step": "WAITING_FOR_CHANNEL"}
    
    welcome_text = (
        "👋 أهلاً بك في بوت تشغيل الإذاعة المباشرة!\n\n"
        "📥 لتشغيل الإذاعة، من فضلك أرسل **يوزر القناة** أو الجروب الذي تريد تشغيل البث فيه (مثال: @MyChannel) أو الآيدي الخاص بها:"
    )
    await message.reply_text(welcome_text)

# --- [ 2. استقبال البيانات خطوة بخطوة ] ---
@bot.on_message(filters.text & filters.private & ~filters.command(["start", "stop"]))
async def handle_steps(client: Client, message: Message):
    user_id = message.from_user.id
    state = user_states.get(user_id)

    # إذا كان المستخدم يرسل نصاً عشوائياً دون بدء المحادثة بـ /start
    if not state:
        await message.reply_text("💡 من فضلك أرسل الأمر `/start` للبدء في ضبط البث خطوة بخطوة.")
        return

    step = state.get("step")

    # الخطوة الأولى: استلمنا اليوزر أو الآيدي
    if step == "WAITING_FOR_CHANNEL":
        channel_input = message.text.strip()
        
        # الانتقال للخطوة التالية وحفظ القناة مؤقتاً
        user_states[user_id] = {
            "step": "WAITING_FOR_URL",
            "channel": channel_input
        }
        
        await message.reply_text(
            f"✅ تم استقبال القناة: `{channel_input}`\n\n"
            "📻 الآن، من فضلك أرسل **رابط الإذاعة** (Stream URL) الذي تريدني أن أبثه فوراً:"
        )

    # الخطوة الثانية: استلمنا الرابط وبداية التشغيل الفعلي
    elif step == "WAITING_FOR_URL":
        stream_url = message.text.strip()
        channel_input = state.get("channel")
        
        # مسح حالة المستخدم لتهيئة البوت لاستقبال طلبات جديدة
        user_states.pop(user_id, None)
        
        status_msg = await message.reply_text("⏳ جاري التحقق من القناة وتوجيه الحساب المساعد لبدء البث...")
        
        try:
            # محاولة التعرف على آيدي الرقمي للقناة سواء كانت يوزر أو آيدي ثابت
            try:
                chat = await bot.get_chat(channel_input)
                chat_id = chat.id
            except Exception:
                # إذا فشل البوت (مثلاً لو لم يكن مشرفاً بعد)، نحاول تحويل النص لرقم مباشرة لو كان آيدي
                if channel_input.startswith("-100") or channel_input.isdigit():
                    chat_id = int(channel_input)
                else:
                    chat_id = channel_input

            # إذا كان الآيدي لا يزال نصاً، نتأكد من الصيغة
            if isinstance(chat_id, str) and not chat_id.startswith("@"):
                chat_id = int(chat_id)

            # استدعاء الحساب المساعد ليدخل المكالمة ويبث الرابط
            await pytgcalls.join_group_call(
                chat_id,
                MediaStream(stream_url)
            )
            
            await status_msg.edit_text(
                f"🥳 **ممتاز! بدأ البث الصوتي بنجاح الآن!**\n\n"
                f"📢 القناة: `{channel_input}`\n"
                f"📻 الرابط والمصدر: {stream_url}\n\n"
                f"💡 لإيقاف البث في أي وقت، أرسل: `/stop` متبوعاً بمعرف القناة."
            )
            
        except Exception as e:
            await status_msg.edit_text(
                f"❌ **فشل بدء البث!**\n\n"
                f"⚠️ **السبب:** {e}\n\n"
                f"💡 **تأكد من الآتي:**\n"
                f"1. المكالمة الصوتية/المرئية مفتوحة حالياً في القناة.\n"
                f"2. الحساب المساعد (صاحب السيشن) عضو داخل القناة ولديه صلاحية التحدث."
            )

# --- [ 3. أمر إيقاف البث /stop ] ---
@bot.on_message(filters.command("stop") & filters.private)
async def stop_cmd(client: Client, message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply_text("❌ الصيغة خاطئة! من فضلك أرسل الأمر هكذا لإيقاف البث:\n`/stop يوزر_أو_آيدي_القناة`")
        return

    channel_input = args[1].strip()
    status_msg = await message.reply_text("⏳ جاري مغادرة المكالمة وإيقاف البث...")

    try:
        try:
            chat = await bot.get_chat(channel_input)
            chat_id = chat.id
        except Exception:
            chat_id = int(channel_input) if (channel_input.startswith("-100") or channel_input.isdigit()) else channel_input

        if isinstance(chat_id, str) and not chat_id.startswith("@"):
            chat_id = int(chat_id)

        await pytgcalls.leave_group_call(chat_id)
        await status_msg.edit_text(f"🛑 تم إيقاف البث ومغادرة المكالمة بنجاح من: `{channel_input}`")
    except Exception as e:
        await status_msg.edit_text(f"❌ حدث خطأ أثناء محاولة الإيقاف: {e}")

# --- [ تشغيل كافة المكونات بالتزامن ] ---
async def start_services():
    print("🚀 جاري إقلاع البوت التفاعلي والحساب المساعد معاً...", flush=True)
    await bot.start()
    await assistant.start()
    await pytgcalls.start()
    print("🌟 النظام جاهز تماماً الآن ومستعد لتلقي رسائلك في الخاص!", flush=True)
    await pyrogram.idle()

if __name__ == "__main__":
    asyncio.run(start_services())
