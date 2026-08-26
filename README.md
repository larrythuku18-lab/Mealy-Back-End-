# Mealy Backend API

Flask REST API backend for the Mealy meal ordering platform. Provides authentication, meal management, order processing, and admin dashboard endpoints.

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

# Initialize database with seed data
flask seed

# Run the server
python app.py
```

The server starts at `http://localhost:5000`.

## API Endpoints

### Auth (`/api/auth`)

| Method | Endpoint      | Description              | Auth Required |
|--------|---------------|--------------------------|---------------|
| POST   | `/register`   | Register a new user      | No            |
| POST   | `/login`      | Login with email/password| No            |
| POST   | `/logout`     | Logout current session   | Yes           |
| GET    | `/me`         | Get current user info    | Yes           |

### Users (`/api/users`)

| Method | Endpoint      | Description              | Auth Required |
|--------|---------------|--------------------------|---------------|
| GET    | `/profile`    | Get user profile         | Yes           |
| PUT    | `/profile`    | Update user profile      | Yes           |

### Menus (`/api/menus`)

| Method | Endpoint      | Description              | Auth Required |
|--------|---------------|--------------------------|---------------|
| GET    | `/`           | List all meal options    | No            |
| POST   | `/`           | Create a meal option     | Yes (Admin)   |
| GET    | `/:id`        | Get a meal option        | No            |
| PUT    | `/:id`        | Update a meal option     | Yes (Admin)   |
| DELETE | `/:id`        | Delete a meal option     | Yes (Admin)   |
| GET    | `/today`      | Get today's published menu | No          |
| POST   | `/publish`    | Publish today's menu     | Yes (Admin)   |

### Orders (`/api/orders`)

| Method | Endpoint      | Description              | Auth Required |
|--------|---------------|--------------------------|---------------|
| GET    | `/`           | List user's orders       | Yes           |
| POST   | `/`           | Create a new order       | Yes           |
| GET    | `/:id`        | Get a specific order     | Yes           |
| GET    | `/today`      | Get today's orders       | Yes (Admin)   |
| PUT    | `/:id/status` | Update order status      | Yes (Admin)   |

### Reviews (`/api/reviews`)

| Method | Endpoint          | Description              | Auth Required |
|--------|-------------------|--------------------------|---------------|
| POST   | `/`               | Create a review          | Yes           |
| GET    | `/:meal_option_id`| Get reviews for a meal   | No            |

### Categories (`/api/categories`)

| Method | Endpoint | Description              | Auth Required |
|--------|----------|--------------------------|---------------|
| GET    | `/`      | List all categories      | No            |
| POST   | `/`      | Create a category        | Yes (Admin)   |

### Royalties (`/api/royalties`)

| Method | Endpoint      | Description              | Auth Required |
|--------|---------------|--------------------------|---------------|
| GET    | `/`           | List user's royalties    | Yes           |
| POST   | `/`           | Create royalty record    | Yes           |
| GET    | `/:id`        | Get a royalty record     | Yes           |

## Request/Response Format

### Register
```json
POST /api/auth/register
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "secure123",
  "phone": "+254 700 000 000",
  "role": "user"
}
```

### Login
```json
POST /api/auth/login
{
  "email": "john@example.com",
  "password": "secure123"
}
```

### Create Order
```json
POST /api/orders
Authorization: Bearer <token>
{
  "mealOptionIds": [1, 2],
  "quantities": [2, 1]
}
```

## User Roles
- **user**: Can browse menu, place orders, view order history, leave reviews
- **admin**: Can manage meal options, publish daily menus, view all orders, update order statuses

## Order Status Flow
`confirmed` → `preparing` → `in_transit` → `delivered`

## Development

```bash
# Run in development mode
export FLASK_ENV=development
python app.py

# Seed database
flask seed
```
