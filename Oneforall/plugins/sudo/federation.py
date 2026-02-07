import asyncio
from datetime import datetime

from pyrogram import filters
from pyrogram.enums import ChatMemberStatus, ChatType
from pyrogram.errors import FloodWait
from pyrogram.types import Message

from Oneforall import app
from Oneforall.core.mongo import mongodb
from Oneforall.misc import SUDOERS
from Oneforall.utils.functions import extract_user, extract_user_and_reason
from config import BANNED_USERS


__MODULE__ = "Fᴇᴅᴇʀᴀᴛɪᴏɴ"
__HELP__ = """
/newfed <name> - Create a new federation.
/addfed <fed_id> - Connect current group to a federation.
/chatfed - Show linked federation details for the current chat.
/fpromote | /fptomote <user> - Promote a user as federation admin.
/superban <user> [reason] - Ban a user from all chats linked to federation.
/unsuperban <user> - Unban a user in all federation chats.
/fedbanlist - List federation banned users.
"""

fedsdb = mongodb.federations
fedbansdb = mongodb.federation_bans


async def get_fed_by_chat(chat_id: int):
    return await fedsdb.find_one({"chats": chat_id})


async def is_chat_admin(chat_id: int, user_id: int) -> bool:
    member = await app.get_chat_member(chat_id, user_id)
    return member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]


async def can_manage_fed(fed: dict, user_id: int) -> bool:
    if user_id in SUDOERS:
        return True
    if user_id == fed.get("owner_id"):
        return True
    return user_id in fed.get("admins", [])


