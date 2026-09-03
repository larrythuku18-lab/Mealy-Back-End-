# Mealy Backend API

Flask REST API backend for the Mealy meal ordering platform. Provides authentication, meal management, order processing, M-Pesa payments, and admin dashboard endpoints.

## Setup

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/larrythuku18-lab/Mealy-Back-End-.git
cd Mealy-Back-End-

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your values

# Initialize database with seed data (dev only — see warning below)
flask seed

# Run the server
python app.py
```

The server starts at `http://localhost:5000`.

> **Warning:** `flask seed` **drops and recreates all tables** before inserting
> sample data. Only run it against a fresh or development database — never
> against production data.

### Seed accounts

| Email            | Password  | Role  |
|------------------|-----------|-------|
| admin@mealy.com  | admin123  | admin |
| kev@mealy.com    | user123   | user  |
| eugene@mealy.com | user123   | user  |
| larry@mealy.com  | user123   | user  |
| joy@mealy.com    | user123   | user  |

> **Frontend compatibility:** the deployed Mealy frontend calls the auth, menu,
> and order endpoints **without** the `/api` prefix and uses a singular `/menu`
> path. Those routes are mounted under both prefixes, so `/auth/register`,
> `/menu/today`, `/orders/`, etc. work exactly like their `/api/*` equivalents.
> All other endpoints are only available under `/api/*`.

## Authentication

All protected endpoints expect an `Authorization: Bearer <token>` header. Tokens are
returned by `POST /api/auth/register` and `POST /api/auth/login`, expire after
`JWT_ACCESS_TOKEN_EXPIRES` seconds (default 3600), and are stateless — `logout` does not
invalidate a token server-side.

**Admin-only** endpoints additionally require the token to belong to a user with
`role: admin` (403 otherwise).

## API Endpoints

### System

| Method | Endpoint     | Description                | Auth Required |
|--------|--------------|----------------------------|---------------|
| GET    | `/`          | Service info & status      | No            |
| GET    | `/health`    | Health check               | No            |
| GET    | `/api/health`| Health check (Vercel)      | No            |

### Auth (`/api/auth`)

| Method | Endpoint   | Description                        | Auth Required |
|--------|------------|------------------------------------|---------------|
| POST   | `/register`| Register a new user                | No            |
| POST   | `/login`   | Login with email/password          | No            |
| POST   | `/logout`  | Logout current session             | Yes           |
| GET    | `/me`      | Get current user info              | Yes           |

### Users (`/api/users`)

| Method | Endpoint   | Description                        | Auth Required |
|--------|------------|------------------------------------|---------------|
| GET    | `/profile` | Get current user's profile         | Yes           |
| PUT    | `/profile` | Update profile (name, email, phone, address) | Yes    |

### Menus (`/api/menus`)

All menu endpoints are scoped to the caterer the user belongs to (`caterer_id`).
A user not associated with a caterer gets `400`.

| Method | Endpoint                  | Description                       | Auth Required |
|--------|---------------------------|-----------------------------------|---------------|
| GET    | `/`                       | List meal options for user's caterer | Yes        |
| POST   | `/`                       | Create a meal option              | Yes (Admin)   |
| GET    | `/<meal_option_id>`       | Get a meal option                 | Yes           |
| PUT    | `/<meal_option_id>`       | Update a meal option              | Yes (Admin)   |
| DELETE | `/<meal_option_id>`       | Delete a meal option              | Yes (Admin)   |
| GET    | `/today`                  | Today's published menu            | Yes           |
| GET    | `/date/<YYYY-MM-DD>`      | Published menu for a specific date| Yes           |
| POST   | `/publish`                | Publish a menu for a date (notifies customers) | Yes (Admin) |

### Orders (`/api/orders`)

| Method | Endpoint               | Description                       | Auth Required |
|--------|------------------------|-----------------------------------|---------------|
| GET    | `/`                    | List current user's orders        | Yes           |
| POST   | `/`                    | Create a new order                | Yes           |
| GET    | `/<order_id>`          | Get an order (own, or any as admin) | Yes         |
| PUT    | `/<order_id>/status`   | Update order status               | Yes (Admin)   |
| PUT    | `/<order_id>/change-meal` | Change meal choice on own order | Yes         |
| GET    | `/today`               | Today's orders with customer names| Yes (Admin)   |
| GET    | `/history`             | All customer orders               | Yes (Admin)   |
| GET    | `/today/sales`         | Today's total orders & revenue    | Yes (Admin)   |

### Reviews (`/api/reviews`)

| Method | Endpoint              | Description                       | Auth Required |
|--------|-----------------------|-----------------------------------|---------------|
| POST   | `/`                   | Create a review (one per user per meal) | Yes     |
| GET    | `/<meal_option_id>`   | Get reviews for a meal option     | No            |

### Categories (`/api/categories`)

| Method | Endpoint | Description              | Auth Required |
|--------|----------|--------------------------|---------------|
| GET    | `/`      | List all categories      | No            |
| POST   | `/`      | Create a category        | Yes (Admin)   |

