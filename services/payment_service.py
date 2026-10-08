import json
import os
import urllib.request
import urllib.error


PAYMENT_PROVIDER = (os.getenv("PAYMENT_PROVIDER") or "mock").lower()


def initiate_payment(amount, currency="UGX", donor_email="", donor_name=""):
    provider = PAYMENT_PROVIDER
    if provider == "mock":
        return {
            "success": True,
            "provider": "mock",
            "message": "Mock payment gateway ready. Configure real provider credentials for production checkout.",
            "reference": f"MOCK-{abs(hash(donor_email or donor_name or 'madondo'))}",
        }

    if provider == "stripe":
        secret_key = os.getenv("STRIPE_SECRET_KEY")
        if not secret_key:
            return {
                "success": False,
                "provider": "stripe",
                "message": "Stripe secret key not configured.",
            }

        payload = json.dumps({
            "amount": int(float(amount) * 100),
            "currency": (currency or "usd").lower(),
            "payment_method_types": ["card"],
            "description": f"Donation from {donor_name or donor_email or 'Madondo donor'}",
        }).encode("utf-8")

        request = urllib.request.Request(
            "https://api.stripe.com/v1/payment_intents",
            data=payload,
            headers={
                "Authorization": f"Bearer {secret_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request) as response:
                result = json.loads(response.read().decode("utf-8"))
            return {
                "success": True,
                "provider": "stripe",
                "message": "Stripe payment intent created.",
                "reference": result.get("id"),
            }
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="ignore")
            return {
                "success": False,
                "provider": "stripe",
                "message": f"Stripe payment error: {error_body}",
            }

    return {
        "success": False,
        "provider": provider,
        "message": "Unsupported payment provider. Set PAYMENT_PROVIDER=mock or stripe.",
    }
