from flask import Blueprint, jsonify, request, session
from sqlalchemy import func

from extensions import db
from models.contact import ContactMessage
from models.donations import Donation
from models.gallery import GalleryImage
from models.project import Project
from models.user import User
from services.email_service import send_email

admin_bp = Blueprint("admin", __name__)


def _monthly_series(model, field_name):
    if db.engine.name == "postgresql":
        month_expr = func.to_char(field_name, "YYYY-MM")
    else:
        month_expr = func.strftime("%Y-%m", field_name)

    return (
        db.session.query(
            month_expr.label("month"),
            func.count(field_name).label("total"),
        )
        .group_by(month_expr)
        .order_by(month_expr)
        .all()
    )


def _require_admin_session():
    if not session.get("admin_logged_in") or not session.get("admin_user_id"):
        return False
    return True


@admin_bp.route("/admin", methods=["GET"])
def admin_dashboard():
    if not _require_admin_session():
        return jsonify({"success": False, "message": "Admin session required."}), 401
    return admin_dashboard_summary()


@admin_bp.route("/admin/dashboard", methods=["GET"])
def admin_dashboard_summary():
    if not _require_admin_session():
        return jsonify({"success": False, "message": "Admin session required."}), 401

    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    donations = Donation.query.order_by(Donation.created_at.desc()).all()
    projects = Project.query.order_by(Project.created_at.desc()).all()
    active_users = User.query.filter_by(is_active=True).count()

    total_amount = sum((donation.amount or 0) for donation in donations)
    pending_count = Donation.query.filter_by(status="pending").count()
    approved_count = Donation.query.filter_by(status="approved").count()
    declined_count = Donation.query.filter_by(status="declined").count()

    donations_by_month = [
        {"month": row.month, "total": row.total}
        for row in _monthly_series(Donation, Donation.created_at)
    ]
    contacts_by_month = [
        {"month": row.month, "total": row.total}
        for row in _monthly_series(ContactMessage, ContactMessage.created_at)
    ]
    projects_by_month = [
        {"month": row.month, "total": row.total}
        for row in _monthly_series(Project, Project.created_at)
    ]

    recent_donation = donations[0].to_dict() if donations else None
    recent_contact = messages[0].to_dict() if messages else None

    return jsonify({
        "success": True,
        "summary": {
            "total_projects": Project.query.count(),
            "total_donations": Donation.query.count(),
            "total_contacts": ContactMessage.query.count(),
            "total_users": User.query.count(),
            "active_users": active_users,
            "total_donation_amount": round(total_amount, 2),
            "pending_donations": pending_count,
            "approved_donations": approved_count,
            "declined_donations": declined_count,
            "unread_contacts": ContactMessage.query.filter_by(is_read=False).count(),
            "recent_donation": recent_donation,
            "recent_contact": recent_contact,
        },
        "projects": [project.to_dict() for project in projects],
        "contacts": [message.to_dict() for message in messages],
        "donations": [donation.to_dict() for donation in donations],
        "charts": {
            "donations_by_month": donations_by_month,
            "contacts_by_month": contacts_by_month,
            "projects_by_month": projects_by_month,
        },
    })


@admin_bp.route("/admin/gallery", methods=["GET", "POST"])
def admin_gallery():
    if not _require_admin_session():
        return jsonify({"success": False, "message": "Admin session required."}), 401

    if request.method == "GET":
        gallery_items = GalleryImage.query.order_by(GalleryImage.created_at.desc()).all()
        return jsonify({"success": True, "gallery": [item.to_dict() for item in gallery_items]})

    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "Untitled image").strip()
    image_url = (data.get("image_url") or "").strip()
    caption = (data.get("caption") or "").strip()

    if not title or not image_url or not caption:
        return jsonify({
            "success": False,
            "message": "Title, image URL, and caption are required.",
        }), 400

    gallery_item = GalleryImage(title=title, image_url=image_url, caption=caption)
    db.session.add(gallery_item)
    db.session.commit()
    return jsonify({"success": True, "gallery_item": gallery_item.to_dict()})


@admin_bp.route("/admin/gallery/<int:gallery_id>", methods=["DELETE"])
def admin_gallery_detail(gallery_id):
    if not _require_admin_session():
        return jsonify({"success": False, "message": "Admin session required."}), 401

    gallery_item = GalleryImage.query.get_or_404(gallery_id)
    db.session.delete(gallery_item)
    db.session.commit()
    return jsonify({"success": True, "message": "Gallery image deleted"})


