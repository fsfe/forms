import json
import smtplib
import filelock
import time
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import make_msgid, formatdate

from fsfe_forms.common.config import SMTP_HOST, SMTP_PORT, LOCK_FILENAME


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
        "timestamp": time.time(),
        "from": send_from,
        "to": send_to,
        "subject": subject,
        "content": content,
        "reply-to": reply_to,
        "include_vars": include_vars
    }

    lock = filelock.FileLock(LOCK_FILENAME)
    logs = read_log(storage, lock) + [add]
    logs_in_json = json.dumps(logs)
    with lock, open(storage, "w") as file:
        file.write(logs_in_json)


def read_log(storage, lock=filelock.FileLock(LOCK_FILENAME)):
    _create_log_file_if_not_exist(storage, lock)
    with lock, open(storage, "r") as file:
        f = file.read()
    return json.loads(f)


def _create_log_file_if_not_exist(storage, lock):
    with lock:
        if not os.path.exists(os.path.dirname(storage)):
            os.makedirs(os.path.dirname(storage))

        if not os.path.exists(storage):
            with open(storage, "w") as file:
                file.write(json.dumps([]))
