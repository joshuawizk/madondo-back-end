from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash

from config import Config
from extensions import db, migrate

# Import all models
from models import *

# Import all blueprints
from routes import (
    project_bp,
    contact_bp,
    donation_bp,
    gallery_bp,
    auth_bp,
    admin_bp,
)

app = Flask(__name__)
app.config.from_object(Config)

CORS(app)

# Initialize extensions
db.init_app(app)
migrate.init_app(app, db)

# Register Blueprints
app.register_blueprint(project_bp)
app.register_blueprint(contact_bp)
app.register_blueprint(donation_bp)
app.register_blueprint(gallery_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)


def seed_demo_projects():
    from models.project import Project

    if Project.query.count() == 0:
        projects = [
            Project(
                title="Community Farming Initiative",
                category="Agriculture",
                description="Supporting families with practical training, seeds, and tools to strengthen food security.",
                image_url="https://images.unsplash.com/photo-1464226184884-fa280b87c399?auto=format&fit=crop&w=900&q=80",
                is_published=True,
            ),
            Project(
                title="Small Business Support",
                category="Entrepreneurship",
                description="Helping local entrepreneurs gain access to training, guidance, and resources to grow their ventures.",
                image_url="https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=900&q=80",
                is_published=True,
            ),
            Project(
                title="Youth Empowerment Programme",
                category="Education",
                description="Creating opportunities for young people through mentorship, skills-building, and community outreach.",
                image_url="https://images.unsplash.com/photo-1517486808906-6ca8b3f04846?auto=format&fit=crop&w=900&q=80",
                is_published=True,
            ),
        ]
        db.session.add_all(projects)
        db.session.commit()


def seed_demo_gallery_images():
    from models.gallery import GalleryImage

    if GalleryImage.query.count() == 0:
        gallery_items = [
            GalleryImage(
                title="Community Farming Session",
                image_url="https://images.unsplash.com/photo-1464226184884-fa280b87c399?auto=format&fit=crop&w=900&q=80",
                caption="Families learning practical ways to grow food and strengthen local livelihoods.",
            ),
            GalleryImage(
                title="Youth Empowerment Day",
                image_url="https://images.unsplash.com/photo-1517486808906-6ca8b3f04846?auto=format&fit=crop&w=900&q=80",
                caption="Young people building confidence, skills, and a brighter future.",
            ),
            GalleryImage(
                title="Small Business Support",
                image_url="https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=900&q=80",
                caption="Entrepreneurs receiving guidance and resources to grow their businesses.",
            ),
        ]
        db.session.add_all(gallery_items)
        db.session.commit()


def seed_admin_account():
    from models.user import User

    if User.query.count() == 0:
        db.session.add(
            User(
                username="madondo",
                email="josephmadondo537@gmail.com",
                password=generate_password_hash("@josephmadondo"),
                role="admin",
                is_active=True,
            )
        )
        db.session.commit()


with app.app_context():
    db.create_all()
    seed_demo_projects()
    seed_demo_gallery_images()
    seed_admin_account()


@app.route("/")
def home():
    return jsonify({
        "success": True,
        "message": "Welcome to Madondo Hope Foundation API",
        "endpoints": [
            "/projects",
            "/contact",
            "/donations",
            "/login",
        ],
    })


@app.route("/health")
def health():
    return jsonify({"success": True, "message": "API is healthy"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)