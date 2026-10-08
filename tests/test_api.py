import os
import sys
import unittest
from werkzeug.security import generate_password_hash

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import app
from extensions import db
from models.contact import ContactMessage
from models.donations import Donation
from models.project import Project
from models.user import User


class ApiRoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config.update(TESTING=True, SQLALCHEMY_DATABASE_URI="sqlite:///:memory:")
        self.client = self.app.test_client()
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            admin = User(
                username="madondo",
                email="josephmadondo537@gmail.com",
                password=generate_password_hash("@josephmadondo"),
                role="admin",
            )
            db.session.add(admin)
            db.session.commit()

    def test_contact_endpoint_accepts_valid_payload(self):
        response = self.client.post(
            "/contact",
            json={
                "name": "Jane",
                "email": "jane@example.com",
                "subject": "Support",
                "message": "Hello from the test suite",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()["success"])

    def test_donation_endpoint_accepts_valid_payload(self):
        response = self.client.post(
            "/donations",
            json={
                "donor_name": "John",
                "email": "john@example.com",
                "phone": "+256700000000",
                "amount": 50000,
                "currency": "UGX",
                "method": "Mobile Money",
                "transaction_ref": "TXN-001",
                "message": "Proud to support",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()["success"])

    def test_admin_login_accepts_hashed_password(self):
        response = self.client.post(
            "/login",
            json={"username": "madondo", "password": "@josephmadondo"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()["success"])
        self.assertIn("madondo", response.get_json()["user"]["username"])

    def test_admin_dashboard_returns_analytics_summary(self):
        with self.app.app_context():
            db.session.add(Project(title="Solar", category="Energy", description="Solar", image_url="", is_published=True))
            db.session.add(ContactMessage(name="A", email="a@example.com", subject="Support", message="Need help", is_read=False))
            db.session.add(Donation(donor_name="B", email="b@example.com", amount=15000, currency="UGX", method="Cash", transaction_ref="T-1", status="approved"))
            db.session.commit()

        login = self.client.post(
            "/login",
            json={"username": "josephmadondo537@gmail.com", "password": "@josephmadondo"},
        )
        self.assertEqual(login.status_code, 200)

        response = self.client.get("/admin/dashboard")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload["success"])
        self.assertEqual(payload["summary"]["total_projects"], 1)
        self.assertEqual(payload["summary"]["total_donations"], 1)
        self.assertEqual(payload["summary"]["total_contacts"], 1)

    def test_gallery_post_and_get_workflow(self):
        login = self.client.post(
            "/login",
            json={"username": "josephmadondo537@gmail.com", "password": "@josephmadondo"},
        )
        self.assertEqual(login.status_code, 200)

        create_response = self.client.post(
            "/admin/gallery",
            json={
                "title": "Community Day",
                "image_url": "https://example.com/gallery.jpg",
                "caption": "A meaningful moment of solidarity.",
            },
        )
        self.assertEqual(create_response.status_code, 200)
        self.assertTrue(create_response.get_json()["success"])

        list_response = self.client.get("/gallery")
        self.assertEqual(list_response.status_code, 200)
        gallery_payload = list_response.get_json()
        self.assertTrue(gallery_payload["success"])
        self.assertEqual(len(gallery_payload["gallery"]), 1)
        self.assertEqual(gallery_payload["gallery"][0]["title"], "Community Day")


if __name__ == "__main__":
    unittest.main()
