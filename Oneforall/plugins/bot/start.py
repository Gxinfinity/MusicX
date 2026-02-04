import asyncio
import time

from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from youtubesearchpython.__future__ import VideosSearch

import config
from config import BANNED_USERS
from Oneforall import app
from Oneforall.misc import _boot_, SUDOERS
from Oneforall.plugins.sudo.sudoers import sudoers_list
from Oneforall.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_lang,
    is_banned_user,
    is_on_off,
)
from Oneforall.utils.decorators.language import LanguageStart
from Oneforall.utils.formatters import get_readable_time
from Oneforall.utils.inline import help_pannel, private_panel, start_panel
from strings import get_string


# =========================
# START → PRIVATE
# =========================
@app.on_message(filters.command("start") & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    await add_served_user(message.from_user.id)
    await message.react("❤")

    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]

        # HELP
        if name.startswith("help"):
            await message.reply_sticker(
                "CAACAgUAAxkBAAEQPYppZ5NUzyEuz9krlTBI7WJxE4l9HgACxggAAtL9OVfNmn5c5Qtt7DgE"
            )
            return await message.reply_video(
    video=config.START_VIDEO_URL,
    caption=_["help_1"].format(config.SUPPORT_CHAT),
    reply_markup=help_pannel(_),
            )

        # SUDO LIST
        if name.startswith("sud"):
            await sudoers_list(client=client, message=message, _=_)
            if await is_on_off(2):
                await app.send_message(
                    config.LOGGER_ID,
                    f"{message.from_user.mention} checked <b>SUDO LIST</b>\n\n"
                    f"<b>ID:</b> <code>{message.from_user.id}</code>\n"
                    f"<b>Username:</b> @{message.from_user.username}",
                )
            return

        # TRACK INFO
        if name.startswith("inf"):
            m = await message.reply_text("🔎")
            query = name.replace("info_", "", 1)
            results = VideosSearch(f"https://www.youtube.com/watch?v={query}", limit=1)

            for r in (await results.next())["result"]:
                title = r["title"]
                duration = r["duration"]
                views = r["viewCount"]["short"]
                thumbnail = r["thumbnails"][0]["url"].split("?")[0]
                channel = r["channel"]["name"]
                channellink = r["channel"]["link"]
                link = r["link"]
                published = r["publishedTime"]

            await m.delete()
            await app.send_photo(
                message.chat.id,
                photo=thumbnail,
                caption=_["start_6"].format(
                    title, duration, views, published, channellink, channel, app.mention
                ),
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(_["S_B_8"], url=link),
                            InlineKeyboardButton(_["S_B_9"], url=config.SUPPORT_CHAT),
                        ]
                    ]
                ),
            )
            return

    # NORMAL START
    await message.reply_video(
        video=config.START_VIDEO_URL,
        caption=_["start_2"].format(message.from_user.mention, app.mention),
        reply_markup=InlineKeyboardMarkup(private_panel(_)),
    )

    if await is_on_off(2):
        await app.send_message(
            config.LOGGER_ID,
            f"{message.from_user.mention} started the bot\n\n"
            f"<b>ID:</b> <code>{message.from_user.id}</code>\n"
            f"<b>Username:</b> @{message.from_user.username}",
        )


# =========================
# START → GROUP
# =========================
@app.on_message(filters.command("start") & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_gp(client, message: Message, _):
    uptime = int(time.time() - _boot_)
    await message.reply_video(
        photo=config.START_VIDEO_URL,
        caption=_["start_1"].format(app.mention, get_readable_time(uptime)),
        reply_markup=InlineKeyboardMarkup(start_panel(_)),
        has_spoiler=True
    )
    await add_served_chat(message.chat.id)


# =========================
# WELCOME HANDLER
# =========================
@app.on_message(filters.new_chat_members, group=-1)
async def welcome_handler(client, message: Message):
    for member in message.new_chat_members:
        try:
            language = await get_lang(message.chat.id)
            _ = get_string(language)

            # BAN CHECK
            if await is_banned_user(member.id):
                try:
                    await message.chat.ban_member(member.id)
                except:
                    pass
                return

            # BOT JOINED
            if member.id == app.id:
                if message.chat.type != ChatType.SUPERGROUP:
                    await message.reply_text(_["start_4"])
                    return await app.leave_chat(message.chat.id)

                if message.chat.id in await blacklisted_chats():
                    await message.reply_text(
                        _["start_5"].format(
                            app.mention,
                            f"https://t.me/{app.username}?start=sudolist",
                            config.SUPPORT_CHAT,
                        ),
                        disable_web_page_preview=True,
                    )
                    return await app.leave_chat(message.chat.id)

                await message.reply_photo(
                    photo=config.START_VIDEO_URL,
                    caption=_["start_3"].format(
                        message.from_user.first_name,
                        app.mention,
                        message.chat.title,
                        app.mention,
                    ),
                    reply_markup=InlineKeyboardMarkup(start_panel(_)),
                )
                await add_served_chat(message.chat.id)
                await message.stop_propagation()
                return

            # OWNER WELCOME
            if member.id == config.OWNER_ID:
                msg = await message.reply_text(
                    f"👑 <b>BOT OWNER JOINED</b>\n\n{member.mention}"
                )
                await asyncio.sleep(20)
                await msg.delete()

            # SUDO WELCOME
            if isinstance(SUDOERS, (list, set)):
                is_sudo = member.id in SUDOERS
            else:
                is_sudo = member.id == SUDOERS

            if is_sudo:
                msg = await message.reply_text(
                    f"⚡ <b>SUDO USER JOINED</b>\n\n{member.mention}"
                )
                await asyncio.sleep(20)
                await msg.delete()

        except Exception as e:
            print(f"[WELCOME ERROR] {e}")