@admin_bp.route("/admin/projects", methods=["GET", "POST"])
def admin_projects():
    if not _require_admin_session():
        return jsonify({"success": False, "message": "Admin session required."}), 401

    if request.method == "GET":
        projects = Project.query.order_by(Project.created_at.desc()).all()
        return jsonify({"success": True, "projects": [p.to_dict() for p in projects]})

    data = request.get_json(silent=True) or {}
    project = Project(
        title=data.get("title", "Untitled project"),
        category=data.get("category", "General"),
        description=data.get("description", ""),
        image_url=data.get("image_url", ""),
        is_published=data.get("is_published", True),
    )
    db.session.add(project)
    db.session.commit()
    return jsonify({"success": True, "project": project.to_dict()})


@admin_bp.route("/admin/projects/<int:project_id>", methods=["PUT", "DELETE"])
def admin_project_detail(project_id):
    if not _require_admin_session():
        return jsonify({"success": False, "message": "Admin session required."}), 401

    project = Project.query.get_or_404(project_id)

    if request.method == "DELETE":
        db.session.delete(project)
        db.session.commit()
        return jsonify({"success": True, "message": "Project deleted"})

    data = request.get_json(silent=True) or {}
    project.title = data.get("title", project.title)
    project.category = data.get("category", project.category)
    project.description = data.get("description", project.description)
    project.image_url = data.get("image_url", project.image_url)
    project.is_published = data.get("is_published", project.is_published)
    db.session.commit()
    return jsonify({"success": True, "project": project.to_dict()})


@admin_bp.route("/admin/contacts", methods=["GET"])
def admin_contacts():
    if not _require_admin_session():
        return jsonify({"success": False, "message": "Admin session required."}), 401

    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return jsonify({"success": True, "contacts": [m.to_dict() for m in messages]})


@admin_bp.route("/admin/contacts/<int:message_id>", methods=["PUT", "DELETE"])
def admin_contact_detail(message_id):
    if not _require_admin_session():
        return jsonify({"success": False, "message": "Admin session required."}), 401

    message = ContactMessage.query.get_or_404(message_id)

    if request.method == "DELETE":
        db.session.delete(message)
        db.session.commit()
        return jsonify({"success": True, "message": "Contact message deleted"})

    data = request.get_json(silent=True) or {}
    message.is_read = data.get("is_read", message.is_read)
    message.reply_note = data.get("reply_note", message.reply_note)
    message.reply_status = data.get("reply_status", message.reply_status)
    db.session.commit()
    return jsonify({"success": True, "contact": message.to_dict()})


@admin_bp.route("/admin/contacts/<int:message_id>/reply", methods=["POST"])
def admin_contact_reply(message_id):
    if not _require_admin_session():
        return jsonify({"success": False, "message": "Admin session required."}), 401

    message = ContactMessage.query.get_or_404(message_id)
    data = request.get_json(silent=True) or {}
    reply_note = (data.get("reply_note") or "").strip()
    if not reply_note:
        return jsonify({"success": False, "message": "Please provide a reply note to send later."}), 400

    message.reply_note = reply_note
    message.reply_status = "queued"
    db.session.commit()

    email_result = send_email(
        to_address=message.email,
        subject=f"Re: {message.subject or 'Madondo Support Message'}",
        body=f"Hello {message.name},\n\nYour message has been received.\n\nAdmin follow-up:\n{reply_note}\n\nBest regards,\nMadondo Hope Foundation",
    )

    if email_result["success"]:
        message.reply_status = "sent"
        db.session.commit()

    return jsonify({
        "success": True,
        "message": email_result.get("message", "Reply queued for email delivery."),
        "contact": message.to_dict(),
    })


@admin_bp.route("/admin/donations", methods=["GET"])
def admin_donations():
    if not _require_admin_session():
        return jsonify({"success": False, "message": "Admin session required."}), 401

    donations = Donation.query.order_by(Donation.created_at.desc()).all()
    return jsonify({"success": True, "donations": [d.to_dict() for d in donations]})


@admin_bp.route("/admin/donations/<int:donation_id>", methods=["PUT"])
def admin_donation_detail(donation_id):
    if not _require_admin_session():
        return jsonify({"success": False, "message": "Admin session required."}), 401

    donation = Donation.query.get_or_404(donation_id)
    data = request.get_json(silent=True) or {}
    donation.status = data.get("status", donation.status)
    db.session.commit()
    return jsonify({"success": True, "donation": donation.to_dict()})