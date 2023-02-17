import imaplib

from email import message_from_bytes

from message import Message


class MailNotifier:

    def __init__(self, mail: str, password: str) -> None:
        self.mail = None
        self.mail_credentials = (mail, password)
        self.checked_messages = {}

    async def __aenter__(self):
        self.mail = imaplib.IMAP4_SSL("imap.mail.ru")
        self.mail.login(*self.mail_credentials)
        self.mail.select("inbox")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.mail.close()
        self.mail.logout()

    async def check_for_new_message(self, func) -> None:
        print("checking...")
        result, data = self.mail.search(None, "UNSEEN")
        if result == "OK":
            for num in data[0].split():
                result, data = self.mail.fetch(num, "(RFC822)")
                self.mail.store(num, '+FLAGS', '\\Unseen')
                if result == "OK":
                    msg = Message(message_from_bytes(data[0][1]))
                    message_id = msg.id
                    if message_id not in self.checked_messages:
                        func(msg.description)
                        self.checked_messages[message_id] = msg.description
