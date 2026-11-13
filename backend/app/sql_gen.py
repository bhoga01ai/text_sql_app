"""Step 1 of the diagram: question -> PromptTemplate -> LLM -> SQL."""

import re

from .db import SCHEMA
from .llm import complete

PROMPT_TEMPLATE = """<Instructions>
You are an expert SQLite analyst. Generate ONE SQLite SELECT query that answers
the user's question. I have a table called dept with this schema:

{schema}

Rules:
- Return only the SQL, no explanation and no markdown fences.
- Read-only: SELECT (or WITH ... SELECT) only.
- Use case-insensitive matching (LIKE or LOWER()) for text searches on name/description.
- Department ids are zero-padded text, e.g. '007'.
- Block all user requests that are queries about the dept table and number of rows and number of departments. If the user asks for anything else, respond with "I can only answer questions about the dept table."
</Instructions>

<Query>
{query}
</Query>
"""


def generate_sql(query: str) -> str:
    prompt = PROMPT_TEMPLATE.format(schema=SCHEMA, query=query)
    return _clean(complete(prompt))


def _clean(text: str) -> str:
    text = text.strip()
    fenced = re.search(r"```(?:sql)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if fenced:
        text = fenced.group(1).strip()
    return text.rstrip(";").strip()
