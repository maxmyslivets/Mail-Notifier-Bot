import asyncio
import threading

from MailNotifierBot.logger import logger
from MailNotifierBot.database import create_database
from MailNotifierBot.email_cli.mail_read import MailReader
from MailNotifierBot.tg_bot.bot import TelegramBot
from config import TG_TOKEN


if __name__ == '__main__':
    try:
        logger.info("Mail Notifier Bot start")

        # Проверяем наличие базы данных. Если ее нет, то она создается
        create_database()

        # создаем экземпляр Telegram-бота
        bot = TelegramBot(TG_TOKEN)

        # запускаем MailReader в отдельном потоке
        mail_thread = threading.Thread(target=asyncio.run, args=(MailReader.run_mail_reader(bot),))
        mail_thread.start()

        # запускаем Telegram-бота
        bot.run_polling()

    except Exception as e:
        logger.error(f"Unhandled exception occurred. {e}")
