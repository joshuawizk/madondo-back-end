from flask import Blueprint, jsonify, request, session
from werkzeug.security import check_password_hash

from models.user import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return jsonify({
            "success": True,
            "message": "Login endpoint is working",
        })

    data = request.get_json(silent=True) or {}
    username = (data.get("username") or data.get("email") or "").strip()
    password = (data.get("password") or "").strip()

    if not username or not password:
        return jsonify({
            "success": False,
            "message": "Please provide your admin username/email and password.",
        }), 400

    user = User.query.filter((User.username == username) | (User.email == username)).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({
            "success": False,
            "message": "Invalid admin credentials.",
        }), 401

    session["admin_logged_in"] = True
    session["admin_user_id"] = user.id
    session["admin_username"] = user.username

    return jsonify({
        "success": True,
        "message": "Admin login successful.",
        "user": user.to_dict(),
    })


@auth_bp.route("/admin/session", methods=["GET"])
def admin_session_status():
    if session.get("admin_logged_in") and session.get("admin_user_id"):
        user = User.query.get(session["admin_user_id"])
        if user:
            return jsonify({
                "success": True,
                "logged_in": True,
                "user": user.to_dict(),
            })

    return jsonify({
        "success": True,
        "logged_in": False,
    })


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({
        "success": True,
        "message": "Admin session cleared.",
    })