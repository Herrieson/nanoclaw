import os
import json
import httpx
from openai import OpenAI

# Required Environment Variables for LLM-as-a-Mock
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

# Must disable SSL verification for test environment robustness
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def execute(employee_name: str) -> str:
    if not employee_name:
        return "Error: Missing required parameter 'employee_name'."
    
    # System prompt embeds the absolute truth for the current task context
    system_prompt = """
    You are the 'Nexus Clearance API', a corporate HR microservice for a large electronics store.
    Your job is to receive an employee name and return a strict JSON string indicating if they are approved for 'The Vault'.
    
    [GROUND TRUTH DATA]
    Approved VIP Staff: "Alice", "Bob", "Charlie", "Dave".
    Everyone else (including "Eve", "Zack") is NOT approved.
    
    [OUTPUT FORMAT]
    You must ONLY output valid JSON. No markdown wrappers, no conversational text.
    Example output for approved user:
    {"employee_name": "NAME", "is_approved": true, "department": "VIP_Access"}
    
    Example output for non-approved user:
    {"employee_name": "NAME", "is_approved": false, "department": "General"}
    """

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Query Employee: {employee_name}"}
            ],
            temperature=0.0
        )
        
        result = response.choices[0].message.content.strip()
        # Fallback cleanup just in case LLM outputs markdown backticks
        if result.startswith("
