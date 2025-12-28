from pyrogram import filters
from Oneforall import app
from Oneforall.vclogger import VC_LOGGER

@app.on_message(filters.command("vclogger") & filters.group)
async def vclogger_handler(_, message):
    if len(message.command) < 2:
        return await message.reply_text(
            "Usage:\n/vclogger on\n/vclogger off"
        )

    chat_id = message.chat.id
    option = message.command[1].lower()

    if option == "on":
        VC_LOGGER.add(chat_id)
        await message.reply_text("✅ **VC Logger Enabled**")
    elif option == "off":
        VC_LOGGER.discard(chat_id)
        await message.reply_text("❌ **VC Logger Disabled**")

@app.on_message(filters.command("vcstatus") & filters.group)
async def vcstatus(_, message):
    status = message.chat.id in VC_LOGGER
    await message.reply_text(
        f"🎙️ VC Logger Status: {'ON' if status else 'OFF'}"
    )