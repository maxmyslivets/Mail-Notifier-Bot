import os
import telebot
from telebot.types import Message


class TelegramBot:

    def __init__(self):
        self.token = os.getenv("TG_TOKEN")
        self.bot = telebot.TeleBot(self.token)

    def send_message(self, text: str):
        self.bot.send_message(os.getenv("TG_CHAT_ID"), text)

    def listen_for_messages(self):
        @self.bot.message_handler(commands=['start'])
        def handle_start(message: Message):
            self.bot.send_message(message.chat.id, f"Привет! Я бот для обработки почты.\nchat-id: {message.chat.id}")

        @self.bot.message_handler(func=lambda message: True)
        def handle_message(message: Message):
            if message.text.startswith('@'+os.getenv("TG_BOT_NAME")):
                self.bot.send_message(message.chat.id, "Бот временно не обрабатывает входящие запросы.")

        self.bot.polling(none_stop=True)

    def run_polling(self):
        self.listen_for_messages()
