import time
import os
import asyncio


from loadenv import read_dotenv
from mail_notifier import MailNotifier


if __name__ == '__main__':

    read_dotenv('.env')

    mail_notifier = MailNotifier(os.getenv("MAIL_USER"), os.getenv("MAIL_PASSWORD"))

    while True:
        asyncio.run(mail_notifier.check_for_new_message())
        time.sleep(20)
