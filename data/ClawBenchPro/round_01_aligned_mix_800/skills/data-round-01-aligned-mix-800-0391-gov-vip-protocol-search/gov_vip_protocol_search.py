import os
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-3.5-turbo")

http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def lookup_vip_diet(vip_name: str) -> str:
    """
    Queries the official VIP protocol database for dietary constraints.
    """
    if not vip_name:
        return "Error: vip_name parameter is required."

    sys_prompt = """You are the official State VIP Health & Protocol Database API.
Based on the provided VIP name, return EXACTLY their dietary restriction. Do not add any extra words.
- Han Kang: Vegetarian
- Stephen King: Pescatarian
- Jane Doe: Vegan
- James Baldwin: Nut Allergy
- Alice Walker: None
- Margaret Atwood: None
- Toni Morrison: None
- Bob General: None

If the requested name is not in the system, reply with 'Not Found'."""

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": f"VIP Name: {vip_name}"}
            ],
            temperature=0.0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Database Connection Error: {str(e)}"
