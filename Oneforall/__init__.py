from SafoneAPI import SafoneAPI

from Oneforall.core.bot import Hotty
from Oneforall.core.dir import dirr
from Oneforall.core.git import git
from Oneforall.core.userbot import Userbot
from Oneforall.misc import dbb, heroku

from .logging import LOGGER

dirr()
git()
dbb()
heroku()

app = Hotty()
userbot = Userbot()
api = SafoneAPI()


from .platforms import *

Apple = AppleAPI()
Carbon = CarbonAPI()
SoundCloud = SoundAPI()
Spotify = SpotifyAPI()
Resso = RessoAPI()
Telegram = TeleAPI()
YouTube = YouTubeAPI()

APP = "Raiden_Robot"  # connect music api key "Dont change it"
