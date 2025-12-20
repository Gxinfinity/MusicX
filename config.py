import os
import re
from os import getenv

from dotenv import load_dotenv
from pyrogram import filters

load_dotenv()

# Get this value from my.telegram.org/apps
API_ID = int(getenv("API_ID", "26950458"))
API_HASH = getenv("API_HASH", "d818b8d530e4a9b209509815ab1b9c7c")

# Get your token from @BotFather on Telegram.
BOT_TOKEN = getenv("BOT_TOKEN","")

# OpenAI Token
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Get your mongo url from cloud.mongodb.com
MONGO_DB_URI = getenv("MONGO_DB_URI", "mongodb+srv://knight4563:knight4563@cluster0.a5br0se.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
MUSIC_BOT_NAME = getenv("MUSIC_BOT_NAME", "Roohi_Queen_Bot")
PRIVATE_BOT_MODE = getenv("PRIVATE_BOT_MODE", None)

DURATION_LIMIT_MIN = int(getenv("DURATION_LIMIT", 100000))

# Chat id of a group for logging bot's activities
LOGGER_ID = int(getenv("LOGGER_ID", -1002869205475))

# Get this value from @BRANDRD_ROBOT on Telegram by /id
OWNER_ID = int(getenv("OWNER_ID", "8442486781"))
SUDO_USERS = list(map(int, getenv("SUDO_USERS", "7487670897").split()))

## Fill these variables if you're deploying on heroku.
# Your heroku app name
HEROKU_APP_NAME = getenv("HEROKU_APP_NAME")
# Get it from http://dashboard.heroku.com/account
HEROKU_API_KEY = getenv("HEROKU_API_KEY")

UPSTREAM_REPO = getenv(
    "UPSTREAM_REPO",
    "https://github.com/Gxtoxic4563/Roohi",
)
UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH", "main")
GIT_TOKEN = getenv(
    "GIT_TOKEN", None
)  # Fill this variable if your upstream repository is private

SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/dark_x_knight_musiczz_support/112")
SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/cuties_logs")

# Set this to True if you want the assistant to automatically leave chats after an interval
AUTO_LEAVING_ASSISTANT = bool(getenv("AUTO_LEAVING_ASSISTANT", False))

# Auto Gcast/Broadcast Handler (True = broadcast on , False = broadcast off During Hosting, Dont Do anything here.)
AUTO_GCAST = os.getenv("AUTO_GCAST")

# Auto Broadcast Message That You Want Use In Auto Broadcast In All Groups.
AUTO_GCAST_MSG = getenv("AUTO_GCAST_MSG", "")

# Get this credentials from https://developer.spotify.com/dashboard
SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID", "6fb7e1766693439b86ec57e3deb3c36f")
SPOTIFY_CLIENT_SECRET = getenv(
    "SPOTIFY_CLIENT_SECRET", "da3f94c6a68d49f6b64a7216ec9eb905"
)


# Maximum limit for fetching playlist's track from youtube, spotify, apple links.
SERVER_PLAYLIST_LIMIT = int(getenv("SERVER_PLAYLIST_LIMIT", "1000"))
PLAYLIST_FETCH_LIMIT = int(getenv("PLAYLIST_FETCH_LIMIT", "1000"))

SONG_DOWNLOAD_DURATION = int(getenv("SONG_DOWNLOAD_DURATION_LIMIT", "180"))
SONG_DOWNLOAD_DURATION_LIMIT = int(getenv("SONG_DOWNLOAD_DURATION_LIMIT", "2000"))

# Telegram audio and video file size limit (in bytes)
TG_AUDIO_FILESIZE_LIMIT = int(getenv("TG_AUDIO_FILESIZE_LIMIT", 104857600))
TG_VIDEO_FILESIZE_LIMIT = int(getenv("TG_VIDEO_FILESIZE_LIMIT", 1073741824))
# Checkout https://www.gbmb.org/mb-to-bytes for converting mb to bytes


# Get your pyrogram v2 session from @BRANDEDSTRINGSESSION_BOT on Telegram
STRING1 = getenv("STRING_SESSION",  "")
STRING2 = getenv("STRING_SESSION2", None)
STRING3 = getenv("STRING_SESSION3", None)
STRING4 = getenv("STRING_SESSION4", None)
STRING5 = getenv("STRING_SESSION5", None)


BANNED_USERS = filters.user()
TEMP_DB_FOLDER = "tempdb"
adminlist = {}
lyrical = {}
votemode = {}
autoclean = []
confirmer = {}


START_IMG_URL = getenv("START_IMG_URL", "https://graph.org/file/7c703f3d157b477bd5879-4463312df2304b779f.jpg")
PING_IMG_URL = getenv("PING_IMG_URL", "https://graph.org/file/7c703f3d157b477bd5879-4463312df2304b779f.jpg")
PLAYLIST_IMG_URL = "https://graph.org/file/7c703f3d157b477bd5879-4463312df2304b779f.jpg"
STATS_IMG_URL = "https://graph.org/file/7c703f3d157b477bd5879-4463312df2304b779f.jpg"
TELEGRAM_AUDIO_URL = "https://graph.org/file/7c703f3d157b477bd5879-4463312df2304b779f.jpg"
TELEGRAM_VIDEO_URL = "https://graph.org/file/7c703f3d157b477bd5879-4463312df2304b779f.jpg"
STREAM_IMG_URL = "https://graph.org/file/7c703f3d157b477bd5879-4463312df2304b779f.jpg"
SOUNCLOUD_IMG_URL = "https://graph.org/file/7c703f3d157b477bd5879-4463312df2304b779f.jpg"
YOUTUBE_IMG_URL = "https://graph.org/file/7c703f3d157b477bd5879-4463312df2304b779f.jpg"
SPOTIFY_ARTIST_IMG_URL = "https://graph.org/file/7c703f3d157b477bd5879-4463312df2304b779f.jpg"
SPOTIFY_ALBUM_IMG_URL = "https://graph.org/file/7c703f3d157b477bd5879-4463312df2304b779f.jpg"
SPOTIFY_PLAYLIST_IMG_URL = "https://graph.org/file/7c703f3d157b477bd5879-4463312df2304b779f.jpg"


def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60**i for i, x in enumerate(reversed(stringt.split(":"))))


DURATION_LIMIT = int(time_to_seconds(f"{DURATION_LIMIT_MIN}:00"))

if SUPPORT_CHANNEL:
    if not re.match("(?:http|https)://", SUPPORT_CHANNEL):
        raise SystemExit(
            "[ERROR] - Your SUPPORT_CHANNEL url is wrong. Please ensure that it starts with https://"
        )

if SUPPORT_CHAT:
    if not re.match("(?:http|https)://", SUPPORT_CHAT):
        raise SystemExit(
            "[ERROR] - Your SUPPORT_CHAT url is wrong. Please ensure that it starts with https://"
        )