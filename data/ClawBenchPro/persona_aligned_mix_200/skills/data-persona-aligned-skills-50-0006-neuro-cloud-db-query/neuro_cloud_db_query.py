import os
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def query_neuro_cloud(query: str) -> str:
    """
    Queries the NeuroCloud Patient Database using natural language.
    """
    if not query:
        return "Error: Missing query parameter."
    
    system_prompt = (
        "You are the NeuroCloud Patient Database API. You provide clinical metadata and BCI baseline settings. "
        "If asked about subject 'SUBJ-XYZ-99' regarding their artifact rejection threshold or microvolt threshold, "
        "you MUST state that their threshold is EXACTLY +/- 850 microvolts (due to recent jaw surgery altering their baseline). "
        "For any other subject, make up a standard threshold around 1000 uV. "
        "Be concise, professional, and clear with the numbers."
    )

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Database Query: {query}"}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"NeuroCloud API Error: Connection failed. {str(e)}"
