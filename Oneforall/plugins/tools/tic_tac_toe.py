# ─────────────────────────────────────────────
# Tic Tac Toe (XOXO) Game
# Friend vs Friend & Friend vs Bot
# ─────────────────────────────────────────────

from pyrogram import filters
from pyrogram.types import Message
from Oneforall import app

games = {}  # chat_id -> game state

WIN = [
    [0,1,2],[3,4,5],[6,7,8],
    [0,3,6],[1,4,7],[2,5,8],
    [0,4,8],[2,4,6]
]

def render(board):
    return "\n".join([
        " | ".join(board[i:i+3]) for i in range(0,9,3)
    ])

def check_winner(board):
    for a,b,c in WIN:
        if board[a] == board[b] == board[c] != "⬜":
            return board[a]
    if "⬜" not in board:
        return "draw"
    return None

# ───────── START GAME ─────────

@app.on_message(filters.command("tictactoe", prefixes=["/", "!", "."]))
async def start_game(_, m: Message):
    args = m.text.split()

    if len(args) < 2:
        return await m.reply(
            "**Usage:**\n"
            "`/tictactoe bot`  → Play with bot\n"
            "`/tictactoe friend` → Play with friend"
        )

    mode = args[1].lower()
    chat_id = m.chat.id

    board = ["⬜"] * 9

    games[chat_id] = {
        "board": board,
        "turn": "❌",
        "mode": mode,
        "players": [m.from_user.id],
    }

    if mode == "friend":
        games[chat_id]["players"].append(None)
        await m.reply(
            "**🎮 Tic Tac Toe Started (Friend Mode)**\n"
            "Second player type `/join`\n\n"
            f"{render(board)}"
        )
    else:
        await m.reply(
            "**🤖 Tic Tac Toe Started (Bot Mode)**\n\n"
            f"{render(board)}\n\n"
            "Use `/move 1-9`"
        )

# ───────── JOIN FRIEND ─────────

@app.on_message(filters.command("join", prefixes=["/", "!", "."]))
async def join_game(_, m: Message):
    chat_id = m.chat.id
    game = games.get(chat_id)

    if not game or game["mode"] != "friend":
        return

    if game["players"][1] is None:
        game["players"][1] = m.from_user.id
        await m.reply(
            "**✅ Player Joined**\n\n"
            f"{render(game['board'])}\n\n"
            "❌ Turn"
        )

# ───────── PLAYER MOVE ─────────

@app.on_message(filters.command("move", prefixes=["/", "!", "."]))
async def player_move(_, m: Message):
    chat_id = m.chat.id
    game = games.get(chat_id)

    if not game:
        return

    try:
        pos = int(m.text.split()[1]) - 1
    except:
        return await m.reply("Use `/move 1-9`")

    if pos < 0 or pos > 8 or game["board"][pos] != "⬜":
        return await m.reply("❌ Invalid move")

    uid = m.from_user.id
    turn = game["turn"]

    # Check turn
    if game["mode"] == "friend":
        p1, p2 = game["players"]
        if (turn == "❌" and uid != p1) or (turn == "⭕" and uid != p2):
            return
    else:
        if uid != game["players"][0]:
            return

    game["board"][pos] = turn
    winner = check_winner(game["board"])

    if winner:
        del games[chat_id]
        if winner == "draw":
            return await m.reply(f"🤝 **Draw!**\n\n{render(game['board'])}")
        return await m.reply(f"🏆 **{winner} Wins!**\n\n{render(game['board'])}")

    # Switch turn
    game["turn"] = "⭕" if turn == "❌" else "❌"

    # Bot Move
    if game["mode"] == "bot" and game["turn"] == "⭕":
        for i in range(9):
            if game["board"][i] == "⬜":
                game["board"][i] = "⭕"
                break

        winner = check_winner(game["board"])
        if winner:
            del games[chat_id]
            return await m.reply(f"🏆 **{winner} Wins!**\n\n{render(game['board'])}")

        game["turn"] = "❌"

    await m.reply(render(game["board"]))

# ───────── END GAME ─────────

@app.on_message(filters.command("endgame", prefixes=["/", "!", "."]))
async def end_game(_, m: Message):
    if games.pop(m.chat.id, None):
        await m.reply("🛑 **Game Ended**")