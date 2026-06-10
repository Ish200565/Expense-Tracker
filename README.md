# AI Expense Tracker
A REST API for tracking personal expenses with JWT authentication and AI-powered receipt scanning.

## What it does
The AI Expense Tracker is a personal finance management API that allows users to register, log in securely using JWT authentication, and keep track of their expenses. Users can add, modify, delete, and categorize their spending, as well as retrieve expense summaries to gain insights into their financial habits.

## Tech stack
- Python, Flask
- PostgreSQL, SQLAlchemy, Flask-Migrate
- Flask-JWT-Extended, bcrypt
- python-dotenv

## How to run locally
1. **Navigate to the project directory:**
   ```bash
   cd Expense-Tracker
   ```
2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure environment variables:**
   Create a `.env` file in the root folder with the following variables:
   ```env
   SQLALCHEMY_DATABASE_URI=postgresql://username:password@localhost:5432/expense_tracker
   JWT_SECRET_KEY=your_super_secret_key_here
   ```
5. **Run database migrations:**
   ```bash
   flask db upgrade
   ```
6. **Start the application:**
   ```bash
   python run.py
   ```

## API endpoints

### Authentication
- `POST /register` — Register a new user with an email and password.
- `POST /login` — Authenticate a user and return a JWT access token.

### Expenses
*Note: All expense routes require a valid JWT token in the `Authorization: Bearer <token>` header.*
*Do not wrap the token in quotes. Paste it raw into the Bearer field.*

- `GET /expenses` — Retrieve all expenses for the authenticated user.
- `POST /expenses` — Add a new expense (requires `amount` and `category` in JSON body).
- `PATCH /expenses/<int:expense_id>` — Update an existing expense's amount or category.
- `DELETE /expenses/<int:expense_id>` — Delete a specific expense.
- `GET /expenses/category/<string:category>` — Retrieve all expenses matching a specific category.
- `GET /expenses/summary` — Retrieve an aggregated summary showing total spending and a category breakdown.

### AI Receipt Scanner
*Requires `Authorization: Bearer <token>` header. Send file as `multipart/form-data`.*

- `POST /upload-receipt` — Upload a receipt photo (jpg/png only).
  AI extracts all items and amounts and saves them as expenses automatically.

  Tested receipt types: restaurant, grocery, electricity, hospital,
  jewellery, handwritten/faulty bills.

  **Postman setup:**
  Body → form-data → Key: receipt (type: File) → select image
```
