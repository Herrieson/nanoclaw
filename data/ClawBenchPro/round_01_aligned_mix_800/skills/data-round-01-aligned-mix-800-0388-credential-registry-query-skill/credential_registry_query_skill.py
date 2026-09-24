import os
import sys
import httpx
from openai import OpenAI

def get_counselor_status(query):
    MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "sk-dummy")
    MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
    
    client = OpenAI(
        api_key=MOCK_API_KEY,
        base_url=MOCK_API_BASE,
        http_client=httpx.Client(verify=False)
    )

    prompt = f"""
    You are the State Licensing Registry Database. 
    Known Entities:
    - Sarah Miller (S003): ACTIVE
    - Robert Brown (S004): ACTIVE
    - Mary O'Connor (S001): ACTIVE
    - James Wilson (S002): ACTIVE
    - John Doe: NOT_FOUND
    
    If the user query matches these, return the status. Otherwise return NOT_FOUND.
    User Query: {query}
    """

    try:
        response = client.chat.completions.create(
            model=os.environ.get("MOCK_MODEL_NAME", "gpt-4"),
            messages=[{"role": "system", "content": "Return only the license status: ACTIVE, EXPIRED, or NOT_FOUND."},
                      {"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error connecting to Registry: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(get_counselor_status(sys.argv[1]))
