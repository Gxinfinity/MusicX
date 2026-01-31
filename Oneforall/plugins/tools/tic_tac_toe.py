from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from Oneforall import app
from Oneforall.core.mongo import mongodb

games = {}
db = mongodb.xoxo_leaderboard

EMPTY = "⬜"
X = "❌"
O = "⭕"

WIN = [
    [0,1,2],[3,4,5],[6,7,8],
    [0,3,6],[1,4,7],[2,5,8]
]

# ───── HELPERS ─────

def check(board):
    for a,b,c in WIN:
        if board[a] == board[b] == board[c] != EMPTY:
            return board[a]
    if EMPTY not in board:
        return "draw"
    return None

def board_kb(gid, board):
    rows = []
    for i in range(0,9,3):
        rows.append([
            InlineKeyboardButton(board[i], callback_data=f"xoxo:{gid}:{i}"),
            InlineKeyboardButton(board[i+1], callback_data=f"xoxo:{gid}:{i+1}"),
            InlineKeyboardButton(board[i+2], callback_data=f"xoxo:{gid}:{i+2}")
        ])
    rows.append([
        InlineKeyboardButton("🔁 Rematch", callback_data=f"xoxo_rematch:{gid}"),
        InlineKeyboardButton("🛑 End Game", callback_data=f"xoxo_end:{gid}")
    ])
    return InlineKeyboardMarkup(rows)

async def get_name(uid):
    if uid == 0:
        return "🤖 <b>Bot</b>"
    user = await app.get_users(uid)
    return user.mention

async def add_win(uid):
    if uid == 0:
        return
    await db.update_one(
        {"user_id": uid},
        {"$inc": {"wins": 1}},
        upsert=True
    )

# ───── /game MENU ─────

@app.on_message(filters.command("game"))
async def game_menu(_, m):
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("❌⭕ Tic Tac Toe", callback_data="game_xoxo")]
    ])
    await m.reply(
        "🎮 <b>Game Center</b>\n\nChoose a game:",
        reply_markup=kb
    )

@app.on_callback_query(filters.regex("^game_xoxo$"))
async def game_xoxo(_, q: CallbackQuery):
    fake = type("obj", (), {"chat": q.message.chat, "from_user": q.from_user})
    await start_xoxo(_, fake)

# ───── /xoxo START ─────

@app.on_message(filters.command("xoxo"))
async def start_xoxo(_, m):
    gid = m.chat.id

    if gid in games:
        return await m.reply("⚠️ <b>A game is already running!</b>\nUse 🛑 End Game.")

    games[gid] = {
        "board": [EMPTY]*9,
        "p1": m.from_user.id,
        "p2": None,
        "turn": X,
        "mode": "friend"
    }

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("👥 Join Game", callback_data=f"xoxo_join:{gid}")],
        [InlineKeyboardButton("🤖 Play vs Bot", callback_data=f"xoxo_bot:{gid}")]
    ])

    await m.reply(
        f"❌⭕ <b>Tic Tac Toe</b>\n\n"
        f"👤 <b>Player 1:</b> {m.from_user.mention}\n\n"
        f"Choose mode:",
        reply_markup=kb
    )

# ───── JOIN FRIEND ─────

@app.on_callback_query(filters.regex("^xoxo_join"))
async def join(_, q: CallbackQuery):
    gid = int(q.data.split(":")[1])
    g = games.get(gid)

    if not g or g["p2"]:
        return await q.answer("Game already started")

    if q.from_user.id == g["p1"]:
        return await q.answer("You are Player 1")

    g["p2"] = q.from_user.id

    p1 = await get_name(g["p1"])
    p2 = await get_name(g["p2"])

    await q.message.edit_text(
        f"🎮 <b>Game Started!</b>\n\n"
        f"❌ {p1}\n"
        f"⭕ {p2}\n\n"
        f"🔄 <b>Turn:</b> ❌",
        reply_markup=board_kb(gid, g["board"])
    )

# ───── BOT MODE ─────

@app.on_callback_query(filters.regex("^xoxo_bot"))
async def bot(_, q: CallbackQuery):
    gid = int(q.data.split(":")[1])
    g = games[gid]

    g["p2"] = 0
    g["mode"] = "bot"

    p1 = await get_name(g["p1"])

    await q.message.edit_text(
        f"🤖 <b>Bot Mode</b>\n\n"
        f"❌ {p1}\n"
        f"⭕ 🤖 <b>Bot</b>\n\n"
        f"🔄 <b>Your Turn:</b> ❌",
        reply_markup=board_kb(gid, g["board"])
    )

# ───── MOVE ─────

@app.on_callback_query(filters.regex("^xoxo:"))
async def move(_, q: CallbackQuery):
    _, gid, pos = q.data.split(":")
    gid, pos = int(gid), int(pos)
    g = games.get(gid)

    if not g or g["board"][pos] != EMPTY:
        return

    uid = q.from_user.id

    if g["turn"] == X and uid != g["p1"]:
        return await q.answer("Not your turn")
    if g["turn"] == O and g["mode"] == "friend" and uid != g["p2"]:
        return await q.answer("Not your turn")

    g["board"][pos] = g["turn"]
    res = check(g["board"])

    p1 = await get_name(g["p1"])
    p2 = await get_name(g["p2"])

    if res:
        winner = g["p1"] if res == X else g["p2"]
        await add_win(winner)
        games.pop(gid)

        return await q.message.edit_text(
            f"🏆 <b>Winner!</b>\n\n"
            f"{p1} vs {p2}\n\n"
            f"🎉 <b>{res} wins the match!</b>",
            reply_markup=board_kb(gid, g["board"])
        )

    g["turn"] = O if g["turn"] == X else X

    await q.message.edit_text(
        f"❌ {p1}\n⭕ {p2}\n\n"
        f"🔄 <b>Turn:</b> {g['turn']}",
        reply_markup=board_kb(gid, g["board"])
    )

# ───── REMATCH ─────

@app.on_callback_query(filters.regex("^xoxo_rematch"))
async def rematch(_, q: CallbackQuery):
    gid = int(q.data.split(":")[1])
    if gid not in games:
        return

    games[gid]["board"] = [EMPTY]*9
    games[gid]["turn"] = X

    await q.message.edit_text(
        "🔁 <b>Rematch Started!</b>\n\n🔄 Turn: ❌",
        reply_markup=board_kb(gid, games[gid]["board"])
    )

# ───── END GAME ─────

@app.on_callback_query(filters.regex("^xoxo_end"))
async def end(_, q: CallbackQuery):
    gid = int(q.data.split(":")[1])
    games.pop(gid, None)
    await q.message.edit_text("🛑 <b>Game Ended</b>")

# ───── LEADERBOARD ─────

@app.on_message(filters.command("xoxotop"))
async def top(_, m):
    text = "🏆 <b>XOXO Leaderboard</b>\n\n"
    i = 1
    async for u in db.find().sort("wins", -1).limit(10):
        user = await app.get_users(u["user_id"])
        text += f"{i}. {user.mention} — {u['wins']} wins\n"
        i += 1
    await m.reply(text)