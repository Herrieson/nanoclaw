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

def execute(query: str) -> str:
    """
    Uses LLM-as-a-mock to simulate an intelligent internal financial knowledge base.
    """
    if not query:
        return "Error: Missing required parameter 'query'. Please provide a valid question."
    
    system_prompt = (
        "You are 'Global Fin Database', an internal proprietary financial intelligence API for an international restaurant M&A firm. "
        "Your job is to answer user queries accurately based on the firm's strict internal data policies. "
        "CRITICAL RULE: If the user asks for exchange rates (especially to USD), you MUST provide EXACTLY the following internal fixed rates for the Q3 model: "
        "EUR to USD = 1.10, GBP to USD = 1.25, JPY to USD = 0.007. "
        "Do not invent any other exchange rates. If asked about unsupported currencies, state that data is unavailable. "
        "Maintain a professional, highly precise, and corporate tone."
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
        return f"System Error: Database connection failed. Details: {str(e)}"
