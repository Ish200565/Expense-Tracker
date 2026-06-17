# AI Expense Tracker
A REST API for tracking personal expenses with JWT authentication and AI-powered receipt scanning.

**Live demo:** `https://ish200565.github.io/Expense-Tracker`
**Live API:** `https://ai-expense-tracker-fgcf.onrender.com`

## What it does
The AI Expense Tracker is a personal finance management API that allows users to register, log in securely using JWT authentication, and keep track of their expenses. Users can add, modify, delete, and categorize their spending, as well as retrieve expense summaries to gain insights into their financial habits.

## Tech stack

**Backend**
- Python, Flask, Gunicorn
- PostgreSQL, SQLAlchemy, Flask-Migrate
- Flask-JWT-Extended, bcrypt, Flask-CORS

**AI**
- Groq LLM — llama-4-scout vision model for receipt scanning and NLP queries
- ChromaDB — vector database for semantic expense search
- fastembed — lightweight local text embeddings

**Frontend**
- Vanilla HTML, CSS, JavaScript — single page, no framework
- Deployed on GitHub Pages

**Infrastructure**
- API deployed on Render
- Database on Render PostgreSQL
- Frontend on GitHub Pages

## How to run locally

1. **Clone the repository:**
```bash
   git clone https://github.com/ish200565/Expense-Tracker.git
   cd Expense-Tracker
```

2. **Create and activate a virtual environment:**
```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Mac/Linux:
   source venv/bin/activate
```

3. **Install dependencies:**
```bash
   pip install -r requirements.txt
```

4. **Create a `.env` file in the root folder:**
```env
   SQLALCHEMY_DATABASE_URI=postgresql://username:password@localhost:5432/expense_tracker
   JWT_SECRET_KEY=your_secret_key_min_32_characters
   GROQ_API_KEY=your_groq_api_key
   DEBUG_KEEP_FILES=false
```

5. **Run database migrations:**
   ```bash
   flask db upgrade
   ```
6. **Start the application:**
   ```bash
   python run.py
   ```

7. **Open `index.html` in your browser to use the frontend.**

---

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
### AI Insights
*All routes require Bearer token.*

- `GET /summary` — AI analyses all your expenses and returns a friendly 3-4 sentence summary with spending insights and a money saving tip.
- `POST /ask` — Ask a natural language question about your expenses.
```json
  { "question": "how much did I spend on food?" }
```
  Powered by ChromaDB semantic search + Groq LLM. Returns a specific answer based on your actual expense data.

## Deployment
Deployed on Render with PostgreSQL. Auto-deploys on every push to main branch.

## Note on free tier

The API is hosted on Render's free tier which sleeps after 15 minutes of inactivity. The first request after sleep may take 30-50 seconds to respond. Subsequent requests are fast.