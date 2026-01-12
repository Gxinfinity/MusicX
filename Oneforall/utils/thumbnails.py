import os
import random
import re

import aiofiles
import aiohttp
from PIL import (
    Image,
    ImageEnhance,
    ImageOps,
    ImageDraw,
    ImageFont,
    ImageFilter,
)
from youtubesearchpython.__future__ import VideosSearch

from config import YOUTUBE_IMG_URL


def changeImageSize(maxWidth, maxHeight, image):
    return image.resize((maxWidth, maxHeight), Image.LANCZOS)


def clear(text):
    words = text.split()
    title = ""
    for w in words:
        if len(title) + len(w) < 60:
            title += " " + w
    return title.strip()


async def get_thumb(videoid):
    final = f"cache/{videoid}.png"
    temp = f"cache/thumb{videoid}.png"

    if os.path.isfile(final):
        return final

    try:
        search = VideosSearch(
            f"https://www.youtube.com/watch?v={videoid}", limit=1
        )
        result = (await search.next())["result"][0]

        title = clear(
            re.sub(r"\W+", " ", result.get("title", "Unsupported Title")).title()
        )
        duration = result.get("duration", "LIVE")
        channel = result.get("channel", {}).get("name", "Unknown Channel")
        thumbnail = result["thumbnails"][-1]["url"].split("?")[0]

        # download thumbnail
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    async with aiofiles.open(temp, "wb") as f:
                        await f.write(await resp.read())

        base = Image.open(temp).convert("RGB")

        # ===== BACKGROUND =====
        bg = changeImageSize(1280, 720, base)
        bg = bg.filter(ImageFilter.GaussianBlur(22))
        bg = ImageEnhance.Brightness(bg).enhance(0.55)

        overlay = Image.new("RGBA", bg.size, (0, 0, 0, 170))
        bg = Image.alpha_composite(bg.convert("RGBA"), overlay)

        # ===== FOREGROUND CARD =====
        fg = changeImageSize(720, 405, base)
        fg = ImageEnhance.Sharpness(fg).enhance(1.4)

        mask = Image.new("L", fg.size, 0)
        mdraw = ImageDraw.Draw(mask)
        mdraw.rounded_rectangle(
            [(0, 0), fg.size], radius=30, fill=255
        )

        card = Image.new("RGBA", fg.size)
        card.paste(fg, (0, 0), mask)

        shadow = Image.new("RGBA", fg.size, (0, 0, 0, 180))
        shadow = shadow.filter(ImageFilter.GaussianBlur(25))

        cx = (1280 - fg.width) // 2
        cy = 100

        bg.paste(shadow, (cx + 12, cy + 18), shadow)
        bg.paste(card, (cx, cy), card)

        draw = ImageDraw.Draw(bg)

        # ===== PROGRESS BAR =====
        bar_y = cy + fg.height - 12
        draw.line(
            [(cx + 40, bar_y), (cx + 240, bar_y)],
            fill=(255, 60, 150),
            width=6,
        )

        # ===== TEXT =====
        try:
            title_font = ImageFont.truetype("Tune/assets/font.ttf", 42)
            small_font = ImageFont.truetype("Tune/assets/font2.ttf", 28)
        except:
            title_font = small_font = ImageFont.load_default()

        draw.text(
            (cx, cy + fg.height + 40),
            title,
            font=title_font,
            fill="white",
        )

        draw.text(
            (cx, cy + fg.height + 95),
            f"{channel} • {duration}",
            font=small_font,
            fill=(190, 190, 190),
        )

        # ===== POWERED BY =====
        power = "˹ ROOHI MUSIC "
        pw = draw.textlength(power, small_font)
        px = (1280 - pw) // 2

        draw.text(
            (px, 650),
            power,
            font=small_font,
            fill=(255, 80, 170),
        )

        try:
            os.remove(temp)
        except:
            pass

        bg.convert("RGB").save(final, "PNG", quality=95)
        return final

    except Exception as e:
        print("THUMB ERROR:", e)
        return YOUTUBE_IMG_URL
