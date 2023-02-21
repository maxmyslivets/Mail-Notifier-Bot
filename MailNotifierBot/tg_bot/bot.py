import asyncio
import os
import threading

import telebot
from telebot.types import Message, CallbackQuery

from MailNotifierBot.database import get_id_message
from MailNotifierBot.logger import logger
from MailNotifierBot.email_cli.mail_read import MailReader
from config import MAIL_SERVER, MAIL_USER, MAIL_PASSWORD


class TelegramBot:

    is_connected: bool = False

    def __init__(self, token):
        logger.debug("Create bot")
        self.bot = telebot.TeleBot(token)

    def send_message(self, text: str, attachments: list[str]) -> int:
        try:
            if os.getenv("TG_CHAT_ID") is not None:
                logger.info("Send new message")
                markup = telebot.types.InlineKeyboardMarkup()
                for i, label in enumerate(attachments):
                    attachment_id = str(i)
                    callback_data = f"download_{attachment_id}"
                    markup.add(
                        telebot.types.InlineKeyboardButton(text=f"\U0001F4CE {label}", callback_data=callback_data))
                msg = self.bot.send_message(os.getenv("TG_CHAT_ID"), text, parse_mode="HTML", reply_markup=markup)
                return msg.id
        except Exception:
            logger.error(f"Error occurred while sending message")
            raise "Error occurred while sending message"

    def send_document(self, reply_id: int, attachments: list) -> None:
        for attachment in attachments:
            logger.info("Send attachment")
            self.bot.send_document(os.getenv("TG_CHAT_ID"),
                                   document=attachment[1], visible_file_name=attachment[0],
                                   reply_to_message_id=reply_id)

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

            @self.bot.callback_query_handler(func=lambda call: True)
            def handle_button_click(call: CallbackQuery):
                msg_id = call.message.id
                attachment_id = call.data.split('_')[-1]
                email_message_id = get_id_message(msg_id)
                self.handle_button_click(msg_id, email_message_id, attachment_id)

        except Exception:
            logger.error(f"Error occurred while listening for commands")

    def handle_button_click(self, msg_id, email_message_id, attachment_id):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.async_handle_button_click(msg_id, email_message_id, attachment_id))

    async def async_handle_button_click(self, msg_id, email_message_id, attachment_id):
        async with MailReader(MAIL_SERVER, MAIL_USER, MAIL_PASSWORD) as mail_reader:
            attachments = mail_reader.get_attachments(email_message_id)
            attachment = attachments[int(attachment_id)]
            self.send_document(msg_id, [attachment])

    def run_polling(self):
        try:
            logger.info("Run Telegram-bot")
            self.listen_for_commands()
            self.bot.polling(none_stop=True)
        except Exception:
            logger.error(f"Error occurred while running polling")
