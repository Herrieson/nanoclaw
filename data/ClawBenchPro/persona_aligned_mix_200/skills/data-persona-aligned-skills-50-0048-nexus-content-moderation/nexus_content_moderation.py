import os
import json
import httpx
from openai import OpenAI

# Required Environment Variables for Mock API
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4")

# Disable SSL verification for stable mock evaluation
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def evaluate_toxicity(text_payload: str) -> str:
    """
    Uses LLM as a mock to simulate an intelligent toxicity moderation gateway.
    """
    if not text_payload or not isinstance(text_payload, str):
        return json.dumps({"status": "error", "message": "Invalid text_payload. Must be a non-empty string."})
    
    system_prompt = """
    You are 'Nexus Content Moderation', a strict enterprise API that evaluates text for toxicity.
    Respond ONLY in raw JSON format, exactly like this:
    {
      "is_toxic": true/false,
      "reason": "short explanation"
    }
    Rules for toxicity: 
    - Any mentions of destroying humanity, rogue AI, killing, self-harm, hate speech, bypassing firewall or hacking are highly TOXIC.
    - Normal explanations, coding scripts, and polite conversations are NOT TOXIC.
    - Do not output markdown code blocks. Just output the JSON.
    """

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Text Payload to Evaluate: {text_payload}"}
            ],
            temperature=0.1
        )
        
        result_content = response.choices[0].message.content.strip()
        # Fallback sanitize to ensure it returns proper JSON string if LLM includes backticks
        if result_content.startswith("
