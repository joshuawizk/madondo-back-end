from flask import Blueprint, jsonify, request
from extensions import db
from models.contact import ContactMessage

contact_bp = Blueprint("contact", __name__)


def _normalize_text(value):
    return (value or "").strip()


@contact_bp.route("/contact", methods=["POST"])
@contact_bp.route("/api/contact", methods=["POST"])
def contact():
    data = request.get_json(silent=True) or {}

    if not data:
        data = request.form.to_dict() or {}

    name = _normalize_text(data.get("name"))
    email = _normalize_text(data.get("email"))
    subject = _normalize_text(data.get("subject"))
    message = _normalize_text(data.get("message"))

    if not name or not email or not message:
        return jsonify({
            "success": False,
            "message": "Please provide your name, email, and a message."
        }), 400

    new_message = ContactMessage(
        name=name,
        email=email,
        subject=subject or "General enquiry",
        message=message,
    )

    try:
        db.session.add(new_message)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": "We could not save your message right now. Please try again later."
        }), 500

    return jsonify({
        "success": True,
        "message": "Thank you! Your message has been received. We will get back to you shortly."
    })