# Expense Tracker API

A secure Flask REST API for tracking personal expenses. Users sign up, log in, and manage their own expenses and categories. Authentication is **session-based** (a signed cookie), passwords are hashed with **Flask-Bcrypt**, and every user can only see and change their own data.

## Features

- Session-based authentication: signup, login, logout, and a check-session route
- Passwords hashed with bcrypt; the hash is never returned by any route
- Full CRUD for expenses and categories
- Paginated expense list
- Ownership checks on every route, so users cannot view or edit each other's records
- Validation with Marshmallow and clear HTTP status codes
- Database migrations with Flask-Migrate and demo data with a seed script
- Automated tests with pytest

## Tech stack

Python 3.8+, Flask 2.2.2, Flask-SQLAlchemy, Flask-Migrate, Flask-Bcrypt, Marshmallow, SQLite, pytest.

## Project structure

```
expense-tracker-api/
├── migrations/            # Flask-Migrate files
├── routes/
│   ├── auth.py            # /signup, /login, /logout, /check_session
│   ├── expenses.py        # /expenses routes
│   └── categories.py      # /categories routes
├── tests/
│   ├── conftest.py        # fixtures (test client, signup helper)
│   ├── test_auth.py
│   ├── test_expenses.py
│   └── test_categories.py
├── app.py                 # Flask app, config, extensions
├── models.py              # User, Category, Expense
├── helpers.py             # error(), get_json(), current_user(), login_required# Flask-Migrate files
├── seed.py                # demo data
├── Pipfile
└── README.md
```

## Installation

```bash
git clone https://github.com/godwillboro-source/expense-tracker-api.git
cd expense-tracker-api

pipenv install
pipenv shell

export FLASK_APP=app.py
flask db upgrade        # creates the database from the migrations/ folder
python seed.py          # optional: adds demo data
```

Windows PowerShell: use `$env:FLASK_APP = "app.py"` instead of `export`.


## Run the server

```bash
flask run --port 5555
```

The API is now at `http://127.0.0.1:5555`.

## Demo data

`python seed.py` resets the database and adds two users with sample categories and expenses. It is safe to run again.

| Username | Password |
|----------|----------|
| alice | password123 |
| bob | password123 |

## Models

| Model | Fields |
|-------|--------|
| **User** | `id`, `username` (unique), password hash (never returned) |
| **Category** | `id`, `name` (unique per user), `user_id` |
| **Expense** | `id`, `title`, `amount`, `date`, `user_id`, `category_id` (optional) |

A user has many categories and many expenses. A category has many expenses. Deleting a category keeps its expenses and sets their `category_id` to `null`.

## API reference

All request and response bodies are JSON. Routes marked **login required** return `401` if there is no valid session.

### Authentication

| Method | Path | Body | Success | Errors |
|--------|------|------|---------|--------|
| POST | `/signup` | `{username, password}` | 201 and the user. Logs you in | 409 username taken, 422 invalid |
| POST | `/login` | `{username, password}` | 200 and the user | 401 bad credentials, 422 missing fields |
| DELETE | `/logout` | none | 204 | none |
| GET | `/check_session` | none | 200 and the user | 401 not logged in |

Rules: username is 3 to 50 characters, password is 8 to 128 characters.

### Expenses (login required)

| Method | Path | Body or query | Success | Errors |
|--------|------|---------------|---------|--------|
| GET | `/expenses?page=1&per_page=10` | query: `page`, `per_page` | 200, paginated list | 400 bad page values |
| GET | `/categories/<id>/expenses?page=1&per_page=10` | query: `page`, `per_page` | 200, paginated expenses for your category | 400 bad page values, 404 category not found |
| POST | `/expenses` | `{title, amount, date?, category_id?}` | 201 and the expense | 422 invalid |
| GET | `/expenses/<id>` | none | 200 and the expense | 404 |
| PATCH | `/expenses/<id>` | any subset of the fields above | 200 and the updated expense | 404, 422 |
| DELETE | `/expenses/<id>` | none | 204 | 404 |

Rules: `title` is required (up to 100 characters), `amount` is required and must be greater than 0, `date` is `YYYY-MM-DD` and defaults to today, and `category_id` must be one of your own categories. Results are newest first, and `per_page` is capped at 100.

**Paginated response:**