@app.on_message(filters.command("newfed") & ~BANNED_USERS)
async def newfed_command(_, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /newfed <federation name>")

    fed_name = message.text.split(None, 1)[1].strip()
    fed_id = f"fed_{message.from_user.id}_{int(datetime.utcnow().timestamp())}"

    await fedsdb.insert_one(
        {
            "fed_id": fed_id,
            "name": fed_name,
            "owner_id": message.from_user.id,
            "admins": [],
            "chats": [],
            "created_at": datetime.utcnow(),
        }
    )

    await message.reply_text(
        f"Federation created.\n**Name:** {fed_name}\n**Fed ID:** `{fed_id}`\nUse /addfed {fed_id} in a group to connect it."
    )


@app.on_message(filters.command("addfed") & ~filters.private & ~BANNED_USERS)
async def addfed_command(_, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /addfed <fed_id>")

    if not await is_chat_admin(message.chat.id, message.from_user.id):
        return await message.reply_text("You must be a chat admin to connect a federation.")

    fed_id = message.command[1].strip()
    fed = await fedsdb.find_one({"fed_id": fed_id})
    if not fed:
        return await message.reply_text("Federation not found.")

    if not await can_manage_fed(fed, message.from_user.id):
        return await message.reply_text("You are not allowed to manage this federation.")

    if message.chat.id in fed.get("chats", []):
        return await message.reply_text("This chat is already connected to this federation.")

    await fedsdb.update_one({"fed_id": fed_id}, {"$addToSet": {"chats": message.chat.id}})

    existing_bans = fedbansdb.find({"fed_id": fed_id})
    applied = 0
    async for ban in existing_bans:
        try:
            await app.ban_chat_member(message.chat.id, ban["user_id"])
            applied += 1
        except Exception:
            continue

    await message.reply_text(
        f"Connected this chat to federation **{fed['name']}** (`{fed_id}`).\nApplied {applied} existing superbans."
    )


@app.on_message(filters.command("chatfed") & ~filters.private & ~BANNED_USERS)
async def chatfed_command(_, message: Message):
    fed = await get_fed_by_chat(message.chat.id)
    if not fed:
        return await message.reply_text("This chat is not connected to any federation.")

    owner = fed.get("owner_id")
    admins = fed.get("admins", [])
    chats = fed.get("chats", [])
    bans_count = await fedbansdb.count_documents({"fed_id": fed["fed_id"]})

    await message.reply_text(
        "**Federation details**\n"
        f"Name: {fed['name']}\n"
        f"Fed ID: `{fed['fed_id']}`\n"
        f"Owner ID: `{owner}`\n"
        f"Fed admins: `{len(admins)}`\n"
        f"Connected chats: `{len(chats)}`\n"
        f"Superbanned users: `{bans_count}`"
    )


@app.on_message(filters.command(["fpromote", "fptomote"]) & ~filters.private & ~BANNED_USERS)
async def fpromote_command(_, message: Message):
    fed = await get_fed_by_chat(message.chat.id)
    if not fed:
        return await message.reply_text("This chat is not connected to any federation.")

    if message.from_user.id not in SUDOERS and message.from_user.id != fed.get("owner_id"):
        return await message.reply_text("Only federation owner can promote federation admins.")

    user_id = await extract_user(message)
    if not user_id:
        return await message.reply_text("Reply to a user or pass a valid user ID/username.")

    if user_id in fed.get("admins", []):
        return await message.reply_text("User is already a federation admin.")

    await fedsdb.update_one({"fed_id": fed["fed_id"]}, {"$addToSet": {"admins": user_id}})
    await message.reply_text(f"Promoted `{user_id}` as federation admin in `{fed['fed_id']}`.")


@app.on_message(filters.command(["superban", "fedban"]) & ~filters.private & ~BANNED_USERS)
async def superban_command(_, message: Message):
    fed = await get_fed_by_chat(message.chat.id)
    if not fed:
        return await message.reply_text("This chat is not connected to any federation.")

    if not await can_manage_fed(fed, message.from_user.id):
        return await message.reply_text("You need federation admin rights to use /superban.")

    user_id, reason = await extract_user_and_reason(message)
    if not user_id:
        return await message.reply_text("Reply to a user or give a valid user id/username.")
    if user_id in SUDOERS or user_id == app.id:
        return await message.reply_text("Cannot superban this user.")

    already = await fedbansdb.find_one({"fed_id": fed["fed_id"], "user_id": user_id})
    if already:
        return await message.reply_text("This user is already superbanned in this federation.")

    await fedbansdb.insert_one(
        {
            "fed_id": fed["fed_id"],
            "user_id": user_id,
            "reason": reason or "No reason provided",
            "banned_by": message.from_user.id,
            "banned_at": datetime.utcnow(),
        }
    )

    count = 0
    for chat_id in fed.get("chats", []):
        try:
            await app.ban_chat_member(chat_id, user_id)
            count += 1
        except FloodWait as fw:
            await asyncio.sleep(int(fw.value))
        except Exception:
            continue

    await message.reply_text(
        f"Superbanned `{user_id}` in federation `{fed['fed_id']}`.\nAffected chats: `{count}`\nReason: {reason or 'No reason provided'}"
    )


@app.on_message(filters.command(["unsuperban", "unfedban"]) & ~filters.private & ~BANNED_USERS)
async def unsuperban_command(_, message: Message):
    fed = await get_fed_by_chat(message.chat.id)
    if not fed:
        return await message.reply_text("This chat is not connected to any federation.")

    if not await can_manage_fed(fed, message.from_user.id):
        return await message.reply_text("You need federation admin rights to use /unsuperban.")

    user_id = await extract_user(message)
    if not user_id:
        return await message.reply_text("Reply to a user or pass a valid user ID/username.")

    exists = await fedbansdb.find_one({"fed_id": fed["fed_id"], "user_id": user_id})
    if not exists:
        return await message.reply_text("User is not superbanned in this federation.")

    await fedbansdb.delete_one({"fed_id": fed["fed_id"], "user_id": user_id})

    count = 0
    for chat_id in fed.get("chats", []):
        try:
            await app.unban_chat_member(chat_id, user_id)
            count += 1
        except FloodWait as fw:
            await asyncio.sleep(int(fw.value))
        except Exception:
            continue

    await message.reply_text(f"Removed superban for `{user_id}`. Chats updated: `{count}`")


@app.on_message(filters.command("fedbanlist") & ~filters.private & ~BANNED_USERS)
async def fedbanlist_command(_, message: Message):
    fed = await get_fed_by_chat(message.chat.id)
    if not fed:
        return await message.reply_text("This chat is not connected to any federation.")

    cursor = fedbansdb.find({"fed_id": fed["fed_id"]})
    lines = [f"**Superban list for {fed['name']}**"]
    count = 0
    async for entry in cursor:
        count += 1
        lines.append(f"{count}. `{entry['user_id']}` - {entry.get('reason', 'No reason')}")
        if count >= 50:
            break

    if count == 0:
        return await message.reply_text("No users are superbanned in this federation.")

    await message.reply_text("\n".join(lines))


@app.on_message(filters.group & ~filters.service & ~BANNED_USERS, group=8)
async def enforce_fed_superban(_, message: Message):
    if message.chat.type not in [ChatType.SUPERGROUP, ChatType.GROUP]:
        return
    if not message.from_user:
        return

    fed = await get_fed_by_chat(message.chat.id)
    if not fed:
        return

    user_id = message.from_user.id
    if user_id in SUDOERS:
        return

    banned = await fedbansdb.find_one({"fed_id": fed["fed_id"], "user_id": user_id})
    if not banned:
        return

    try:
        await app.ban_chat_member(message.chat.id, user_id)
        await message.reply_text(
            f"User `{user_id}` is federation-superbanned and was removed."
        )
    except Exception:
        return
