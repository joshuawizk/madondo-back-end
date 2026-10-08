from datetime import datetime, timezone
from extensions import db


def now():
    return datetime.now(timezone.utc)


class Donation(db.Model):
    __tablename__ = "donations"

    id = db.Column(db.Integer, primary_key=True)
    donor_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(40))
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default="UGX", nullable=False)
    method = db.Column(db.String(40), nullable=False)
    transaction_ref = db.Column(db.String(120))
    message = db.Column(db.Text)
    status = db.Column(db.String(20), default="pending", nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=now, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "donor_name": self.donor_name,
            "email": self.email,
            "phone": self.phone,
            "amount": self.amount,
            "currency": self.currency,
            "method": self.method,
            "transaction_ref": self.transaction_ref,
            "message": self.message,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
        }