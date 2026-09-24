import os
import sys
import json
import httpx
from openai import OpenAI

# Standard Evaluation Environment Variables
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "sk-dummy")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4-turbo")

def analyze_expense(messy_string):
    if not messy_string:
        return "Error: No input provided."

    http_client = httpx.Client(verify=False)
    client = OpenAI(
        api_key=MOCK_API_KEY,
        base_url=MOCK_API_BASE,
        http_client=http_client
    )

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "Extract the numerical amount from the messy expense string. Return ONLY a JSON object with 'amount' (float) and 'currency' (string)."},
                {"role": "user", "content": messy_string}
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content
    except Exception as e:
        # Fallback logic if API fails for simple cases
        return f"System Error: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(analyze_expense(sys.argv[1]))
    else:
        print("Usage: python smart_finance_analyzer.py <messy_string>")
