import os
import json
import re
from typing import Any, Dict, List
import httpx

DEFAULT_MODEL = os.getenv("DO_INFERENCE_MODEL", "openai-gpt-oss-120b")
API_URL = "https://inference.do-ai.run/v1/chat/completions"
TOKEN = os.getenv("DIGITALOCEAN_INFERENCE_KEY")

def _extract_json(text: str) -> str:
    """Extract JSON from a string that may contain Markdown code fences."""
    m = re.search(r"```(?:json)?\s*\n?([\s\S]*?)\n?\s*```", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    m = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return text.strip()

async def _call_inference(messages: List[Dict[str, str]], max_tokens: int = 512) -> Dict[str, Any]:
    if not TOKEN:
        return {"note": "AI service not configured (missing DIGITALOCEAN_INFERENCE_KEY)."}
    payload = {
        "model": DEFAULT_MODEL,
        "messages": messages,
        "max_completion_tokens": max_tokens,
        "temperature": 0.2,
    }
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(API_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        cleaned = _extract_json(content)
        if cleaned:
            return json.loads(cleaned)
        return {}
    except Exception as exc:
        return {"note": f"AI temporarily unavailable: {str(exc)}"}

async def call_summarization(content: str) -> Dict[str, Any]:
    system = "You are an assistant that creates a concise one‑sentence summary of the given content."
    user = f"Summarize in ONE sentence:\n\n{content}"
    return await _call_inference([
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ])

async def call_tagging(content: str) -> Dict[str, Any]:
    system = (
        "You are an AI that suggests a hierarchical tag list (max 3 levels) for the given content. "
        "Return JSON array of strings like [\"Tech > AI > NLP\", \"Science > Climate\"]."
    )
    user = f"Provide tags for the following content:\n\n{content}"
    return await _call_inference([
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ])

async def generate_embeddings(content: str) -> Dict[str, Any]:
    system = "You generate a vector embedding for the given text. Return JSON with key 'embedding' containing an array of floats."
    user = f"Embed this text:\n\n{content}"
    return await _call_inference([
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ])