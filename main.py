import time
import os
import asyncio
import threading


from py_dotenv import read_dotenv
from mail_notifier import MailNotifier
from bot import TelegramBot


# функция для запуска MailNotifier в отдельном потоке
async def run_mail_notifier():
    while True:
        async with MailNotifier(os.getenv("MAIL_USER"), os.getenv("MAIL_PASSWORD")) as mail_notifier:
            await mail_notifier.check_for_new_message(bot.send_message)
        time.sleep(60)


if __name__ == '__main__':

    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    read_dotenv(dotenv_path)

    bot = TelegramBot()

    # запускаем MailNotifier в отдельном потоке
    mail_thread = threading.Thread(target=asyncio.run, args=(run_mail_notifier(),))
    mail_thread.start()

    # запускаем TelegramBot
    bot.run_polling()
