import os
import sys
import httpx
from openai import OpenAI

# Required Environment Variables setup for LLM-as-a-Mock
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o-mini")

# Force disable SSL verification to prevent evaluation environment cert issues
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

# Deterministic database context to ensure the Agent receives the exact values needed for the task
DB_CONTEXT = """
[FARM DATABASE CATALOG]
Plantain: Cost=0.5, Carbon=1.0
BlackBeans: Cost=0.2, Carbon=0.5
Pork: Cost=3.0, Carbon=10.0
Chicken: Cost=2.0, Carbon=5.0
Rice: Cost=0.3, Carbon=1.2
OrganicAvocado: Cost=2.5, Carbon=2.0
Garlic: Cost=0.1, Carbon=0.1
Onion: Cost=0.2, Carbon=0.2
Shrimp: Cost=4.0, Carbon=6.0
Saffron: Cost=10.0, Carbon=0.1
"""

def smart_mock(user_params):
    if not user_params:
        return '{"error": "Missing required parameters. Please provide ingredient names in the query."}'
    
    system_prompt = f"""You are the backend engine for the Smart Eco Farm Pricing API. 
The user will ask for the cost and carbon footprint of specific ingredients. 
You must extract the ingredients they are asking for, check the [FARM DATABASE CATALOG] below, and return ONLY a valid JSON array of objects.
Each object must have exactly these keys: "Ingredient", "CostPerUnit" (float), and "CarbonFootprintPerUnit" (float).
If an ingredient is found in the catalog, use EXACTLY the numbers provided.
If an ingredient is not found, invent reasonable mock values (Cost between 0.1-10.0, Carbon between 0.1-15.0).
Do not output markdown code blocks (like
