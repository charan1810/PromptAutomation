# prompt_multi_tables.py
import os
from typing import List
from openai import OpenAI
import PyPDF2
from typing import BinaryIO

# Initialize the OpenAI client

# Read API key from env: set OPENAI_API_KEY in your environment
client = OpenAI()  # uses OPENAI_API_KEY

def extract_text_from_pdf(file: BinaryIO) -> str:
    """Extract text directly from a file-like object (no disk write)."""
    reader = PyPDF2.PdfReader(file)
    text_parts = []
    for page in reader.pages:
        t = page.extract_text()
        if t:
            text_parts.append(t)
    return "\n".join(text_parts)

def generate_prompts_from_pdf(
    file: BinaryIO,
    model: str = "gpt-4o",
    temperature: float = 0.3,
    max_prompts: int = 50,
):
    pdf_text = extract_text_from_pdf(file)
    """
    Given a PDF (containing schema/definitions/notes),
    return ONLY natural-language question prompts.
    """
    # pdf_text = extract_text_from_pdf(pdf_path)

    system_msg = (
        "You generate concise, diverse, schema-aware natural-language questions. "
        "Return ONLY questions, each on its own line. No numbering, no SQL, no extra text."
    )

    user_prompt = f"""
You are given content extracted from a PDF that likely describes a Snowflake (or SQL) schema, relationships, and business rules.

Task:
- Produce up to {max_prompts} natural-language QUESTION prompts that an analyst could ask about the data.
- Cover: temporal data (dates/fiscal), dimensions (dept/region), metrics (salary/revenue/headcount), basic stats (count/min/max/avg), YoY/% change, and sanity/validation checks.
- Vary phrasing and scope (table-level, join-level, group-by, filters).
- STRICTLY OUTPUT ONLY the questions, one per line. No numbering, no bullets, no commentary, no SQL, no special characters like *, #, @.

PDF content:
---
{pdf_text}
---
"""

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
    )

    raw = resp.choices[0].message.content.strip()
    # Split by lines and clean
    prompts = [line.strip().lstrip("-•0123456789. ").strip() for line in raw.splitlines() if line.strip()]
    # Deduplicate while preserving order
    seen, unique = set(), []
    for p in prompts:
        if p not in seen:
            seen.add(p)
            unique.append(p)
    return unique

