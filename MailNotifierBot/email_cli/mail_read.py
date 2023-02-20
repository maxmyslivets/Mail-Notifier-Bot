import imaplib
import asyncio
import threading
import traceback

from email import message_from_bytes

from config import MAIL_SERVER, MAIL_USER, MAIL_PASSWORD, INTERVAL
from MailNotifierBot.email_cli.mail_processor import Message
from MailNotifierBot.database import check_read_messages, set_read_messages
from MailNotifierBot.logger import logger


class MailReader:
    """
Класс MailReader предназначен для подключения к почтовому серверу, получения новых непрочитанных сообщений и передачи
их описания в функцию-обработчик. Класс содержит методы для проверки наличия новых сообщений, а также для запуска
MailReader в отдельном потоке.

Атрибуты:

mail: объект IMAP-сервера для работы с почтой

mail_server: строка с адресом почтового сервера

mail_credentials: кортеж, содержащий имя пользователя и пароль для доступа к почтовому ящику

Методы:

__init__(self, server: str, mail: str, password: str) -> None: конструктор класса, инициализирует атрибуты класса

__aenter__(self): метод для входа в контекстный менеджер, создает подключение к IMAP-серверу

__aexit__(self, exc_type, exc_val, exc_tb): метод для выхода из контекстного менеджера, закрывает подключение
к IMAP-серверу

check_for_new_message(self, func) -> None: метод для проверки наличия новых непрочитанных сообщений на сервере и
передачи их описания в функцию-обработчик func

run_mail_reader(bot): статический метод для запуска MailReader в отдельном потоке
    """

    def __init__(self, server: str, mail: str, password: str) -> None:
        """
        конструктор класса, инициализирует атрибуты класса

        :param server:
        :param mail:
        :param password:
        """

        self.mail = imaplib.IMAP4_SSL(server)
        self.mail_credentials = (mail, password)

    async def __aenter__(self):
        """
        метод для входа в контекстный менеджер, создает подключение к IMAP-серверу

        :return:
        """

        try:
            logger.debug(f"Authorization {self.mail_credentials[0]}")
            self.mail.login(*self.mail_credentials)
            self.mail.select("inbox")
            return self
        except Exception:
            logger.error(f"Failed to connect to mail server")
            raise

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        метод для выхода из контекстного менеджера, закрывает подключение к IMAP-серверу

        :param exc_type:
        :param exc_val:
        :param exc_tb:
        :return:
        """

        try:
            logger.debug(f"Close connection with mail server")
            self.mail.close()
            self.mail.logout()
        except Exception:
            logger.error(f"Failed to close connect to mail server")
            raise

    def __enter__(self):
        # синхронный метод для входа в контекстный менеджер
        def run_async():
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.__aenter__())
        threading.Thread(target=run_async).start()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # синхронный метод для выхода из контекстного менеджера
        def run_async():
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.__aexit__(exc_type, exc_val, exc_tb))
        threading.Thread(target=run_async).start()

    async def check_for_new_message(self, func) -> None:
        """
        Метод check_for_new_message проверяет наличие непрочитанных сообщений на почтовом сервере, извлекает описание
        новых сообщений и передает их в функцию-обработчик func. В случае успешного получения описания нового
        сообщения, метод вызывает функцию check_read_messages для проверки, было ли сообщение уже обработано ранее.
        Если сообщение еще не было обработано, оно передается в функцию-обработчик и его идентификатор добавляется в
        базу данных с помощью функции set_read_messages.

        :param func: функция-обработчик
        :return:
        """

        try:
            result, data = self.mail.search(None, "UNSEEN")
            if result == "OK":
                for num in data[0].split():
                    result, data = self.mail.fetch(num, "(RFC822)")
                    self.mail.store(num, '+FLAGS', '\\Unseen')
                    if result == "OK":
                        message = Message(message_from_bytes(data[0][1]))
                        if not check_read_messages(message.id):
                            tg_msg_id = func(message.post, message.attachments)
                            set_read_messages(message.id, tg_msg_id)
        except Exception:
            logger.error(f"Error occurred while checking for new messages")

    @staticmethod
    async def run_mail_reader(bot):
        """
        Метод run_mail_reader предназначен для запуска MailReader в отдельном потоке. Он создает экземпляр MailReader,
        вызывает его метод check_for_new_message и засыпает на заданное время. После этого цикл повторяется.
        Функция-обработчик передается в метод check_for_new_message в качестве аргумента.

        :param bot: экземпляр Telegram-бота
        :return:
        """

        while True:
            try:
                if bot.is_connected:
                    logger.debug(f"Started MailReader on a separate thread")
                    async with MailReader(MAIL_SERVER, MAIL_USER, MAIL_PASSWORD) as mail_reader:
                        await mail_reader.check_for_new_message(bot.send_message)
                else:
                    logger.debug(f"Wait connection bot to chat")
            except Exception:
                logger.error(f"Error occurred in MailReader")
            await asyncio.sleep(INTERVAL)

    def get_attachments(self, message_id: str):
        try:
            logger.debug(f"Getting attachments from message id {message_id}")

            # проверка, было ли сообщение уже прочитано
            unseen_messages = []
            result, data = self.mail.search(None, "UNSEEN")
            if result == "OK":
                for num in data[0].split():
                    result, data = self.mail.fetch(num, "(RFC822)")
                    self.mail.store(num, '+FLAGS', '\\Unseen')
                    if result == "OK":
                        unseen_messages.append(Message(message_from_bytes(data[0][1])).id)
            is_unseen = True if message_id in unseen_messages else False
            # Поиск сообщения по его UID
            result, data = self.mail.uid('search', None, f'HEADER Message-ID "{message_id}"')
            if result == "OK":
                for num in data[0].split():
                    result, data = self.mail.uid('fetch', num, "(RFC822)")
                    if is_unseen:
                        self.mail.store(num, '+FLAGS', '\\Unseen')
                    if result == "OK":
                        return Message.get_attachments_content(message_from_bytes(data[0][1]))
        except Exception:
            logger.error(f"Error occurred while checking for new messages")
