"""Step 2 of the diagram: Query + SQL + output -> LLM -> friendly answer."""

import json

from .llm import complete

PROMPT_TEMPLATE = """You are a helpful data assistant. A user asked a question, a SQL
query was run against the company's `dept` table, and these are the results.
Write a short, friendly, plain-English answer to the user's question based ONLY
on the results. If the results are empty, say no matching data was found.
Don't mention SQL unless it helps. The data is read-only: if the user asked to
change or delete data, say that this assistant can only look data up.
Write plain text with no markdown (no asterisks or headings); use simple
"- " lines if you need a list. The query returned {total} rows in total; only
the first {n} are shown below, so use {total} for any count of results.

Question: {query}

SQL: {sql}

Columns: {columns}
Rows: {rows}
"""

MAX_PROMPT_ROWS = 50


def generate_answer(query: str, sql: str, columns: list[str], rows: list[list]) -> str:
    prompt = PROMPT_TEMPLATE.format(
        query=query,
        sql=sql,
        columns=columns,
        total=len(rows),
        n=min(len(rows), MAX_PROMPT_ROWS),
        rows=json.dumps(rows[:MAX_PROMPT_ROWS], default=str),
    )
    return complete(prompt).strip()
