import time
from pyrogram.handlers import RawUpdateHandler
from pyrogram.raw.types import UpdateGroupCallParticipants, GroupCallParticipant
from Oneforall import userbot, app

VC_LOGGER = set()

# user_id -> join_time
VC_JOIN_TIME = {}


def format_duration(seconds: int):
    mins, sec = divmod(seconds, 60)
    hrs, mins = divmod(mins, 60)

    if hrs:
        return f"{hrs}h {mins}m {sec}s"
    elif mins:
        return f"{mins}m {sec}s"
    else:
        return f"{sec}s"


async def vc_raw_handler(client, update, users, chats):
    if not isinstance(update, UpdateGroupCallParticipants):
        return

    chat_id = update.chat_id
    if chat_id not in VC_LOGGER:
        return

    for p in update.participants:
        if not isinstance(p, GroupCallParticipant):
            continue

        user = users.get(p.user_id)
        if not user:
            continue

        user_link = f"[{user.first_name}](tg://user?id={user.id})"

        # 🔹 USER JOIN
        if not p.left:
            VC_JOIN_TIME[p.user_id] = int(time.time())

            await app.send_message(
                chat_id,
                f"""🤖 **ROOHI VC LOGGER**

#JoinVideoChat
👤 User : {user_link}
🆔 ID : `{user.id}`
"""
            )

        # 🔹 USER LEAVE
        else:
            join_time = VC_JOIN_TIME.pop(p.user_id, None)
            if not join_time:
                return

            duration = format_duration(int(time.time()) - join_time)

            await app.send_message(
                chat_id,
                f"""🤖 **ROOHI VC LOGGER**

#LeftVideoChat
👤 User : {user_link}
🆔 ID : `{user.id}`
⏱️ Time in VC : **{duration}**
"""
            )


def attach():
    for cli in [
        getattr(userbot, "one", None),
        getattr(userbot, "two", None),
        getattr(userbot, "three", None),
        getattr(userbot, "four", None),
        getattr(userbot, "five", None),
    ]:
        if cli:
            cli.add_handler(RawUpdateHandler(vc_raw_handler), group=0)