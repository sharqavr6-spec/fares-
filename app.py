import os
import asyncio
import traceback
from pyrogram import Client, filters, idle
from pyrogram.types import Message

# --- تخطي أخطاء مكتبة المكالمات ---
import pyrogram.errors
if not hasattr(pyrogram.errors, "GroupcallForbidden"):
    class GroupcallForbidden(Exception): pass
    pyrogram.errors.GroupcallForbidden = GroupcallForbidden

from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream

# جلب الإعدادات
API_ID = os.environ.get("API_ID", "").strip()
API_HASH = os.environ.get("API_HASH", "").strip()
BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip()
SESSION_STRING = os.environ.get("SESSION_STRING", "").strip()
OWNER_ID = os.environ.get("OWNER_ID", "").strip()

if not all([API_ID, API_HASH, BOT_TOKEN, SESSION_STRING]):
    print("❌ خطأ: إعدادات Railway غير مكتملة!", flush=True)
    sys.exit(1)

API_ID = int(API_ID)
OWNER_ID = int(OWNER_ID) if (OWNER_ID and OWNER_ID.isdigit()) else None

print("⚙️ جاري التشغيل بوضع الذاكرة الحية (In-Memory) لتخطي تجميد Railway...", flush=True)

# 🚀 الحل السحري: in_memory=True تمنع تجمد قاعدة البيانات نهائياً في ريلواي
bot = Client("tg_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, in_memory=True)
assistant = Client("tg_account", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING, in_memory=True)
pytgcalls = PyTgCalls(assistant)

user_states = {}

@bot.on_message(filters.text & filters.private)
async def main_bot_router(client: Client, message: Message):
    try:
        text = message.text.strip()
        user_id = message.from_user.id

        # تفاعل فوري بإيموجي لتأكيد القراءة والاستجابة (بدل الردود النصية المزعجة)
        try:
            await client.send_reaction(chat_id=message.chat.id, message_id=message.id, emoji="⚡")
        except Exception:
            pass

        print(f"📥 استلمت أمر: {text} من {user_id}", flush=True)

        if text.startswith("/start"):
            user_states[user_id] = {"step": "WAITING_FOR_CHANNEL"}
            await message.reply_text("أرسل الآن يوزر القناة (مثال: @MyChannel) أو الآيدي:")
            return

        elif text.startswith("/stop"):
            args = text.split(maxsplit=1)
            if len(args) < 2:
                await message.reply_text("أرسل الأمر هكذا: `/stop يوزر_القناة`")
                return

            channel_input = args[1].strip()
            
            try:
                try:
                    chat = await bot.get_chat(channel_input)
                    chat_id = chat.id
                except Exception:
                    chat_id = int(channel_input) if (channel_input.startswith("-100") or channel_input.isdigit()) else channel_input

                await pytgcalls.leave_group_call(chat_id)
                try:
                    await client.send_reaction(chat_id=message.chat.id, message_id=message.id, emoji="🛑")
                except:
                    await message.reply_text(f"🛑 تم إيقاف البث.")
            except Exception as e:
                await message.reply_text(f"❌ خطأ: {e}")
            return

        state = user_states.get(user_id)
        if not state:
            return

        step = state.get("step")

        if step == "WAITING_FOR_CHANNEL":
            user_states[user_id] = {"step": "WAITING_FOR_URL", "channel": text}
            try:
                await client.send_reaction(chat_id=message.chat.id, message_id=message.id, emoji="👍")
            except:
                pass
            await message.reply_text("✅ ممتاز. أرسل الآن رابط البث المباشر (Stream URL):")

        elif step == "WAITING_FOR_URL":
            stream_url = text
            channel_input = state.get("channel")
            user_states.pop(user_id, None)
            
            try:
                try:
                    chat = await bot.get_chat(channel_input)
                    chat_id = chat.id
                except Exception:
                    chat_id = int(channel_input) if (channel_input.startswith("-100") or channel_input.isdigit()) else channel_input

                await pytgcalls.join_group_call(chat_id, MediaStream(stream_url))
                try:
                    await client.send_reaction(chat_id=message.chat.id, message_id=message.id, emoji="🔥")
                except:
                    pass
                await message.reply_text(f"📻 **تم تشغيل البث بنجاح في `{channel_input}`!**")
            except Exception as e:
                await message.reply_text(f"❌ فشل التشغيل: {e}")

    except Exception:
        traceback.print_exc()

async def start_services():
    print("🚀 بدء تشغيل الحسابات...", flush=True)
    await bot.start()
    await assistant.start()
    await pytgcalls.start()
    
    if OWNER_ID:
        try:
            await bot.send_message(chat_id=OWNER_ID, text="⚡ **تم تفعيل وضع الذاكرة الحية والتفاعلات بالإيموجي. جرب /start الآن، لن يتجمد السيرفر!**")
        except Exception:
            pass

    # استخدام idle الرسمي من بايروجرام لضمان عدم موت الاتصال
    await idle()
    
    await pytgcalls.stop()
    await bot.stop()
    await assistant.stop()

if __name__ == "__main__":
    asyncio.run(start_services())
