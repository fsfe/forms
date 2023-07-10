from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import orm
from sqlalchemy.dialects.postgresql import JSON


db = SQLAlchemy()


class Repository(db.Model):
    """Repository database class"""

    appid = db.Column(db.String(40))
    timestamp = db.Column(db.DateTime())
    from_ = db.Column(db.String(40))
    to = db.Column(db.String(40))
    subject = db.Column(db.String(40))
    content = db.Column(db.Text)
    reply_to = db.Column(db.String(40))
    include_vars = db.Column(JSON)

    @classmethod
    def log(cls, storage, send_from, send_to, subject, content, reply_to, include_vars):
        ...

    @classmethod
    def find(cls, storage: str, email: str) -> bool:
        ...
