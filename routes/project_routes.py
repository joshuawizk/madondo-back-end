from flask import Blueprint, jsonify
from models.project import Project

project_bp = Blueprint("projects", __name__)


@project_bp.route("/projects", methods=["GET"])
@project_bp.route("/api/projects", methods=["GET"])
def get_projects():
    projects = Project.query.filter_by(is_published=True).order_by(Project.created_at.desc()).all()
    return jsonify({
        "success": True,
        "projects": [p.to_dict() for p in projects]
    })