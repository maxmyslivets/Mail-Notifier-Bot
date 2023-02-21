import datetime
import email.utils
import base64
from bs4 import BeautifulSoup
import quopri
import re

from email.message import Message as EmailMessage
from email.header import decode_header
from MailNotifierBot.logger import logger


class Message:

    def __init__(self, raw_message: EmailMessage) -> None:

        if raw_message["Message-ID"]:
            self.id = raw_message["Message-ID"].lstrip("<").rstrip(">")
        else:
            self.id = raw_message["Received"]

        self.name_from = self.from_subj_decode(raw_message["From"])
        self.subject = self.from_subj_decode(raw_message["Subject"])
        if self.subject is None:
            self.subject = "Без темы"

        if raw_message["Return-path"]:
            self.email_from = raw_message["Return-path"].lstrip("<").rstrip(">")
        else:
            self.email_from = self.name_from

        # FIXME: parse image from email message

        self.text = self._get_text(raw_message)
        if self.text is None:
            self.text = ""
        self.attachments = self._get_attachments(raw_message)

    @staticmethod
    def from_subj_decode(msg_from_subj):
        """декодирует имена отправителей и темы сообщений электронной почты."""
        if msg_from_subj:
            encoding = decode_header(msg_from_subj)[0][1]
            msg_from_subj = decode_header(msg_from_subj)[0][0]
            if isinstance(msg_from_subj, bytes):
                msg_from_subj = msg_from_subj.decode(encoding)
            if isinstance(msg_from_subj, str):
                pass
            msg_from_subj = str(msg_from_subj).strip("<>").replace("<", "")
            return msg_from_subj
        else:
            return None

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
        except Exception as e:
            logger.error(f"Text from html err: {e}")
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

    def _get_attachments(self, msg):
        """извлекает список имен файлов всех вложений в сообщении электронной почты."""
        attachments = list()
        for part in msg.walk():
            if (
                    part["Content-Type"]
                    and "name" in part["Content-Type"]
                    and part.get_content_disposition() == "attachment"
            ):
                filename = part.get_filename()
                filename = self.from_subj_decode(filename)
                attachments.append(filename)
        return attachments

    @staticmethod
    def get_attachments_content(msg: EmailMessage) -> list:
        attachments = list()
        for part in msg.walk():
            if (
                    part["Content-Type"]
                    and "name" in part["Content-Type"]
                    and part.get_content_disposition() == "attachment"
            ):
                filename = Message.from_subj_decode(part.get_filename())
                content = part.get_payload(decode=True)
                attachments.append((filename, content))
        return attachments

    @property
    def post(self) -> str:
        return f"\U0001F4E8 <b>{self.subject}</b>\n" \
               f"\n" \
               f"<pre>{self.name_from}\n" \
               f"{self.email_from}</pre>\n" \
               f"\n" \
               f"<i>{self.text}</i>"
