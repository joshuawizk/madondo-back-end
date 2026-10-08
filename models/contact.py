from datetime import datetime, timezone
from extensions import db


def now():
    return datetime.now(timezone.utc)


class ContactMessage(db.Model):
    __tablename__ = "contact_messages"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200))
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    reply_note = db.Column(db.Text)
    reply_status = db.Column(db.String(24), default="pending", nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=now, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "subject": self.subject,
            "message": self.message,
            "is_read": self.is_read,
            "reply_note": self.reply_note,
            "reply_status": self.reply_status,
            "created_at": self.created_at.isoformat(),
        }
    