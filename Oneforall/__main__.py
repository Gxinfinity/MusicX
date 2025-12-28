import asyncio
import importlib
from pyrogram import idle
from pytgcalls.exceptions import NoActiveGroupCall

import config
from config import BANNED_USERS
from Oneforall import LOGGER, app, userbot
from Oneforall.core.call import Hotty
from Oneforall.misc import sudo
from Oneforall.plugins import ALL_MODULES
from Oneforall.utils.database import get_banned_users, get_gbanned


async def init():
    if (
        not config.STRING1
        and not config.STRING2
        and not config.STRING3
        and not config.STRING4
        and not config.STRING5
    ):
        LOGGER(__name__).error("Assistant client variables not defined, exiting...")
        exit()

    await sudo()

    try:
        users = await get_gbanned()
        for user_id in users:
            BANNED_USERS.add(user_id)
        users = await get_banned_users()
        for user_id in users:
            BANNED_USERS.add(user_id)
    except:
        pass

    # 🔹 Start bot
    await app.start()

    # 🔹 Load plugins
    for module in ALL_MODULES:
        try:
            module_name = module.lstrip(".")
            importlib.import_module(f"Oneforall.plugins.{module_name}")
        except Exception as e:
            LOGGER(__name__).error(f"Failed to import plugin {module}: {e}")

    LOGGER("Oneforall.plugins").info("Successfully Imported Modules...")

    # 🔹 Start assistants
    await userbot.start()

    
    # 🔹 Start VC player
    await Hotty.start()

    try:
        await Hotty.stream_call(
            "https://graph.org/file/e999c40cb700e7c684b75.mp4"
        )
    except NoActiveGroupCall:
        LOGGER("Oneforall").error(
            "Please turn on the videochat of your log group/channel.\n\nStopping Bot..."
        )
        exit()
    except:
        pass

    await Hotty.decorators()

    LOGGER("Oneforall").info("Bot started successfully.")

    await idle()
    await app.stop()
    await userbot.stop()
    LOGGER("Oneforall").info("Stopping One for all Bot...")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(init())