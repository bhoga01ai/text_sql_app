import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

_client: OpenAI | None = None


def complete(prompt: str) -> str:
    """Send a single prompt to the model and return its text output."""
    global _client
    if _client is None:
        _client = OpenAI()  # reads OPENAI_API_KEY from the environment
    response = _client.responses.create(model=MODEL, input=prompt, temperature=0)
    return response.output_text or ""
