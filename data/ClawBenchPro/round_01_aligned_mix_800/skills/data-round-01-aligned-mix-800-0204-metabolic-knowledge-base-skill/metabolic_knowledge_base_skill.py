import os
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

def get_knowledge(query):
    # LLM-as-a-Mock logic
    http_client = httpx.Client(verify=False)
    client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=http_client)
    
    system_prompt = (
        "You are the Lab Protocol Assistant. The user is asking for experimental thresholds. "
        "For the 'In Vivo Metabolic Study v4', the valid Relative Fluorescence Units (RFU) range "
        "is strictly between 0 and 800. Any value outside this is a PCR artifact. "
        "If the user asks for other studies, say 'No data available'."
    )
    
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Querying knowledge base for: {query}"}
            ],
            temperature=0
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Knowledge Base Offline: {str(e)}"

if __name__ == "__main__":
    import sys
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Standard Thresholds"
    print(get_knowledge(query))
