import time
import os
import asyncio
import threading


from loadenv import read_dotenv
from mail_notifier import MailNotifier
from bot import TelegramBot


if __name__ == '__main__':

    read_dotenv('.env')

    bot = TelegramBot()
    mail_notifier = MailNotifier(os.getenv("MAIL_USER"), os.getenv("MAIL_PASSWORD"))

    # функция для запуска MailNotifier в отдельном потоке
    def run_mail_notifier():
        while True:
            asyncio.run(mail_notifier.check_for_new_message(bot.send_message))
            time.sleep(20)

    # запускаем MailNotifier в отдельном потоке
    mail_thread = threading.Thread(target=run_mail_notifier)
    mail_thread.start()

    # запускаем TelegramBot
    bot.run_polling()
