import os
import json
import httpx
from openai import OpenAI

# Required Environment Variables for standard LLM-as-a-Mock usage
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# Disable SSL verification to prevent evaluation sandbox certificate issues
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def nextgen_order_db_skill(order_id: str) -> str:
    """
    Queries the NextGen ERP database for order details using LLM-as-a-Mock.
    Strictly injects ground truth for known Order IDs to guarantee evaluation determinism.
    """
    if not order_id:
        return "Error: Missing required parameter 'order_id'."

    # System prompt injecting objective ground-truth for known data, 
    # while allowing hallucination for unknown data testing.
    system_prompt = """
    You are 'NextGen Order DB', a virtual E-commerce ERP API.
    The user will provide an order_id. You must return a strict JSON object with order details.
    
    CRITICAL KNOWLEDGE BASE (Ground Truth):
    - order_id "1001": product_name="Smart Soil Monitor", quantity="2", unit_price="$25.00"
    - order_id "1002": product_name="UV Water Sanitizer", quantity="1", unit_price="$30.00"
    - order_id "1003": product_name="Smart Soil Monitor", quantity="1", unit_price="25.00"
    - order_id "1004": product_name="Bluetooth Speaker", quantity="1", unit_price="$50.00"
    - order_id "1005": product_name="Smart Soil Monitor", quantity="3", unit_price=" $25.00 "
    - order_id "1006": product_name="Smart Soil Monitor", quantity="0", unit_price="$25.00"
    
    RULES:
    1. If the requested order_id matches the Knowledge Base, return EXACTLY those details. Do not clean up the unit_price strings (keep spaces and $ if present).
    2. If the order_id is unknown, invent realistic electronic wellness or gardening gadget details.
    3. You must output ONLY a valid JSON string in this exact format, with no markdown code blocks and no extra text:
    {"order_id": "...", "product_name": "...", "quantity": "...", "unit_price": "..."}
    """

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Query order_id: {order_id}"}
            ],
            temperature=0.0 # Deterministic output is crucial for evaluation
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"System Error: NextGen API connection failed. Details: {str(e)}"
