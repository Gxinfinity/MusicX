from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultPhoto,
)
from youtubesearchpython.__future__ import VideosSearch

from config import BANNED_USERS
from Oneforall import app


@app.on_inline_query(~BANNED_USERS)
async def inline_query_handler(client, query):
    text = query.query.strip()
    answers = []

    # 🔹 Empty query safe handle
    if not text:
        return await client.answer_inline_query(
            query.id,
            results=[],
            cache_time=5
        )

    search = VideosSearch(text, limit=20)
    results = (await search.next()).get("result", [])

    # 🔹 Safe loop (no IndexError)
    for result in results[:15]:
        title = result["title"].title()
        duration = result.get("duration", "N/A")
        views = result["viewCount"]["short"]
        thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        channellink = result["channel"]["link"]
        channel = result["channel"]["name"]
        link = result["link"]
        published = result.get("publishedTime", "N/A")

        description = f"{views} | {duration} | {channel} | {published}"

        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="ʏᴏᴜᴛᴜʙᴇ 🎄",
                        url=link
                    )
                ]
            ]
        )

        caption = f"""
❄ <b>ᴛɪᴛʟᴇ :</b> <a href="{link}">{title}</a>

⏳ <b>ᴅᴜʀᴀᴛɪᴏɴ :</b> {duration}
👀 <b>ᴠɪᴇᴡs :</b> <code>{views}</code>
🎥 <b>ᴄʜᴀɴɴᴇʟ :</b> <a href="{channellink}">{channel}</a>
⏰ <b>ᴘᴜʙʟɪsʜᴇᴅ ᴏɴ :</b> {published}

<u><b>➻ ɪɴʟɪɴᴇ sᴇᴀʀᴄʜ ʙʏ {app.name}</b></u>
"""

        answers.append(
            InlineQueryResultPhoto(
                photo_url=thumbnail,
                thumb_url=thumbnail,
                title=title,
                description=description,
                caption=caption,
                reply_markup=buttons,
            )
        )

    # 🔹 Final safe answer
    try:
        await client.answer_inline_query(
            query.id,
            results=answers,
            cache_time=10
        )
    except Exception as e:
        print(f"Inline error: {e}")