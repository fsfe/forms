import json
import smtplib
from email.mime.text import MIMEText

from common.config import SMTP_HOST, SMTP_PORT


def send(send_from, send_to, subject, content, reply_to, headers):
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.ehlo_or_helo_if_needed()
        msg = MIMEText(content)
        msg['Subject'] = subject
        msg['From'] = send_from
        if headers is not None:
            for field, value in headers.items():
                msg[field] = value
        if reply_to is not None:
            msg.add_header('reply-to', reply_to)
        try:
            smtp.sendmail(send_from, send_to, msg.as_string())
            return True
        except:
            return False


def log(storage, send_from, send_to, subject, content, reply_to, include_vars):
    text = json.dumps({
        "from": send_from,
        "to": send_to,
        "subject": subject,
        "content": content,
        "reply-to": reply_to,
        "include_vars": include_vars
    }) + "\n"
    with open(storage, "a") as file:
        file.write(text)
