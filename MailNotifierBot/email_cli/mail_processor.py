import datetime
import email.utils

from email.message import Message as EmailMessage
from email.header import decode_header


class Message:

    def __init__(self, raw_message: EmailMessage) -> None:
        self.id: str = ...
        self.name_from: str = ...
        self.email_from: str = ...
        self.body: str = ...
        self.attachments = []

        self._parse(raw_message)

    def _parse(self, raw: EmailMessage) -> None:
        self.id = raw["Message-ID"]
        self.time = self._parse_time(raw["Date"])
        self.name_from = raw['Return-path'][1:-1]
        self.email_from = self._decode(raw["From"])
        self.subject = self._decode(raw["Subject"])

        self.body = ""
        for part in raw.walk():
            part: EmailMessage
            if part.get_content_maintype() == 'text' and part.get_content_subtype() == 'plain':
                self.body += self._decode(part.get_payload(decode=True))
            elif part.get_content_disposition() == 'attachment':
                filename = self._decode(part.get_filename())
                document = part.get_payload(decode=True)
                self.attachments.append((filename, document))

                # # download in project directory
                # with open(filename, "wb") as fp:
                #     fp.write(part.get_payload(decode=True))

    def _parse_time(self, time_str: str) -> str:
        time_tuple = email.utils.parsedate_tz(time_str)
        if time_tuple:
            dt = datetime.datetime.fromtimestamp(email.utils.mktime_tz(time_tuple))
            return dt.strftime("%d.%m.%Y %H:%M:%S")
        else:
            return ""

    def _decode(self, string: str) -> str:
        if string is None:
            return ''
        elif not isinstance(string, bytes):
            decoded = ""
            for part, encoding in decode_header(string):
                if isinstance(part, bytes):
                    decoded_part = part.decode(encoding or 'utf-8', errors='ignore')
                else:
                    decoded_part = part
                decoded += decoded_part
            return decoded
        else:
            return string.decode('utf-8', errors='ignore')

    @property
    def post(self) -> tuple:
        if self.attachments:
            attachments = f"\nВложения {len(self.attachments)}:\n"
            for filename, document in self.attachments:
                attachments += f"{filename}\n"
        else:
            attachments = ""
        return f"От: {self.email_from} [{self.name_from}]\n" \
               f"Время: {self.time}\n" \
               f"Тема: {self.subject}\n" \
               f"Текст: {self.body}" + attachments, self.attachments
