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
OWNER_ID = os.environ.get("OWNER_ID", "").strip()  # آيدي حسابك أنت لتلقي إشعار التشغيل

if not all([API_ID, API_HASH, BOT_TOKEN, SESSION_STRING]):
    print("❌ خطأ: تأكد من إضافة (API_ID, API_HASH, BOT_TOKEN, SESSION_STRING) في Railway!", flush=True)
    sys.exit(1)

API_ID = int(API_ID)
if OWNER_ID:
    try:
        OWNER_ID = int(OWNER_ID)
    except ValueError:
        print("⚠️ تنبيه: OWNER_ID يجب أن يكون رقماً فقط. سيتم تجاهل ميزة إشعار المالك التلقائي.", flush=True)
        OWNER_ID = None

# 2. إنشاء العميلين (البوت الموجه والحساب المساعد للبث)
print("🤖 جاري تهيئة البوت العام المفتوح للجميع...", flush=True)
bot = Client("tg_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
assistant = Client("tg_account", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

# ربط محرك الصوت بالحساب المساعد
pytgcalls = PyTgCalls(assistant)

# قاموس لحفظ خطوات المستخدمين في الذاكرة (لكل مستخدم حسب الآيدي الخاص به)
user_states = {}

# --- [ 1. أمر البداية /start - متاح لأي مستخدم ] ---
@bot.on_message(filters.command("start") & filters.private)
async def start_cmd(client: Client, message: Message):
    user_id = message.from_user.id
    # بدء تسجيل الخطوات لهذا المستخدم
    user_states[user_id] = {"step": "WAITING_FOR_CHANNEL"}
    
    welcome_text = (
        "👋 أهلاً بك في بوت تشغيل الإذاعة وبث القرآن الكريم المباشر!\n\n"
        "📥 لتشغيل البث في قناتك أو جروبك، من فضلك أرسل لي **يوزر القناة** (مثال: @MyChannel) أو الآيدي الرقمي الخاص بها:\n"
        "*(تأكد أولاً أن الحساب المساعد عضو في قناتك والمكالمة الصوتية مفتوحة)*"
    )
    await message.reply_text(welcome_text)

# --- [ 2. استقبال البيانات خطوة بخطوة - متاح لأي مستخدم ] ---
@bot.on_message(filters.text & filters.private & ~filters.command(["start", "stop"]))
async def handle_steps(client: Client, message: Message):
    user_id = message.from_user.id
    state = user_states.get(user_id)

    if not state:
        await message.reply_text("💡 من فضلك أرسل الأمر `/start` للبدء في ضبط البث خطوة بخطوة.")
        return

    step = state.get("step")

    # الخطوة الأولى: استلام القناة أو الجروب
    if step == "WAITING_FOR_CHANNEL":
        channel_input = message.text.strip()
        user_states[user_id] = {
            "step": "WAITING_FOR_URL",
            "channel": channel_input
        }
        await message.reply_text(
            f"✅ تم استقبال معرف القناة: `{channel_input}`\n\n"
            "📻 الآن، من فضلك أرسل **رابط الإذاعة أو البث الصوتي** (Stream URL) لتشغيله فوراً:"
        )

    # الخطوة الثانية: استلام الرابط والتشغيل الفعلي
    elif step == "WAITING_FOR_URL":
        stream_url = message.text.strip()
        channel_input = state.get("channel")
        
        # إنهاء حالة المستخدم ليكون جاهزاً لأي طلب مستقبلي
        user_states.pop(user_id, None)
        
        status_msg = await message.reply_text("⏳ جاري التحقق من القناة وتوجيه الحساب المساعد لبدء البث...")
        
        try:
            try:
                chat = await bot.get_chat(channel_input)
                chat_id = chat.id
            except Exception:
                if channel_input.startswith("-100") or channel_input.isdigit():
                    chat_id = int(channel_input)
                else:
                    chat_id = channel_input

            if isinstance(chat_id, str) and not chat_id.startswith("@"):
                chat_id = int(chat_id)

            # تشغيل البث
            await pytgcalls.join_group_call(
                chat_id,
                MediaStream(stream_url)
            )
            
            await status_msg.edit_text(
                f"🥳 **ممتاز! بدأ البث الصوتي بنجاح الآن!**\n\n"
                f"📢 القناة: `{channel_input}`\n"
                f"📻 رابط البث: {stream_url}\n\n"
                f"💡 لإيقاف البث في أي وقت، أرسل: `/stop {channel_input}`"
            )
            
        except Exception as e:
            await status_msg.edit_text(
                f"❌ **فشل بدء البث!**\n\n"
                f"⚠️ **السبب:** {e}\n\n"
                f"💡 **تأكد من:**\n"
                f"1. فتح المكالمة الصوتية في القناة يدوياً.\n"
                f"2. انضمام الحساب المساعد داخل هذه القناة."
            )

# --- [ 3. أمر إيقاف البث /stop - متاح لأي مستخدم ] ---
@bot.on_message(filters.command("stop") & filters.private)
async def stop_cmd(client: Client, message: Message):
    args = message.text.split(maxsplit=1)
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
        await status_msg.edit_text(f"🛑 تم إيقاف البث بنجاح من: `{channel_input}`")
    except Exception as e:
        await status_msg.edit_text(f"❌ حدث خطأ أثناء محاولة الإيقاف: {e}")

# --- [ تشغيل كافة المكونات بالتزامن وإرسال الإشعار الخاص بك ] ---
async def start_services():
    print("🚀 جاري إقلاع البوت والحساب المساعد معاً...", flush=True)
    await bot.start()
    await assistant.start()
    await pytgcalls.start()
    print("🌟 النظام جاهز ومستعد لاستقبال طلبات الجميع!", flush=True)
    
    # 🔔 إرسال الإشعار الخاص بك أنت فقط (صاحب البوت) عند التشغيل
    if OWNER_ID:
        try:
            await bot.send_message(
                chat_id=OWNER_ID,
                text="🙋‍♂️ **انا جاهز يا باشا!**\n\nالسيرفر اشتغل تمام والبوت شغال دلوقتي مع كل الناس عادي ومستني أوامرهم."
            )
            print("🔔 تم إرسال إشعار 'انا جاهز يا باشا' لحساب المالك بنجاح.", flush=True)
        except Exception as e:
            print(f"⚠️ لم نتمكن من إرسال رسالة الإقلاع للمالك. السبب: {e}", flush=True)
            
    await pyrogram.idle()

if __name__ == "__main__":
    asyncio.run(start_services())
