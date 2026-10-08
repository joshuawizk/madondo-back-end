from flask import Blueprint, jsonify

from models.gallery import GalleryImage

gallery_bp = Blueprint("gallery", __name__)


@gallery_bp.route("/gallery", methods=["GET"])
@gallery_bp.route("/api/gallery", methods=["GET"])
def get_gallery():
    gallery_items = GalleryImage.query.order_by(GalleryImage.created_at.desc()).all()
    return jsonify({
        "success": True,
        "gallery": [item.to_dict() for item in gallery_items],
    })
