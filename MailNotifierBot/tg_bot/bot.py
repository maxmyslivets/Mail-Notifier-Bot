import os

import telebot
from telebot.types import Message

from MailNotifierBot.logger import logger


class TelegramBot:

    is_connected: bool = False

    def __init__(self, token):
        logger.debug("Create bot")
        self.bot = telebot.TeleBot(token)

    def send_message(self, text: str, attachments: list[str]) -> int:
        try:
            if os.getenv("TG_CHAT_ID") is not None:
                logger.info("Send new message")
                msg = self.bot.send_message(os.getenv("TG_CHAT_ID"), text, parse_mode="HTML")
                # fixme: Под сообщением должны быть кнопки с названиями вложений из `attachments`
                return msg.id
        except Exception:
            logger.error(f"Error occurred while sending message")

    def listen_for_commands(self):
        try:
            @self.bot.message_handler(commands=['start'])
            def handle_start(message: Message):
                logger.info("User command /start")
                chat_id = os.getenv("TG_CHAT_ID")
                if chat_id is None:
                    logger.info("Initial bot in chat")
                    os.environ.setdefault('TG_CHAT_ID', str(message.chat.id))
                    self.is_connected = True
                    self.bot.send_message(message.chat.id,
                                          "Привет! Я Telegram-бот, который отправляет уведомления о новых электронных "
                                          "письмах, полученных на заданный почтовый ящик.\nЭто быстрый и удобный способ "
                                          "получать уведомления о новых письмах без необходимости постоянно проверять "
                                          "почтовый ящик вручную.")
                else:
                    self.bot.send_message(message.chat.id, "Бот уже подключен к чату.")
        except Exception:
            logger.error(f"Error occurred while listening for commands")

    def run_polling(self):
        try:
            logger.info("Run Telegram-bot")
            self.listen_for_commands()
            self.bot.polling(none_stop=True)
        except Exception:
            logger.error(f"Error occurred while running polling")
