import asyncio
from datetime import datetime

from pyrogram import filters
from pyrogram.enums import ChatMemberStatus, ChatType
from pyrogram.errors import FloodWait
from pyrogram.types import Message

import config
from config import BANNED_USERS
from Oneforall import app, userbot
from Oneforall.core.mongo import mongodb
from Oneforall.misc import SUDOERS
from Oneforall.utils import get_readable_time
from Oneforall.utils.database import (
    add_banned_user,
    get_banned_count,
    get_banned_users,
    get_served_chats,
    is_banned_user,
    remove_banned_user,
)
from Oneforall.utils.decorators.language import language
from Oneforall.utils.extraction import extract_user

superbanstatsdb = mongodb.superban_stats
fedbansdb = mongodb.federation_bans


def _get_active_assistants():
    assistants = []
    for assistant in [userbot.one, userbot.two, userbot.three, userbot.four, userbot.five]:
        if assistant and getattr(assistant, "is_connected", False):
            assistants.append(assistant)
    return assistants


def _get_allowed_bridge_ids():
    ids = set(config.NETWORK_BRIDGE_IDS)
    if config.ASSISTANT_BRIDGE_ID:
        ids.add(config.ASSISTANT_BRIDGE_ID)
    return ids


async def _assistant_global_ban(user_id: int):
    affected_chats = 0
    assistants = _get_active_assistants()
    for assistant in assistants:
        async for dialog in assistant.get_dialogs(limit=400):
            if dialog.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
                continue
            try:
                member = await assistant.get_chat_member(dialog.chat.id, "me")
                if member.status not in [
                    ChatMemberStatus.ADMINISTRATOR,
                    ChatMemberStatus.OWNER,
                ]:
                    continue
                await assistant.ban_chat_member(dialog.chat.id, user_id)
                affected_chats += 1
            except FloodWait as fw:
                await asyncio.sleep(int(fw.value))
            except Exception:
                continue
    return affected_chats


async def _sync_other_bots(user_id: int):
    if not config.NETWORK_SUB_BOTS:
        return 0
    command = f"{config.NETWORK_INTERNAL_GBAN_COMMAND} {user_id}"
    sent = 0
    assistants = _get_active_assistants()
    for bot in config.NETWORK_SUB_BOTS:
        for assistant in assistants:
            if config.ASSISTANT_BRIDGE_ID and assistant.me.id != config.ASSISTANT_BRIDGE_ID:
                continue
            try:
                await assistant.send_message(bot, command)
                sent += 1
                break
            except Exception:
                continue
    return sent


async def _send_rose_fban(user_id: int):
    if not config.ROSE_FEDERATION_CHAT:
        return False
    assistants = _get_active_assistants()
    for assistant in assistants:
        if config.ASSISTANT_BRIDGE_ID and assistant.me.id != config.ASSISTANT_BRIDGE_ID:
            continue
        try:
            await assistant.send_message(
                config.ROSE_FEDERATION_CHAT,
                f"{config.ROSE_FBAN_COMMAND} {user_id}",
            )
            return True
        except Exception:
            continue
    return False


async def _save_superban_stats(user_id: int, data: dict):
    payload = {
        "user_id": user_id,
        "main_bot_chats": data.get("main_bot_chats", 0),
        "assistant_chats": data.get("assistant_chats", 0),
        "sub_bots_synced": data.get("sub_bots_synced", 0),
        "rose_fban_sent": data.get("rose_fban_sent", False),
        "performed_by": data.get("performed_by", 0),
        "performed_at": datetime.utcnow(),
    }
    await superbanstatsdb.update_one(
        {"user_id": user_id}, {"$set": payload}, upsert=True
    )


async def _build_supstat_text(user):
    user_id = user.id
    stats = await superbanstatsdb.find_one({"user_id": user_id}) or {}
    fed_count = await fedbansdb.count_documents({"user_id": user_id})
    total_bots = 1 + int(stats.get("sub_bots_synced", 0))
    total_chats = int(stats.get("main_bot_chats", 0)) + int(stats.get("assistant_chats", 0))

    return (
        "<code>[ ꜱᴜᴘᴇʀʙᴀɴ ꜱᴛᴀᴛᴜꜱ ]\n"
        f"👤 Target: {user.first_name} | {user_id}\n"
        f"🛰️ Federations: {fed_count}\n"
        f"🤖 Bots Synced: {total_bots}\n"
        f"💬 Chats Impacted: {total_chats}\n"
        f"⚡ Main Bot Chats: {int(stats.get('main_bot_chats', 0))}\n"
        f"🛡️ Assistant Chats: {int(stats.get('assistant_chats', 0))}\n"
        f"🔗 Rose FBan: {'Sent' if stats.get('rose_fban_sent') else 'Not Sent'}\n"
        f"🕒 Last Update: {stats.get('performed_at', 'N/A')}</code>"
    )


def _network_report(user_name: str, user_id: int, sudo_name: str, chats_count: int):
    return (
        "<code>[ ꜱʏꜱᴛᴇᴍ-ᴡɪᴅᴇ ɴᴇᴛᴡᴏʀᴋ ʙᴀɴ ]\n"
        f"👤 Target: {user_name} | {user_id}\n"
        f"⚡ Main Bot: GBanned in {chats_count} Chats\n"
        "🤖 Sub-Bots: Global Ban Synced Successfully\n"
        "🛡️ Assistant: Userbot-Level Ban Applied\n"
        "🔗 Federation: FBan Request Sent to Rose\n"
        f"👮 Authorized By: {sudo_name}</code>"
    )


