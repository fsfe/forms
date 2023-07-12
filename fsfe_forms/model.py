from typing import Any, Dict, Optional
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import orm
from sqlalchemy.dialects.postgresql import JSON


EMAIL_MAX_LENGTH = 320
EMAIL_SUBJECT_MAX_LENGTH = 998


db = SQLAlchemy()


class Email(db.Model):
    """Email sent by the FSFE Form Server."""
    # The application name from the `applications.json` file.
    # Example: contact, pmpc-sign, reuse-booster
    email_form = db.Column(db.String(EMAIL_MAX_LENGTH))
    # Ingestion timestamp.
    create_at = db.Column(db.DateTime())
    # The email address of the sender.
    from_ = db.Column(db.String(EMAIL_MAX_LENGTH))
    # The email address of the recipient.
    to = db.Column(db.String(EMAIL_MAX_LENGTH))
    # The subject of the email.
    subject = db.Column(db.String(EMAIL_SUBJECT_MAX_LENGTH))
    # The content of the email.
    content = db.Column(db.Text)
    # The reply-to address of the email.
    reply_to = db.Column(db.String(EMAIL_MAX_LENGTH))
    # The variables included in the email parameters.
    include_vars = db.Column(db.Text)
    # The confirmation status of the email.
    # Some emails are not attenting confirmation. Consequently, this field
    # is nullable.
    confirmed = db.Column(db.Boolean(nullable=True))
    # Ingestion timestamp.
    confirmed_date = db.Column(db.DateTime(nullable=True))

    @classmethod
    def log(cls, email_form: str, send_from: str, send_to: str, subject: str, content: str, reply_to: str, include_vars: Dict[str, Any]):
        """Save the e-mail to the database or confirm the previous."""
        if email := cls._get(email_form, send_from):
            cls._confirmed(email)
        else:
            cls._create(email_form, send_from, send_to, subject, content, reply_to, include_vars)

    @classmethod
    def find(cls, email_form: str, email: str) -> bool:
        """Return True if the e-mail has been sent to the given email address."""
        return cls._get(email_form, email) is not None

    @classmethod
    def _get(cls, email_form: str, email: str) -> Optional["Email"]:
        return cls.query.filter_by(
            email_form=email_form,
            from_=email,
        ).one_or_none()

    @classmethod
    def _confirmed(cls, email: "Email"):
        email.confirmed = True
        email.confirmed_date = db.func.now()
        db.session.commit()

    @classmethod
    def _create(cls, email_form: str, send_from: str, send_to: str, subject: str, content: str, reply_to: str, include_vars: Dict[str, Any]):
        must_be_confirmed = bool(include_vars.get("include_vars", {}).get("confirm"))

        record = cls(
            email_form=email_form,
            from_=send_from,
            to=send_to,
            subject=subject,
            content=content,
            reply_to=reply_to,
            include_vars=str(include_vars),
            confirmed=False if must_be_confirmed else None,
            confirmed_date=None
        )

        db.session.add(record)
        db.session.commit()

        return record
