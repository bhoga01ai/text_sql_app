# Text-to-SQL app

Ask questions about departments in plain English. gpt-4o-mini (OpenAI) writes SQL, the SQL runs
against a SQLite `dept` table (100 synthetic rows), and the model turns the result
into a friendly answer.

```
Frontend (Next.js) ──query──▶ sql_gen.py (PromptTemplate → OpenAI) ──SQL──▶ Data API (SQLite, read-only)
       ▲                                                                          │
       └──────── friendly answer ◀── output_gen.py (Query + SQL + rows → OpenAI) ◀┘
```

| Diagram box        | Code                                   |
| ------------------ | -------------------------------------- |
| Frontend           | `frontend/app/page.tsx`                |
| API/sql_gen.py     | `backend/app/sql_gen.py`               |
| Data API / dept DB | `backend/app/db.py`, `backend/data/company.db` |
| output_gen.py/API  | `backend/app/output_gen.py`            |
| Endpoint           | `POST /api/ask` in `backend/app/main.py` |

## Run

```bash
# Backend (port 8000)
cd backend
cp .env.example .env          # then put your OPENAI_API_KEY in .env
uv sync
uv run seed.py                # (re)creates data/company.db with 100 rows
uv run uvicorn app.main:app --reload

# Frontend (port 3000), in a second terminal
cd frontend
npm install
npm run dev
```

Open http://localhost:3000.

Model defaults to `gpt-4o-mini`; override with `OPENAI_MODEL` in `backend/.env`.
Generated SQL is restricted to a single `SELECT`/`WITH` statement and the database is
opened read-only.