### Royalties (`/api/royalties`)

| Method | Endpoint       | Description                       | Auth Required |
|--------|----------------|-----------------------------------|---------------|
| GET    | `/`            | List current user's royalties     | Yes           |
| POST   | `/`            | Create a royalty record (own order only) | Yes     |
| GET    | `/<royalty_id>`| Get a royalty record (own, or any as admin) | Yes  |

### Payments — M-Pesa (`/api/payments`)

| Method | Endpoint     | Description                       | Auth Required |
|--------|--------------|-----------------------------------|---------------|
| POST   | `/stk-push`  | Initiate an STK push for an order (own order only) | Yes |
| POST   | `/callback`  | Safaricom payment callback        | No            |

The `/callback` endpoint is called by Safaricom's servers — do **not** send an
`Authorization` header when testing it manually.

### Notifications (`/api/notifications`)

| Method | Endpoint | Description                       | Auth Required |
|--------|----------|-----------------------------------|---------------|
| GET    | `/`      | List current user's notifications | Yes           |

### Sales (`/api/sales`)

| Method | Endpoint | Description                       | Auth Required |
|--------|----------|-----------------------------------|---------------|
| GET    | `/today` | Today's total orders & revenue    | Yes (Admin)   |

## Request/Response Format

### Register
```json
POST /api/auth/register
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "secure123",
  "phone": "+254 700 000 000",
  "address": "Westlands, Nairobi"
}
```
Response: `201` with `{ "token": "<jwt>", "user": {...} }`.
The optional `role` field accepts only safe roles — `user`, `customer`, or
`caterer` (defaults to `user`). Requesting `admin` (or any other value) is
rejected with `400`; admin accounts are created via seed, never public signup.

### Login
```json
POST /api/auth/login
{
  "email": "john@example.com",
  "password": "secure123"
}
```
Response: `200` with `{ "token": "<jwt>", "user": {...} }`.

### Create Order
```json
POST /api/orders
Authorization: Bearer <token>
{
  "mealOptionIds": [1, 2],
  "quantities": [2, 1]
}
```
Response: `201` with the created order including its items.

### Update Order Status (admin)
```json
PUT /api/orders/42/status
Authorization: Bearer <token>
{
  "status": "preparing"
}
```

### Publish Menu (admin)
```json
POST /api/menus/publish
Authorization: Bearer <token>
{
  "date": "2026-09-03",
  "mealOptionIds": [1, 2, 3]
}
```

### Initiate M-Pesa STK Push
```json
POST /api/payments/stk-push
Authorization: Bearer <token>
{
  "order_id": 42,
  "phone_number": "254700000000"
}
```
Response: `200` with the payment record and the Safaricom response.

## User Roles
- **user**: View menus, place orders, change meal choice, view own order history, leave reviews, earn and view royalties, pay via M-Pesa, view notifications, update profile
- **admin**: All of the above, plus: manage meal options, publish daily menus, manage categories, view all orders and sales dashboards, update order statuses

## Order Status Flow
`confirmed` → `preparing` → `in_transit` → `delivered`

Valid statuses (used by `PUT /api/orders/<id>/status`):
`confirmed`, `preparing`, `in_transit`, `delivered`

## Development

```bash
# Run in development mode
export FLASK_ENV=development
python app.py

# Seed database (drops existing tables — dev only)
flask seed
```

If `DATABASE_URL` is not set, the app falls back to a local SQLite database
(`instance/mealy.db`). For M-Pesa testing, set `MPESA_ENVIRONMENT=sandbox` and use a
Safaricom sandbox test number.

## Deployment (Vercel)

The repo includes a Vercel serverless config (`vercel.json` + `api/index.py`).
To deploy:

1. Create the Vercel project from this repo, or import it in the Vercel dashboard.
2. **Name the project `mealy-back-end`** — the deployed frontend hardcodes the API
   base URL `https://mealy-back-end.vercel.app/`, so the project name must match
   exactly (hyphens included).
3. Set the following environment variables in the Vercel project settings
   (Framework Preset: Other):

   | Variable | Example value |
   |----------|---------------|
   | `DATABASE_URL` | `postgresql://...` (Neon) |
   | `SECRET_KEY` | any long random string |
   | `JWT_SECRET_KEY` | any long random string |
   | `CORS_ORIGINS` | `https://mealy-front-end-build.vercel.app` |
   | `MPESA_CONSUMER_KEY` | Safaricom sandbox key |
   | `MPESA_CONSUMER_SECRET` | Safaricom sandbox secret |
   | `MPESA_SHORTCODE` | e.g. `174379` |
   | `MPESA_PASSKEY` | Safaricom sandbox passkey |
   | `MPESA_CALLBACK_URL` | `https://mealy-back-end.vercel.app/api/payments/callback` |
   | `MPESA_ENVIRONMENT` | `sandbox` (or `production`) |

   Without `SECRET_KEY`/`JWT_SECRET_KEY` the app falls back to insecure dev
   defaults — always set them in production.
4. Deploy. Tables are created automatically on first request (`db.create_all()`).