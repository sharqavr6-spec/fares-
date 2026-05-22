import os
import asyncio
import sys
import traceback

from pyrogram import Client, filters
from pyrogram.types import Message

import pyrogram.errors
if not hasattr(pyrogram.errors, "GroupcallForbidden"):
    class GroupcallForbidden(Exception):
        pass
    pyrogram.errors.GroupcallForbidden = GroupcallForbidden

from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped


# =====================
# ENV
# =====================
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
SESSION_STRING = os.environ.get("SESSION_STRING", "")
OWNER_ID = os.environ.get("OWNER_ID", "0")

if not API_ID or not API_HASH or not BOT_TOKEN or not SESSION_STRING:
    print("❌ Missing environment variables", flush=True)
    sys.exit(1)

OWNER_ID = int(OWNER_ID) if OWNER_ID.isdigit() else None

print("⚙️ Starting bot on free hosting...", flush=True)

# =====================
# Clients
# =====================
bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
assistant = Client("assistant", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

pytgcalls = PyTgCalls(assistant)

user_states = {}

# =====================
# Start Command
# =====================
@bot.on_message(filters.private & filters.text)
async def handler(client: Client, message: Message):
    try:
        text = message.text.strip()
        user_id = message.from_user.id

        # START
        if text == "/start":
            user_states[user_id] = {"step": "channel"}
            await message.reply("📥 أرسل القناة أو الجروب (مثال @group)")
            return

        # STOP
        if text.startswith("/stop"):
            parts = text.split(maxsplit=1)
            if len(parts) < 2:
                await message.reply("❌ اكتب /stop @group")
                return

            chat = parts[1]

            try:
                chat_id = (await bot.get_chat(chat)).id
            except:
                chat_id = int(chat)

            await pytgcalls.leave_group_call(chat_id)
            await message.reply("⏹ تم الإيقاف")
            return

        # STATE MACHINE
        state = user_states.get(user_id)
        if not state:
            return

        if state["step"] == "channel":
            user_states[user_id] = {"step": "url", "channel": text}
            await message.reply("📻 الآن أرسل رابط البث")
            return

        if state["step"] == "url":
            stream_url = text
            channel = state["channel"]
            user_states.pop(user_id, None)

            status = await message.reply("⏳ جاري التشغيل...")

            try:
                try:
                    chat_id = (await bot.get_chat(channel)).id
                except:
                    chat_id = int(channel)

                await pytgcalls.join_group_call(
                    chat_id,
                    AudioPiped(stream_url)
                )

                await status.edit("📻 تم تشغيل البث بنجاح")

            except Exception as e:
                await status.edit(f"❌ خطأ: {e}")

    except Exception:
        traceback.print_exc()


# =====================
# MAIN START
# =====================
async def main():
    print("🚀 Starting services...", flush=True)

    await bot.start()
    await assistant.start()
    await pytgcalls.start()

    print("✅ Bot is running!")

    if OWNER_ID:
        try:
            await bot.send_message(OWNER_ID, "✅ Bot started successfully")
        except:
            pass

    # KEEP ALIVE (مناسب للهوستات المجانية)
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