@app.on_message(filters.command(["gban", "globalban", "superban"]) & SUDOERS)
@language
async def global_ban(client, message: Message, _):
    if not message.reply_to_message:
        if len(message.command) != 2:
            return await message.reply_text(_["general_1"])
    user = await extract_user(message)
    if user.id == message.from_user.id:
        return await message.reply_text(_["gban_1"])
    elif user.id == app.id:
        return await message.reply_text(_["gban_2"])
    elif user.id in SUDOERS:
        return await message.reply_text(_["gban_3"])
    is_gbanned = await is_banned_user(user.id)
    if is_gbanned:
        return await message.reply_text(_["gban_4"].format(user.mention))
    if user.id not in BANNED_USERS:
        BANNED_USERS.add(user.id)
    served_chats = []
    chats = await get_served_chats()
    for chat in chats:
        served_chats.append(int(chat["chat_id"]))
    time_expected = get_readable_time(len(served_chats))
    mystic = await message.reply_text(_["gban_5"].format(user.mention, time_expected))
    number_of_chats = 0
    for chat_id in served_chats:
        try:
            await app.ban_chat_member(chat_id, user.id)
            number_of_chats += 1
        except FloodWait as fw:
            await asyncio.sleep(int(fw.value))
        except Exception:
            continue
    await add_banned_user(user.id)

    assistant_chat_count = await _assistant_global_ban(user.id)
    synced_bot_count = await _sync_other_bots(user.id)
    rose_sent = await _send_rose_fban(user.id)

    await _save_superban_stats(
        user.id,
        {
            "main_bot_chats": number_of_chats,
            "assistant_chats": assistant_chat_count,
            "sub_bots_synced": synced_bot_count,
            "rose_fban_sent": rose_sent,
            "performed_by": message.from_user.id,
        },
    )

    report = _network_report(
        user.first_name,
        user.id,
        message.from_user.first_name,
        number_of_chats,
    )
    await message.reply_text(report)
    await mystic.delete()


@app.on_message(filters.command(["supstat", "superbanstat"]) & SUDOERS)
async def supstat_command(_, message: Message):
    if not message.reply_to_message and len(message.command) != 2:
        return await message.reply_text("Usage: /supstat <userid|username|reply>")

    user = await extract_user(message)
    status = await _build_supstat_text(user)
    await message.reply_text(status)


@app.on_message(filters.command(config.NETWORK_INTERNAL_GBAN_COMMAND.lstrip("/")))
async def internal_network_gban(_, message: Message):
    if len(message.command) < 2 or not message.from_user:
        return
    bridge_ids = _get_allowed_bridge_ids()
    if message.from_user.id not in bridge_ids and message.from_user.id not in SUDOERS:
        return
    try:
        user_id = int(message.command[1])
    except ValueError:
        return
    if user_id in BANNED_USERS:
        return
    BANNED_USERS.add(user_id)
    chats = await get_served_chats()
    ban_count = 0
    for chat in chats:
        try:
            await app.ban_chat_member(int(chat["chat_id"]), user_id)
            ban_count += 1
        except Exception:
            continue
    await add_banned_user(user_id)
    await _save_superban_stats(
        user_id,
        {
            "main_bot_chats": ban_count,
            "assistant_chats": 0,
            "sub_bots_synced": 0,
            "rose_fban_sent": False,
            "performed_by": message.from_user.id,
        },
    )


@app.on_message(filters.command(["ungban"]) & SUDOERS)
@language
async def global_un(client, message: Message, _):
    if not message.reply_to_message:
        if len(message.command) != 2:
            return await message.reply_text(_["general_1"])
    user = await extract_user(message)
    is_gbanned = await is_banned_user(user.id)
    if not is_gbanned:
        return await message.reply_text(_["gban_7"].format(user.mention))
    if user.id in BANNED_USERS:
        BANNED_USERS.remove(user.id)
    served_chats = []
    chats = await get_served_chats()
    for chat in chats:
        served_chats.append(int(chat["chat_id"]))
    time_expected = get_readable_time(len(served_chats))
    mystic = await message.reply_text(_["gban_8"].format(user.mention, time_expected))
    number_of_chats = 0
    for chat_id in served_chats:
        try:
            await app.unban_chat_member(chat_id, user.id)
            number_of_chats += 1
        except FloodWait as fw:
            await asyncio.sleep(int(fw.value))
        except Exception:
            continue
    await remove_banned_user(user.id)
    await message.reply_text(_["gban_9"].format(user.mention, number_of_chats))
    await mystic.delete()


@app.on_message(filters.command(["gbannedusers", "gbanlist"]) & SUDOERS)
@language
async def gbanned_list(client, message: Message, _):
    counts = await get_banned_count()
    if counts == 0:
        return await message.reply_text(_["gban_10"])
    mystic = await message.reply_text(_["gban_11"])
    msg = _["gban_12"]
    count = 0
    users = await get_banned_users()
    for user_id in users:
        count += 1
        try:
            user = await app.get_users(user_id)
            user = user.first_name if not user.mention else user.mention
            msg += f"{count}➤ {user}\n"
        except Exception:
            msg += f"{count}➤ {user_id}\n"
            continue
    if count == 0:
        return await mystic.edit_text(_["gban_10"])
    else:
        return await mystic.edit_text(msg)
