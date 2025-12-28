from pyrogram.raw.types import UpdateGroupCallParticipants, GroupCallParticipant
from Oneforall import userbot, app

VC_LOGGER = set()

# 🔥 IMPORTANT: use userbot.app (REAL pyrogram client)
@userbot.app.on_raw_update()
async def vc_join_listener(client, update, users, chats):
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