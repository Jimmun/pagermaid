""" PagerMaid initialization. """

from sys import version_info, platform, path
from yaml import load, FullLoader
from shutil import copyfile
from redis import StrictRedis
from logging import getLogger, INFO, DEBUG, StreamHandler
from distutils2.util import strtobool
from coloredlogs import ColoredFormatter
from telethon import TelegramClient

working_dir = __path__[0]
logging_format = "%(levelname)s [%(asctime)s] [%(name)s] %(message)s"
config = None
help_messages = {}
logs = getLogger(__name__)
logging_handler = StreamHandler()
logging_handler.setFormatter(ColoredFormatter(logging_format))
logs.addHandler(logging_handler)
logs.setLevel(INFO)

try:
    config = load(open(r"config.yml"), Loader=FullLoader)
except FileNotFoundError:
    logs.fatal("Configuration file does not exist, generating new configuration file.")
    copyfile(f"{path}/assets/config.gen.yml", "config.yml")
    exit(1)

if strtobool(config['debug']):
    logs.setLevel(DEBUG)
else:
    logs.setLevel(INFO)

if platform == "linux" or platform == "linux2" or platform == "darwin" or platform == "freebsd7" \
        or platform == "freebsd8" or platform == "freebsdN" or platform == "openbsd6":
    logs.info(
        "Detected platform as " + platform + ", proceeding to early load process of PagerMaid."
    )
else:
    logs.error(
        "Your platform " + platform + " is not supported, please start PagerMaid on Linux or *BSD."
    )
    exit(1)

if version_info[0] < 3 or version_info[1] < 6:
    logs.error(
        "Please upgrade your python interpreter to at least version 3.6."
    )
    exit(1)

api_key = config['api_key']
api_hash = config['api_hash']
if api_key is None or api_hash is None:
    logs.info(
        "Please place a valid configuration file in the working directory."
    )
    exit(1)

bot = TelegramClient("pagermaid", api_key, api_hash, auto_reconnect=True)
redis = StrictRedis(host='localhost', port=6379, db=14)


async def log(message):
    if not strtobool(config['log']):
        return
    await bot.send_message(
        int(config['log_chatid']),
        message
    )
