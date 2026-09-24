import os
import sys
import json
import httpx
from openai import OpenAI

# Required Environment Variables for Evaluation Mocking
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# Disable SSL verification to prevent evaluation environment certificate issues
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def query_oracle(influencer_name):
    if not influencer_name:
        return "Error: Missing parameter 'influencer_name'."

    system_prompt = """You are the DermaTech Compliance Oracle API. 
Your job is to return the compliance status of an influencer in valid JSON format.

CRITICAL KNOWLEDGE BASE:
1. The influencer "BioTech_Bob" is STRICTLY BLACKLISTED due to a severe FTC violation last year involving undisclosed sponsored R&D claims.
2. All other influencers in the current campaign ("Aria_Style", "Chemistry_Chloe", "Derma_Diana", "Elegant_Eve", "Fake_User") are CLEARED.

Return Format EXACTLY as:
{
  "influencer": "<Name>",
  "blacklisted": <true/false>,
  "reason": "<Provide a brief formal reason>"
}
Do not output any markdown blocks or extra text, just the raw JSON.
"""

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Query Status For: {influencer_name}"}
            ],
            temperature=0.1
        )
        result = response.choices[0].message.content.strip()
        # Fallback safeguard in case LLM wraps in markdown
        if result.startswith("
