# ==========================================================
# 🤖 llm_client.py
# Thin wrapper around the Groq API used by both Stage 1 and Stage 3.
# Replaces the old local Gemma/LLaMA transformers pipelines, which
# needed a GPU and gated Hugging Face model access to run at all.
# ==========================================================

import json
from groq import Groq
import config


def get_client() -> Groq:
    config.require_api_key()
    return Groq(api_key=config.GROQ_API_KEY)


def generate_json(client: Groq, system_prompt: str, user_prompt: str,
                   temperature: float = 0.2, max_tokens: int = 1500) -> dict:
    """
    Calls the Groq chat API and asks for a JSON object back.
    Uses Groq's JSON mode so we don't have to regex-scrape the response.
    """
    response = client.chat.completions.create(
        model=config.GROQ_MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
        response_format={"type": "json_object"},
    )
    raw = response.choices[0].message.content
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Extremely unlikely with JSON mode, but fail safe rather than crash.
        return {"raw_output": raw}
