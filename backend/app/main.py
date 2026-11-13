import sqlite3

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .db import UnsafeSQLError, run_query
from .llm import MODEL
from .output_gen import generate_answer
from .sql_gen import generate_sql

app = FastAPI(title="Text-to-SQL API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    query: str = Field(min_length=1, max_length=1000)


class AskResponse(BaseModel):
    query: str
    sql: str
    columns: list[str]
    rows: list[list]
    answer: str
    model: str


@app.get("/api/health")
def health():
    return {"status": "ok", "model": MODEL}


@app.post("/api/ask", response_model=AskResponse)
def ask(req: AskRequest):
    try:
        sql = generate_sql(req.query)
    except Exception as e:
        raise HTTPException(502, f"SQL generation failed: {e}")

    try:
        columns, rows = run_query(sql)
    except UnsafeSQLError as e:
        raise HTTPException(400, f"{e} Generated SQL: {sql}")
    except sqlite3.Error as e:
        raise HTTPException(400, f"SQL error: {e}. Generated SQL: {sql}")

    try:
        answer = generate_answer(req.query, sql, columns, rows)
    except Exception as e:
        raise HTTPException(502, f"Answer generation failed: {e}")

    return AskResponse(
        query=req.query, sql=sql, columns=columns, rows=rows, answer=answer, model=MODEL
    )
