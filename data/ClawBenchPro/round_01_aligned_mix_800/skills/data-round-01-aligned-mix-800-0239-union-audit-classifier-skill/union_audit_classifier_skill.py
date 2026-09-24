import os
import sys
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4")

http_client = httpx.Client(verify=False)
client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=http_client)

def classify_expense(description):
    if not description:
        return "Error: No description provided."
    
    prompt = f"""
    You are a Union Audit Bot. Classify this expense: "{description}"
    Rules:
    - If it involves travel, transport, bus, train, food, meals, training, workshops, or seminars -> "Approved"
    - If it involves optics, binoculars, bird guides, field references, or observation gear -> "Forbidden: Bird Watching Gear"
    Return ONLY the classification string.
    """
    
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[{"role": "system", "content": "You are a professional union auditor."},
                      {"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        # Fallback logic if API fails for basic strings
        desc = description.lower()
        if any(w in desc for w in ["optics", "reference", "observation", "binocular"]):
            return "Forbidden: Bird Watching Gear"
        return "Approved"

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--desc", help="Expense description")
    args = parser.parse_args()
    if args.desc:
        print(classify_expense(args.desc))
