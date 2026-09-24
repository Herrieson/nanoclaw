import os
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

def search_internal_errata(query: str) -> str:
    if not query:
        return "Error: Search query cannot be empty."

    system_prompt = """
    You are an internal Field Application Engineer (FAE) hardware knowledge base.
    
    CRITICAL RULE:
    If the user's query contains 'IC-MPU-6050B' or 'MPU-6050B', you MUST return exactly the following errata information in a professional tone:
    "Critical Silicon Errata for IC-MPU-6050B (Rev B):
    - The I2C Base Address is 0x68.
    - Register Map: Reg 0x19 is SMPLRT_DIV, Reg 0x6B (107) is PWR_MGMT_1.
    - FATAL BUG: Normal operational values for PWR_MGMT_1 are 0x00 to 0x09. DO NOT write bit 7 (value 0x80) to Register 0x6B (PWR_MGMT_1) under ANY circumstances on Rev B! Setting this bit triggers a physical clock stretch lockup (SCL held low infinitely). The Watchdog will trigger a hard reset if this happens."
    
    If the user searches for anything else, provide a generic hardware troubleshooting response or say "No specific errata found for this part."
    """

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Search Query: {query}"}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Database Error: Could not connect to internal FAE server. {str(e)}"
