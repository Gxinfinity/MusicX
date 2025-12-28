from pyrogram import filters
from Oneforall import userbot

VC_LOGGER = set()


# COMMAND — bot se reply
@userbot.one.on_message(filters.command("vclogger") & filters.group)
async def vclogger_cmd(client, message):
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


# 🔥 REAL VC INVITE LOGGER
@userbot.one.on_message(filters.video_chat_members_invited & filters.group)
async def vc_invite(client, message):
    if message.chat.id not in VC_LOGGER:
        return

    for user in message.video_chat_members_invited.users:
        await message.reply_text(
            f"""🤖 **ROOHI VC LOGGER**

#JoinVideoChat
👤 NAME : {user.first_name}
🆔 ID : `{user.id}`
🔗 USER : @{user.username if user.username else "None"}
ACTION : IGNORED
"""
        )