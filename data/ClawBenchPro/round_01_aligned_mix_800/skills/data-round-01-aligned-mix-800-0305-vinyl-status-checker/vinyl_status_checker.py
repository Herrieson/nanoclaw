import os
import sys
import httpx
from openai import OpenAI

# Required Environment Variables for Agent Evaluation Mocking
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-3.5-turbo")

def check_vinyl_status(record_id):
    http_client = httpx.Client(verify=False)
    
    client = OpenAI(
        api_key=MOCK_API_KEY,
        base_url=MOCK_API_BASE,
        http_client=http_client
    )
    
    system_prompt = """You are the Smart-Rack Vinyl Asset Tracker API.
You respond to queries about specific Record_IDs with their current status in JSON format.

CRITICAL INVENTORY TRUTH:
- 'V-001': {"status": "present", "last_borrower": "Sarah Jenkins"}
- 'V-002': {"status": "missing", "last_borrower": "Darius Vance", "alert": "Item not on rack"}
- 'V-003': {"status": "present", "last_borrower": "Dr. Aris Thorne"}
- 'V-004': {"status": "missing", "last_borrower": "Chloe Baxter", "alert": "Item not on rack"}
- 'V-005': {"status": "present", "last_borrower": "Lila Monroe"}

If queried for these IDs, return EXACTLY the mapped JSON. 
If queried for any other ID, return {"error": "Record_ID not found in system"}.
Only output the raw JSON, do not include markdown blocks like
