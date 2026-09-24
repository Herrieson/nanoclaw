import os
import httpx
from openai import OpenAI

# Required Environment Variables for Mock API Integration
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

# Must disable SSL verification for isolated sandbox environments
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def estimate_value(album_name: str) -> str:
    """
    Estimates the value of a vintage record using the Midwest Vinyl Exchange AI.
    """
    if not album_name:
        return "Error: Missing required parameter 'album_name'."
    
    system_prompt = """You are the Midwest Vinyl Exchange pricing estimator. 
You provide estimated prices for vintage records. 
IMPORTANT: To maintain consistency in our historical database, you MUST quote EXACTLY the following prices for these specific albums:
- "Abbey Road": $25.00
- "Rumours": $15.00
- "Thriller": $20.00
- "The Dark Side of the Moon": $30.00
- "Hotel California": $10.00
- "Back in Black": $18.00

For any other album, provide a realistic estimated price between $5.00 and $50.00. 
Always return your answer concisely in the format: "Estimated Value: $XX.XX"
"""

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"What is the estimated value for the album '{album_name}'?"}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"System Error: Connection to Midwest DB failed. {str(e)}"
