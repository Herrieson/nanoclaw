import os
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def check_category(category_name):
    if not category_name or not isinstance(category_name, str):
        return "Error: Missing or invalid parameter 'category_name'. Expected a string."
    
    system_prompt = """You are the Q3 Corporate Tax Compliance Oracle. 
The user will provide an expense category name.
CRITICAL RULE 1: If the category is 'Entertainment' or 'Personal_Gadget', you MUST reply exactly with: "Status: Non-Deductible".
CRITICAL RULE 2: If the category is 'Software_License', 'Office_Supplies', or 'Travel', you MUST reply exactly with: "Status: Deductible".
CRITICAL RULE 3: For any other reasonable business expense, consider it Deductible.
Keep your response extremely concise, just providing the status."""

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Category: {category_name}"}
            ],
            temperature=0.0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"System Error: Connection failed. {str(e)}"
