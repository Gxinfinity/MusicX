from Tune import app
from pyrogram import filters
import asyncio
import random
import os

FILE_PATH = os.path.join(os.path.dirname(__file__), "words.txt")
with open(FILE_PATH, "r") as f:
    WORDS = set(w.strip().lower() for w in f.readlines())

games = {}

# -------------------------------------------------------
# /join
# -------------------------------------------------------
@app.on_message(filters.command("join"))
async def join_game(_, message):
    chat_id = message.chat.id

    if chat_id not in games:
        games[chat_id] = {
            "players": [],
            "turn_index": 0,
            "mode": 3,
            "repeat": 0,
            "last_letter": random.choice("abcdefghijklmnopqrstuvwxyz"),
            "timeout_task": None,
            "active": False,
            "total_words": 0,
            "start_time": None,
            "longest_word": "",
            "initial_players": 0,
            "countdown": 60
        }

    game = games[chat_id]

    if game["active"]:
        return await message.reply("❌ Game already started, you cannot join now!")

    if message.from_user.id in game["players"]:
        return await message.reply("Already joined!")

    # Add user to game
    user = message.from_user
    mention = f"[{user.first_name}](tg://user?id={user.id})"

    game["players"].append(user.id)

    await message.reply(f"✔ {mention} joined the game!")

    
    # Start countdown only once
    if chat_id not in start_timers:
        start_timers[chat_id] = asyncio.create_task(start_countdown(chat_id, message))

# ============================
# AUTO START + REMINDER SYSTEM
# ============================

start_timers = {}   # each chat timer

async def start_countdown(chat_id, message):
    game = games[chat_id]
    game["countdown"] = 60       # default start time
    game["max_time"] = 150       # max limit

    while game["countdown"] > 0:
        # Reminders
        if game["countdown"] in [30, 15]:
            await message.reply(f"⏳ {game['countdown']} seconds left to join! Use /join")

        if game["countdown"] % 20 == 0:
            await message.reply(f"⌛ Game starting in {game['countdown']} seconds... /join fast!")

        await asyncio.sleep(1)
        game["countdown"] -= 1

        # Someone extended time?
        if game["countdown"] > game["max_time"]:
            game["countdown"] = game["max_time"]

    # TIME OVER
    if len(game["players"]) < 2:
        await message.reply("❌ Not enough players. Game cancelled.")
        games.pop(chat_id, None)
        return

    # AUTO START GAME
    await message.reply("🎮 Auto-starting game...")
    await auto_start_game(message)


async def auto_start_game(message):
    chat_id = message.chat.id
    game = games[chat_id]

    game["active"] = True
    game["mode"] = 3
    game["repeat"] = 0
    game["turn_index"] = 0
    game["total_words"] = 0
    game["last_letter"] = random.choice("abcdefghijklmnopqrstuvwxyz")
    game["initial_players"] = len(game["players"])
    game["start_time"] = asyncio.get_event_loop().time()

    await message.reply(
        f"🎮 Word Game Started!\n"
        f"➡ First letter: **{game['last_letter']}**\n"
        f"➡ Minimum letters: **{game['mode']}**"
    )

    await next_turn(message)
    
# -------------------------------------------------------
# /startgame
# -------------------------------------------------------
@app.on_message(filters.command("startgame"))
async def manual_start(_, message):
    chat_id = message.chat.id

    if chat_id not in games or len(games[chat_id]["players"]) < 2:
        return await message.reply("Need at least 2 players to start!")

    await auto_start_game(message)
# -------------------------------------------------------
# /stopgame
# -------------------------------------------------------
@app.on_message(filters.command("stopgame"))
async def stop_game(_, message):
    chat_id = message.chat.id

    if chat_id in games:
        if games[chat_id]["timeout_task"]:
            games[chat_id]["timeout_task"].cancel()
        del games[chat_id]

    await message.reply("🛑 Game stopped.")
    
# -------------------------------------------------------
# /extend
# -------------------------------------------------------
@app.on_message(filters.command("extend"))
async def extend_time(_, message):
    chat_id = message.chat.id

    if chat_id not in games:
        return await message.reply("No game lobby available to extend time!")

    game = games[chat_id]

    if game["active"]:
        return await message.reply("Game already started. Cannot extend time.")

    if game["countdown"] >= game["max_time"]:
        return await message.reply("⛔ Max time reached (150 sec)! Cannot extend more.")

    game["countdown"] += 30

    if game["countdown"] > game["max_time"]:
        game["countdown"] = game["max_time"]

    await message.reply(f"⏫ Time extended! New time: {game['countdown']} seconds.")

