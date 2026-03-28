from __future__ import annotations
import requests
from .config import AZURE_TRANSLATOR_KEY, AZURE_TRANSLATOR_REGION, AZURE_TRANSLATOR_ENDPOINT

def azure_translate(text: str) -> str:
    if not text or not AZURE_TRANSLATOR_KEY or not AZURE_TRANSLATOR_REGION:
        return text
    endpoint = AZURE_TRANSLATOR_ENDPOINT.rstrip("/") + "/translate"
    params = {"api-version": "3.0", "from": "en", "to": "fa"}
    headers = {
        "Ocp-Apim-Subscription-Key": AZURE_TRANSLATOR_KEY,
        "Ocp-Apim-Subscription-Region": AZURE_TRANSLATOR_REGION,
        "Content-Type": "application/json",
    }
    body = [{"text": text}]
    try:
        r = requests.post(endpoint, params=params, headers=headers, json=body, timeout=20)
        r.raise_for_status()
        data = r.json()
        return data[0]["translations"][0]["text"].strip()
    except Exception:
        return text

def translate_cached(text: str, state: dict) -> str:
    cache = state.setdefault("translator_cache", {})
    if text in cache:
        return cache[text]
    translated = azure_translate(text)
    cache[text] = translated
    return translated
