import os
import imaplib
import pickle

from email import message_from_bytes

from message import Message


class MailNotifier:

    def __init__(self, mail: str, password: str) -> None:
        self.mail = None
        self.mail_credentials = (mail, password)

        self.read_messages_file = 'read_messages.pkl'
        if not os.path.exists(self.read_messages_file):
            with open(self.read_messages_file, "wb") as f:
                pickle.dump({}, f)

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
                    read_messages = self.get_read_messages()
                    if message_id not in read_messages:
                        func(msg.description)
                        read_messages[message_id] = msg.description
                        self.set_read_messages(read_messages)

    def get_read_messages(self) -> dict:
        with open(self.read_messages_file, "rb") as f:
            return pickle.load(f)

    def set_read_messages(self, read_messages) -> None:
        with open(self.read_messages_file, "wb") as f:
            pickle.dump(read_messages, f)
