from flask import Blueprint, jsonify, request
from extensions import db
from models.donations import Donation
from services.payment_service import initiate_payment

donation_bp = Blueprint("donations", __name__)


def _normalize_text(value):
    return (value or "").strip()


@donation_bp.route("/donations", methods=["GET", "POST"])
@donation_bp.route("/api/donations", methods=["GET", "POST"])
def donations():
    if request.method == "GET":
        donations = Donation.query.order_by(Donation.created_at.desc()).limit(10).all()
        return jsonify({
            "success": True,
            "message": "Donations endpoint is ready",
            "donations": [d.to_dict() for d in donations],
        })

    data = request.get_json(silent=True) or {}
    if not data:
        data = request.form.to_dict() or {}

    donor_name = _normalize_text(data.get("donor_name"))
    amount = data.get("amount")
    method = _normalize_text(data.get("method"))

    if not donor_name or amount is None or not method:
        return jsonify({
            "success": False,
            "message": "Please provide your name, donation amount, and payment method."
        }), 400

    try:
        amount_value = float(amount)
    except (TypeError, ValueError):
        return jsonify({
            "success": False,
            "message": "The donation amount must be a valid number."
        }), 400

    donation = Donation(
        donor_name=donor_name,
        email=_normalize_text(data.get("email")),
        phone=_normalize_text(data.get("phone")),
        amount=amount_value,
        currency=_normalize_text(data.get("currency")) or "UGX",
        method=method,
        transaction_ref=_normalize_text(data.get("transaction_ref")),
        message=_normalize_text(data.get("message")),
        status="pending",
    )

    payment_result = initiate_payment(
        amount=amount_value,
        currency=donation.currency,
        donor_email=donation.email,
        donor_name=donation.donor_name,
    )

    try:
        db.session.add(donation)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": "We could not record your donation right now. Please try again later."
        }), 500

    return jsonify({
        "success": True,
        "message": "Thank you for your generous support. Your donation has been received and is being reviewed.",
        "payment": payment_result,
        "donation": donation.to_dict(),
    })