```json
{
  "items": [
    {"id": 3, "title": "Lunch", "amount": 1255, "date": "2026-10-28", "category_id": 1}
  ],
  "page": 1,
  "per_page": 10,
  "total": 25,
  "pages": 3
}
```

### Categories (login required)

| Method | Path | Body | Success | Errors |
|--------|------|------|---------|--------|
| GET | `/categories` | none | 200, list of your categories | none |
| GET | `/categories/<id>` | none | 200 and the category | 404 |
| POST | `/categories` | `{name}` | 201 and the category | 409 duplicate name, 422 invalid |
| PATCH | `/categories/<id>` | `{name}` | 200 and the updated category | 403 not authorized, 404, 409, 422 |
| DELETE | `/categories/<id>` | none | 204 | 404 |

### Status codes

| Code | Meaning |
|------|---------|
| 200 / 201 / 204 | Success / created / deleted with no body |
| 400 | Bad query parameters, such as `page=abc` |
| 401 | Not logged in, or wrong username or password |
| 403 | The category exists but belongs to another user |
| 404 | Not found, or belongs to another user on endpoints that conceal ownership |
| 409 | Duplicate username or category name |
| 422 | The data failed validation |

Errors come back as `{"error": "message"}`, and validation errors also include a `details` object that says which field failed.

## Try it with curl

`-c` saves the session cookie and `-b` sends it back, like a browser would.

```bash
# Sign up (this also logs you in)
curl -c cookies.txt -X POST http://127.0.0.1:5555/signup \
  -H "Content-Type: application/json" \
  -d '{"username": "kim", "password": "password123"}'

# Create a category
curl -b cookies.txt -X POST http://127.0.0.1:5555/categories \
  -H "Content-Type: application/json" \
  -d '{"name": "Food"}'

# Add an expense
curl -b cookies.txt -X POST http://127.0.0.1:5555/expenses \
  -H "Content-Type: application/json" \
  -d '{"title": "Lunch", "amount": 12.5, "category_id": 1}'

# List expenses
curl -b cookies.txt "http://127.0.0.1:5555/expenses?page=1&per_page=10"

# Log out, then try again: you should get 401
curl -b cookies.txt -X DELETE http://127.0.0.1:5555/logout
curl -b cookies.txt http://127.0.0.1:5555/expenses
```
## Try with Postman
Test with Postman

Postman stores the session cookie after you log in, so later requests are logged in automatically.

Setup: start the server (flask run --port 5555), create a collection, and add a variable baseUrl = http://127.0.0.1:5555. For requests with a body, choose Body > raw > JSON.

| Step | Request | Body | Expect |
|------|---------|------|--------|
| Sign up (logs you in) | POST http://127.0.0.1:5555/signup | {"username": "kim", "password": "password123"} | 201 |
| Check session	| GET http://127.0.0.1:5555/check_session | none | 200 |
| Add category | POST http://127.0.0.1:5555/categories | {"name": "Food"} | 201 |
| Add expense | POST http://127.0.0.1:5555/expenses | {"title": "Lunch", "amount": 12.5, "category_id": 1} | 201 |
| List (paginated) | GET http://127.0.0.1:5555/expenses?page=1&per_page=10 | none | 200 |
| Update | PATCH http://127.0.0.1:5555/expenses/1	 | {"amount": 15} | 200 |
| Delete | DELETE http://127.0.0.1:5555/expenses/1 | none | 204  |
| Log out | DELETE http://127.0.0.1:5555/logout | none | 204 |, then /expenses gives 401

## How authentication and security work

- **Sessions:** after signup or login, Flask stores `user_id` in a cookie signed with `SECRET_KEY`. The browser sends it automatically on each request. The cookie is signed, not encrypted, so only the id is stored.
- **Protected routes:** the `@login_required` decorator reads the session, loads the user, and returns `401` if there isn't one.
- **Passwords:** hashed with bcrypt through the model's `password_hash` setter. The plain password is never stored, and the hash is never returned.
- **Ownership:** every query filters by the logged-in user's id. Another user's record returns `404`, so its existence isn't revealed.
- **Categories:** an expense can only use a category that belongs to the same user.
- **Login errors:** an unknown username and a wrong password return the same message, so usernames can't be guessed.

## Tests

```bash
pytest
```


## Database migrations

After changing a model:

```bash
flask db migrate -m "describe the change"
flask db upgrade
```
