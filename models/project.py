from datetime import datetime, timezone
from extensions import db


def now():
    return datetime.now(timezone.utc)


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(80))
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(300))
    is_published = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=now, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "description": self.description,
            "image_url": self.image_url,
            "is_published": self.is_published,
            "created_at": self.created_at.isoformat(),
        }