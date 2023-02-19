import datetime
import email.utils
import base64
from bs4 import BeautifulSoup
import quopri

from email.message import Message as EmailMessage
from email.header import decode_header


class Message:

    def __init__(self, raw_message: EmailMessage) -> None:
        self.id: str = ...
        self.name_from: str = ...
        self.email_from: str = ...
        self.body: str = ...
        self.attachments = []

        self.text = self._get_text(raw_message)
        self.attachments = self._get_attachments(raw_message)

    # def _parse(self, raw: EmailMessage) -> None:
    #     self.id = raw["Message-ID"]
    #     self.time = self._parse_time(raw["Date"])
    #     self.name_from = raw['Return-path'][1:-1]
    #     self.email_from = self._decode(raw["From"])
    #     self.subject = self._decode(raw["Subject"])
    #
    #     self.body = ""
    #     for part in raw.walk():
    #         part: EmailMessage
    #         if part.get_content_maintype() == 'text' and part.get_content_subtype() == 'plain':
    #             self.body += self._decode(part.get_payload(decode=True))
    #         elif part.get_content_disposition() == 'attachment':
    #             filename = self._decode(part.get_filename())
    #             document = part.get_payload(decode=True)
    #             self.attachments.append((filename, document))
    #
    #             # # download in project directory 
    #             # with open(filename, "wb") as fp:
    #             #     fp.write(part.get_payload(decode=True))

    def _get_text(self, msg):
        if msg.is_multipart():
            for part in msg.walk():
                count = 0
                if part.get_content_maintype() == "text" and count == 0:
                    extract_part = self._decode(part)
                    if part.get_content_subtype() == "html":
                        letter_text = self._get_text_from_html(extract_part)
                    else:
                        letter_text = extract_part.rstrip().lstrip()
                    count += 1
                    return (
                        letter_text.replace("<", "").replace(">", "").replace("\xa0", " ")
                    )
        else:
            count = 0
            if msg.get_content_maintype() == "text" and count == 0:
                extract_part = self._decode(msg)
                if msg.get_content_subtype() == "html":
                    letter_text = self._get_text_from_html(extract_part)
                else:
                    letter_text = extract_part
                count += 1
                return letter_text.replace("<", "").replace(">", "").replace("\xa0", " ")

    def _get_text_from_html(self, body):
        body = body.replace("<div><div>", "<div>").replace("</div></div>", "</div>")
        try:
            soup = BeautifulSoup(body, "html.parser")
            paragraphs = soup.find_all("div")
            text = ""
            for paragraph in paragraphs:
                text += paragraph.text + "\n"
            return text.replace("\xa0", " ")
        except (Exception) as exp:
            print("text ftom html err ", exp)
            return False

    def _parse_time(self, time_str: str) -> str:
        time_tuple = email.utils.parsedate_tz(time_str)
        if time_tuple:
            dt = datetime.datetime.fromtimestamp(email.utils.mktime_tz(time_tuple))
            return dt.strftime("%d.%m.%Y %H:%M:%S")
        else:
            return ""

    def _decode(self, part):
        if part["Content-Transfer-Encoding"] in (None, "7bit", "8bit", "binary"):
            return part.get_payload()
        elif part["Content-Transfer-Encoding"] == "base64":
            encoding = part.get_content_charset()
            return base64.b64decode(part.get_payload()).decode(encoding)
        elif part["Content-Transfer-Encoding"] == "quoted-printable":
            encoding = part.get_content_charset()
            return quopri.decodestring(part.get_payload()).decode(encoding)
        else:  # all possible types: quoted-printable, base64, 7bit, 8bit, and binary
            return part.get_payload()

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
