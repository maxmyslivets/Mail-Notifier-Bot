import os

from py_dotenv import read_dotenv

import logging


logger = logging.getLogger("MailNotifierBot")
try:
    read_dotenv(".env")
    logger.debug("Done setting")
except Exception as e:
    logger.error(f"Error {e.args[0]} occurred while setting variably.")

TG_TOKEN = os.getenv("TG_TOKEN")
MAIL_SERVER = os.getenv("MAIL_SERVER")
MAIL_USER = os.getenv("MAIL_USER")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")

INTERVAL = 5
DATABASE = "read_messages.sqlite"
LOG = "MailNotifierBot.log"
