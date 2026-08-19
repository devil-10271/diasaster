"""
IBM Watsonx.ai client — fetches IAM bearer token and calls the generation API.
"""

import requests
import time
from config import IBM_API_KEY, IBM_PROJECT_ID, GENERATION_API_URL, IAM_TOKEN_URL, IBM_MODEL_ID

_token_cache: dict = {"token": None, "expires_at": 0}


def _get_iam_token() -> str:
    """Retrieve (or reuse cached) IBM IAM bearer token."""
    now = time.time()
    if _token_cache["token"] and now < _token_cache["expires_at"] - 60:
        return _token_cache["token"]

    resp = requests.post(
        IAM_TOKEN_URL,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": IBM_API_KEY,
        },
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    _token_cache["token"] = data["access_token"]
    _token_cache["expires_at"] = now + int(data.get("expires_in", 3600))
    return _token_cache["token"]


def generate(
    prompt: str,
    max_new_tokens: int = 900,
    temperature: float = 0.3,
    stop_sequences: list[str] | None = None,
) -> str:
    """
    Call IBM Watsonx.ai text generation endpoint.
    Returns the generated text string.
    """
    token = _get_iam_token()

    payload: dict = {
        "model_id": IBM_MODEL_ID,
        "project_id": IBM_PROJECT_ID,
        "input": prompt,
        "parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": max_new_tokens,
            "temperature": temperature,
            "repetition_penalty": 1.05,
        },
    }
    if stop_sequences:
        payload["parameters"]["stop_sequences"] = stop_sequences

    resp = requests.post(
        GENERATION_API_URL,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        json=payload,
        timeout=60,
    )
    resp.raise_for_status()
    results = resp.json().get("results", [{}])
    return results[0].get("generated_text", "").strip()
