from pyrogram import filters
from Oneforall import app

VC_LOGGER = set()


# /vclogger on | off
@app.on_message(filters.command("vclogger") & filters.group)
async def vclogger_handler(_, message):
    if len(message.command) < 2:
        return await message.reply_text(
            "Usage:\n/vclogger on\n/vclogger off"
        )

    chat_id = message.chat.id
    opt = message.command[1].lower()

    if opt == "on":
        VC_LOGGER.add(chat_id)
        await message.reply_text("✅ VC Logger Enabled")
    elif opt == "off":
        VC_LOGGER.discard(chat_id)
        await message.reply_text("❌ VC Logger Disabled")


# 🔥 SERVICE MESSAGE LISTENER
@app.on_message(filters.service & filters.group)
async def vc_service_logger(_, message):
    chat_id = message.chat.id
    if chat_id not in VC_LOGGER:
        return

    text = message.text or ""

    # INVITE / JOIN detect
    if "video chat" in text.lower():
        user = message.from_user
        if not user:
            return

        await message.reply_text(
            f"""🤖 **ROOHI VC LOGGER**

#JoinVideoChat
👤 NAME : {user.first_name}
🆔 ID : `{user.id}`
🔗 USER : @{user.username if user.username else "None"}
"""
        )