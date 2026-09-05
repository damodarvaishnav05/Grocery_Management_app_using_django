# 🛒 Om Super Mart

Om Super Mart is a modern AI-powered hypermarket grocery delivery web application built with Django. It allows customers to browse products, manage carts and wishlists, apply daily coupons, earn referral cashbacks (Refer & Earn ₹50), place orders, track delivery via real-time live GPS map, and receive AI-assisted shopping recommendations.


## 🚀 Features

### 👤 Authentication
- User Registration
- User Login / Logout
- Google OAuth Login
- User Profile Management

### 🛍 Product Management
- Browse Products
- Product Categories
- Product Search
- Product Details
- Product Images

### ❤️ Wishlist
- Add Products to Wishlist
- Remove Products from Wishlist
- User-specific Wishlist

### 🛒 Shopping Cart
- Add to Cart
- Update Quantity
- Remove Products
- Cart Total Calculation

### 🎟 Coupon System
- Daily Auto-Generated Coupon
- Coupon Validation
- Discount Calculation
- Session-based Coupon Application
- Coupon Removed on Logout

### 📦 Orders
- Checkout
- Order Placement
- Order History
- Order Success Page

### 🤖 AI Shopping Assistant
- Product Recommendations
- Shopping Guidance
- AI Powered Suggestions

### 🔐 Admin Dashboard
- Product Management
- Category Management
- Order Management
- User Management
- Coupon Management



# 🏗 Tech Stack

### Backend
- Python 3.11+
- Django 5+

### Database
- SQLite (Development)
- PostgreSQL (Production Ready)

### Frontend
- HTML5
- CSS3
- Bootstrap 5
- JavaScript

### Authentication
- Django Authentication
- Google OAuth

### AI
- OpenAI API



# ⚙ Installation

## 1. Clone Repository

```bash
git clone https://github.com/yourusername/freshmart.git

cd freshmart
```



## 2. Create Virtual Environment

### Windows

```bash
python -m venv venv
```

Activate:

```bash
venv\Scripts\activate
```

### Linux / Mac

```bash
python3 -m venv venv

source venv/bin/activate
```



## 3. Install Dependencies

```bash
pip install -r requirements.txt
```



## 4. Configure Environment Variables

Create:

```bash
.env
```

Example:

```env
SECRET_KEY=your_secret_key

DEBUG=True

OPENAI_API_KEY=your_openai_api_key

GOOGLE_CLIENT_ID=your_google_client_id

GOOGLE_CLIENT_SECRET=your_google_client_secret
```



## 5. Apply Migrations

```bash
python manage.py makemigrations

python manage.py migrate
```



## 6. Create Superuser

```bash
python manage.py createsuperuser
```

Follow prompts:

```text
Username:
Email:
Password:
```



## 7. Run Development Server

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

Admin:

```text
http://127.0.0.1:8000/admin/
```



# 📸 Media Files

Product images are stored in:

```text
media/
```

Ensure settings.py contains:

```python
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
```



# 🛠 Common Commands

### Run Server

```bash
python manage.py runserver
```

### Make Migrations

```bash
python manage.py makemigrations
```

### Migrate Database

```bash
python manage.py migrate
```

### Create Superuser

```bash
python manage.py createsuperuser
```

### Open Django Shell

```bash
python manage.py shell
```

### Collect Static Files

```bash
python manage.py collectstatic
```

### Check Project Errors

```bash
python manage.py check
```

### Run Tests

```bash
python manage.py test
```



# 🎟 Daily Coupon System

FreshMart generates a unique coupon every day.

Example:

```text
FRESH0808
```

Benefits:

- Changes daily
- 10% Discount
- Visible only to logged-in users
- Removed automatically after logout



# 🔒 Security Features

- CSRF Protection
- Session Authentication
- Google OAuth Authentication
- Protected Checkout
- User-specific Orders
- User-specific Wishlist
- User-specific Cart


# 🚀 Deployment

Recommended Platforms:

### Render

```text
✔ Best for Django
✔ PostgreSQL Support
✔ Free Tier Available
✔ GitHub Auto Deploy
```

### Railway

```text
✔ Easy Setup
✔ PostgreSQL Support
```

### Vercel

```text
⚠ Possible but not recommended for full Django projects
```


# Git Workflow

### Check Status

```bash
git status
```

### Add Changes

```bash
git add .
```

### Commit Changes

```bash
git commit -m "Updated feature"
```

### Push to GitHub

```bash
git push origin main
```

### Pull Latest Changes

```bash
git pull origin main
```


# Future Enhancements

- Razorpay Integration
- Stripe Payments
- Email Notifications
- Order Tracking
- Delivery Partner Module
- Product Reviews
- Inventory Management
- Multi-Vendor Support
- Mobile Application



# Author

### Made By Damodar Shravandas Vaishnav

AI-Powered Grocery Delivery Platform built using Django.