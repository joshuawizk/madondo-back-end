# Madondo Hope Foundation Backend

This backend powers the Madondo Hope Foundation website with APIs for:
- projects
- contact messages
- donations

## Run locally

1. Open the backend folder
2. Start the app with:
   `python app.py`
3. The API will run at:
   `http://127.0.0.1:5000`

## Environment configuration

Create a `.env` file for live credentials. The backend now automatically loads values from the local environment and a `.env` file.

Recommended variables:

- `SECRET_KEY=your-secret-key`
- `DATABASE_URL=sqlite:///madondo.db`
- `SMTP_HOST=smtp.gmail.com`
- `SMTP_PORT=587`
- `SMTP_USERNAME=your-email@example.com`
- `SMTP_PASSWORD=your-app-password`
- `SMTP_FROM_EMAIL=your-email@example.com`
- `PAYMENT_PROVIDER=mock`
- `STRIPE_SECRET_KEY=your-stripe-secret`

## Available endpoints

- `GET /health`
- `GET /projects`
- `POST /contact`
- `GET /donations`
- `POST /donations`
- `POST /login`
- `GET /admin/dashboard`
- `POST /logout`
