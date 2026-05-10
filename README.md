# SeizeDeals - Django E-Commerce Platform

SeizeDeals is a full-stack e-commerce website built with Python and Django. It’s designed to be a complete online store where users can browse products by category, pick different sizes or colors, and buy items securely using Razorpay.

I built this project to handle the entire shopping process—from user accounts and email verifications to order tracking and automated invoices. It also includes a custom admin dashboard with extra security features like a honeypot to keep the backend safe from unauthorized access.

> **Internship Project** - Elite Softwares Pvt. Ltd., Pune | Dec 2024 - Feb 2025

---

## Live Demo

> Coming soon - deployment in progress

---

## Screenshots

| Home Page | Product Detail | Cart |
|-----------|---------------|------|
| ![Home](docs/screenshots/home.png) | ![Product](docs/screenshots/product.png) | ![Cart](docs/screenshots/cart.png) |

| Payment Gateway | Order Invoice | Admin Dashboard |
|----------------|--------------|----------------|
| ![Payment](docs/screenshots/payment.png) | ![Invoice](docs/screenshots/invoice.png) | ![Admin](docs/screenshots/admin.png) |

---

## Features

### User
- Secure registration & login with email verification
- User profile management with shipping address
- Browse products by category
- Add to cart with size/color variation selection
- Checkout with Razorpay payment gateway (UPI, Cards, Net Banking)
- Order confirmation & payment emails sent automatically
- Order history and invoice view

### Admin
- Custom admin dashboard (full CRUD for products, categories, orders)
- View registered users and their order/payment status
- Manage contact form submissions
- Role-based access control

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.10+, Django 3.1 |
| Frontend | HTML5, CSS3, Bootstrap 4, JavaScript, jQuery |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Payment | Razorpay API |
| Email | Django SMTP + Gmail |
| CI/CD | GitHub Actions (Automated Testing) |
| Image Handling | Pillow |
| Deployment | Ready for Render / PythonAnywhere |

---

## Project Architecture

```
SeizeDeals/
+-- .github/workflows/  # GitHub Actions (CI/CD)
+-- accounts/           # Custom user model, auth, user profiles
+-- store/              # Products, categories, variations, reviews
+-- carts/              # Cart, CartItem, session management
+-- orders/             # Order, OrderProduct, Payment models
+-- seizedeals/         # Django project settings & URLs
+-- templates/          # HTML templates
+-- static/             # CSS, JS, images
+-- media/              # Product images
+-- fixtures/           # Demo data (categories, products, variations)
+-- requirements.txt
+-- .env-sample
```

### Key Design Patterns
- **MVT Architecture** - Django's Model-View-Template pattern
- **CI/CD Integration** - Automated build and system checks via GitHub Actions
- **OOP** - All core entities modelled as Django classes
- **Session-based Cart** - Works for both guests and logged-in users
- **Razorpay Signature Verification** - Server-side HMAC validation for payment security

---

## Local Setup

### Prerequisites
- Python 3.10+
- pip
- Git

### Steps

**1. Clone the repository**
```bash
git clone https://github.com/AayanM05/SeizeDeals-E-commerce-Platform.git
cd SeizeDeals
```

**2. Create and activate a virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Configure environment variables**
```bash
# Windows
copy .env-sample .env

# macOS / Linux
cp .env-sample .env
```
Then open `.env` and fill in your actual values (see Environment Variables section below).

**5. Apply database migrations**
```bash
python manage.py migrate
```

**6. Load demo data (categories, products, variations)**
```bash
python manage.py loaddata fixtures/initial_data.json
```

**7. Create an admin account**
```bash
python manage.py createsuperuser
```

**8. Run the development server**
```bash
python manage.py runserver
```

Open your browser at: **http://127.0.0.1:8000/**  
Real admin panel: **http://127.0.0.1:8000/securelogin/**  

**Security note:** `http://127.0.0.1:8000/admin/` is a honeypot — it shows a fake login page that logs every access attempt. The real admin is at `/securelogin/`.

---

## Environment Variables

Create a `.env` file in the root directory (use `.env-sample` as reference):

```env
# Django Core
SECRET_KEY=your_django_secret_key
DEBUG=True

# Email (Gmail SMTP)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_USE_TLS=True
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_gmail_app_password

# Razorpay Payment Gateway
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret
```

---

## Database Models

### `Account` (Custom User)
Extends `AbstractBaseUser` - uses email as primary login field instead of username.

### `Product` & `Variation`
Products support multiple variations (color, size) linked via `ManyToManyField` on CartItem.

### `Cart` & `CartItem`
Session-based for guests, user-linked for authenticated users. Handles quantity and variation management.

### `Order` & `Payment`
Full order lifecycle: New > Accepted > Completed. Payment stores Razorpay transaction ID and status.

---

## Developer

**Aayan Mulla**
BE Computer Engineering (AI & Data Science)
Dr. D. Y. Patil College of Engineering and Innovation, Pune

[![GitHub](https://img.shields.io/badge/GitHub-Follow-black)](https://github.com/AayanM05)
[![Email](https://img.shields.io/badge/Email%20Me-D14836?style=flat&logo=gmail&logoColor=white)](mailto:aayanmulla7777@gmail.com)

---

## License

This project is open source and available under the [MIT License](LICENSE).