# -------------------------------------------------------
# NEXT TURN MESSAGE
# -------------------------------------------------------
async def next_turn(message):
    chat_id = message.chat.id
    game = games[chat_id]

    # Current turn player
    current_player_id = game["players"][game["turn_index"]]
    current_member = await app.get_chat_member(chat_id, current_player_id)
    current_mention = current_member.user.mention

    # Next turn player
    next_index = (game["turn_index"] + 1) % len(game["players"])
    next_player_id = game["players"][next_index]
    next_member = await app.get_chat_member(chat_id, next_player_id)
    next_mention = next_member.user.mention

    # TIME SETTINGS BY MODE
    time_map = {
        3: 40, 4: 35, 5: 30, 6: 30,
        7: 25, 8: 25, 9: 20, 10: 20
    }
    turn_time = time_map.get(game["mode"], 20)
    game["turn_time"] = turn_time  # store time for use in timeout()

    await message.reply(
        f"Turn: {current_mention} ⭐\n"
        f"(Next: {next_mention})\n"
        f"Your word must start with **{game['last_letter'].upper()}** "
        f"and include at least **{game['mode']} letters**.\n"
        f"You have {turn_time}s to answer.\n"
        f"Players remaining: {len(game['players'])}/{game['initial_players']}\n"
        f"Total words: {game['total_words']}"
    )

    # Start timeout task
    if game.get("timeout_task"):
        game["timeout_task"].cancel()

    game["timeout_task"] = asyncio.create_task(timeout(message))


async def timeout(message):
    chat_id = message.chat.id
    game = games[chat_id]
    turn_time = game["turn_time"]

    await asyncio.sleep(turn_time)

    # Remove the timed-out player
    kicked_id = game["players"].pop(game["turn_index"])
    kicked_member = await app.get_chat_member(chat_id, kicked_id)
    kicked_mention = kicked_member.user.mention

    await message.reply(f"{kicked_mention} ran out of time! They have been eliminated.")

    # Check if winner exists
    if len(game["players"]) == 1:
        winner_id = game["players"][0]
        winner_member = await app.get_chat_member(chat_id, winner_id)
        winner_mention = winner_member.user.mention

        total_players = game["initial_players"]
        total_words = game["total_words"]
        longest_word = game["longest_word"]

        # Game duration
        duration = int(asyncio.get_event_loop().time() - game["start_time"])
        h = duration // 3600
        m = (duration % 3600) // 60
        s = duration % 60

        await message.reply(
            f"🎉 {winner_mention} won the game out of {total_players} players!\n"
            f"🏆 Total words: {total_words}\n"
            f"🔠 Longest word: {longest_word}\n"
            f"⏳ Game length: {h:02}:{m:02}:{s:02}"
        )

        del games[chat_id]
        return

    # If not enough players
    if len(game["players"]) < 2:
        del games[chat_id]
        return await message.reply("Game ended — not enough players.")

    # Correct turn index
    game["turn_index"] %= len(game["players"])

    # Start next turn
    await next_turn(message)
# -------------------------------------------------------
# WORD INPUT HANDLING
# -------------------------------------------------------
@app.on_message(filters.text & ~filters.command([]))
async def game_turn(_, message):
    chat_id = message.chat.id

    if chat_id not in games:
        return

    game = games[chat_id]
    if not game["active"]:
        return

    player = game["players"][game["turn_index"]]
    if message.from_user.id != player:
        return

    word = message.text.lower()

    # Wrong starting letter
    if not word.startswith(game["last_letter"]):
        return await message.reply(f"{message.from_user.mention} ❌ Wrong starting letter!")

    # Word too short
    if len(word) < game["mode"]:
        return await message.reply(
            f"{message.from_user.mention} ❗ Word must be at least **{game['mode']}** letters!"
        )

    # Invalid word
    if word not in WORDS:
        return await message.reply(
            f"{message.from_user.mention} ❗ Not a valid English word!"
        )

    # -------------------------------------------------------
    # ACCEPTED WORD LOGIC (ALL FIXED HERE INSIDE FUNCTION)
    # -------------------------------------------------------

    game["last_letter"] = word[-1]
    game["total_words"] += 1

    # Update longest word
    if len(word) > len(game["longest_word"]):
        game["longest_word"] = word

    await message.reply(f"✔ `{word}` is accepted!")

    # Repeat level 3 times before increase
    if game["mode"] < 10:
        game["repeat"] += 1
        if game["repeat"] == 3:
            game["repeat"] = 0
            game["mode"] += 1

    if game["mode"] == 10:
        game["repeat"] = 0

    # Cancel old timeout
    if game["timeout_task"]:
        game["timeout_task"].cancel()

    # Next turn
    game["turn_index"] = (game["turn_index"] + 1) % len(game["players"])

    await next_turn(message)
