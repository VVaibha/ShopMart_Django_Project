# ShopMart — Django E-commerce Store (No JavaScript)

A full-stack e-commerce web app built **entirely with server-side Django +
Bootstrap** — every interaction (add to cart, update quantity, checkout,
review, cancel order, currency switch) is a plain HTML form POST/redirect.
No JavaScript is used anywhere except Bootstrap's own bundle (needed only
for the navbar toggle/dropdown to open).

## Features

- **Admin login** via Django's built-in `/admin/` panel
- **User registration, login, logout**
- Product catalog with categories and search
- **Add to cart, update quantity, remove from cart** — all via forms, page reloads
- **Checkout with payment method selection** (Cash on Delivery / UPI / Card / Net Banking)
- **Order history + Cancel Order** (restores stock, only allowed before shipping)
- **Product reviews / feedback** — logged-in users can rate (1–5 stars) and comment on any product
- **Live currency conversion** (INR / USD / EUR / GBP) — calls a real external
  exchange-rate API (open.er-api.com, no key required) **entirely server-side**;
  chosen currency is stored in the session and every price is converted
  before the template renders it
- Deployment-ready: Gunicorn + Whitenoise + Procfile + env-based settings

## Project Structure

```
shopmart_project/
├── manage.py
├── requirements.txt
├── shopmart_project/         # settings, urls, wsgi
└── store/
    ├── models.py             # Category, Product, Order, OrderItem, Review
    ├── views.py               # all pages (function-based, form + redirect)
    ├── cart.py                 # session-based cart
    ├── currency.py              # server-side exchange-rate API integration
    ├── templatetags/store_extras.py   # {% price %} tag — converts & formats currency
    ├── templates/
    └── static/store/css/
```

## Run Locally in VS Code

```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
copy .env.example .env         # Windows: copy | macOS/Linux: cp

python manage.py makemigrations store
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_products
python manage.py runserver
```

Visit **http://127.0.0.1:8000/** for the store, and
**http://127.0.0.1:8000/admin/** to manage products, orders, and reviews.

> Add product images from the admin panel (Products → open a product →
> upload under "Image" → Save).

## How key features work (for your resume / interview talking points)

- **Cart & checkout:** implemented with Django sessions — no database write
  until checkout, then `Order` + `OrderItem` rows are created and product
  stock is decremented.
- **Order cancellation:** a POST-only view checks `order.can_cancel`
  (status must be `pending` or `paid`), restores stock, and sets status to
  `cancelled`.
- **Reviews/feedback:** one review per user per product (`unique_together`
  constraint), average rating computed with a Django `Avg` aggregate and
  shown as stars on both the listing and detail pages.
- **API integration:** `store/currency.py` calls the free exchange-rate API
  with the `requests` library, caches the result for 6 hours with Django's
  cache framework, and a custom template tag (`{% price %}`) converts and
  formats every price server-side — demonstrating consuming a third-party
  REST API from a Django backend without any client-side code.

## Deploying (Render — free tier example)

1. Push this project to a GitHub repository.
2. On [Render](https://render.com), create a **New Web Service** from that repo.
3. Set:
   - **Build Command:** `./build.sh`
   - **Start Command:** `gunicorn shopmart_project.wsgi`
4. Add environment variables:
   - `SECRET_KEY` — any long random string
   - `DEBUG` — `False`
   - `ALLOWED_HOSTS` — your Render URL, e.g. `shopmart.onrender.com`
   - `DATABASE_URL` — Render provides this automatically if you attach a free Postgres database
5. Deploy. Render runs `build.sh` then starts Gunicorn.

The same `Procfile` also works on Heroku and Railway with minimal changes.

## Tech Stack Summary

Python · Django · Bootstrap 5 · Django Forms & Sessions · SQLite/PostgreSQL ·
REST API consumption (requests) · Gunicorn · Whitenoise · Git deployment
