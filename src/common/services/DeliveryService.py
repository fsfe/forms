import json
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import make_msgid, formatdate

from common.config import SMTP_HOST, SMTP_PORT


def send(send_from, send_to, subject, content, reply_to, headers):
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        if isinstance(content, dict):
            msg = MIMEMultipart('alternative')
            html_content = content.get('html', None)
            plain_content = content.get('plain', None)
            if html_content is not None:
                html = MIMEText(content.get('html', None), 'html')
                msg.attach(html)
            if plain_content is not None:
                plain = MIMEText(content.get('plain', None), 'plain')
                msg.attach(plain)
        else:
            msg = MIMEText(content)
        smtp.ehlo_or_helo_if_needed()
        msg['Subject'] = subject
        msg['From'] = send_from
        msg['To'] = ', '.join(send_to)
        msg['Message-ID'] = make_msgid()
        msg['Date'] = formatdate()

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
    add = {
        "from": send_from,
        "to": send_to,
        "subject": subject,
        "content": content,
        "reply-to": reply_to,
        "include_vars": include_vars
    }

    if not os.path.exists(os.path.dirname(storage)):
       os.makedirs(os.path.dirname(storage))
       with open(storage, "a") as file:
         file.write(json.dumps([]))

    with open(storage, "r") as file:
        prev = json.loads(file.read())

    with open(storage, "w") as file:
        file.write(prev.append(add))

