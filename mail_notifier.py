import imaplib

from email import message_from_bytes

from message import Message


class MailNotifier:

    def __init__(self, mail: str, password: str) -> None:
        self.mail = imaplib.IMAP4_SSL("imap.mail.ru")
        self.mail.login(mail, password)
        self.mail.select("inbox")

    async def check_for_new_message(self) -> None:
        result, data = self.mail.search(None, "UNSEEN")
        if result == "OK":
            for num in data[0].split():
                result, data = self.mail.fetch(num, "(RFC822)")
                self.mail.store(num, '+FLAGS', '\\Unseen')
                if result == "OK":
                    msg = Message(message_from_bytes(data[0][1]))
                    print(f"\n{'='*30}\n{msg.description}\n")
