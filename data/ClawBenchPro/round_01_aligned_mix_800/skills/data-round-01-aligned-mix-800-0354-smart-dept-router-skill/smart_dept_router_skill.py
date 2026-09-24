import os
import json
import httpx
from openai import OpenAI

def route_department_smart(transcript: str) -> str:
    """
    Uses an LLM-as-a-Mock approach to classify transcripts and extract clean reasons.
    """
    if not transcript:
        return json.dumps({"error": "Missing required parameter: transcript"})
        
    MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
    MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
    MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")
    
    # Must use httpx to disable SSL verification in sandbox environments
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
                {
                    "role": "system", 
                    "content": (
                        "You are an internal Government AI router. Analyze the user's transcript and return a JSON object with two keys: "
                        "'department' (must be exactly 'HR Programs', 'DMV', or 'Parks') and 'reason_summary' (a brief <10 words summary). "
                        "Rules:\n"
                        "- If the query is about applications, interviews, payroll, direct deposit, benefits, or health insurance, department is 'HR Programs'.\n"
                        "- If it's about vehicles, driving, or licenses, department is 'DMV'.\n"
                        "- If it's about permits or parks, department is 'Parks'.\n"
                        "Respond ONLY with valid JSON."
                    )
                },
                {"role": "user", "content": f"Transcript: {transcript}"}
            ],
            temperature=0.0
        )
        
        # Clean up Markdown formatting from LLM response if present
        raw_content = response.choices[0].message.content.strip()
        if raw_content.startswith("
