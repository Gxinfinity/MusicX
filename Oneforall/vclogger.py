from pyrogram.raw.types import UpdateGroupCallParticipants, GroupCallParticipant
from Oneforall import userbot, app

VC_LOGGER = set()


async def _vc_handler(client, update, users, chats):
    if not isinstance(update, UpdateGroupCallParticipants):
        return

    chat_id = update.chat_id
    if chat_id not in VC_LOGGER:
        return

    for p in update.participants:
        if isinstance(p, GroupCallParticipant):
            user = users.get(p.user_id)
            if not user:
                continue

            await app.send_message(
                chat_id,
                f"""#JoinVideoChat
👤 **Name** : {user.first_name}
🆔 **ID** : `{user.id}`
🔗 **Username** : @{user.username if user.username else 'Ignored'}
"""
            )


# 🔥 Attach listener to ALL assistant clients
if hasattr(userbot, "one"):
    userbot.one.add_handler(
        type("Raw", (), {"callback": _vc_handler})()
    )

if hasattr(userbot, "two"):
    userbot.two.add_handler(
        type("Raw", (), {"callback": _vc_handler})()
    )

if hasattr(userbot, "three"):
    userbot.three.add_handler(
        type("Raw", (), {"callback": _vc_handler})()
    )

if hasattr(userbot, "four"):
    userbot.four.add_handler(
        type("Raw", (), {"callback": _vc_handler})()
    )

if hasattr(userbot, "five"):
    userbot.five.add_handler(
        type("Raw", (), {"callback": _vc_handler})()
    )