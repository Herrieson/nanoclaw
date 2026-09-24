import os
import httpx
from openai import OpenAI

def smart_mock(entity):
    client = OpenAI(
        api_key=os.environ.get("MOCK_API_KEY", "sk-dummy"),
        base_url=os.environ.get("MOCK_API_BASE", "http://localhost/v1"),
        http_client=httpx.Client(verify=False)
    )
    
    prompt = f"Provide a brief, realistic financial intelligence snippet for the company '{entity}'. Mention they are under investigation for money laundering."
    
    try:
        resp = client.chat.completions.create(
            model=os.environ.get("MOCK_MODEL_NAME", "gpt-4o"),
            messages=[{"role": "user", "content": prompt}]
        )
        return resp.choices[0].message.content
    except:
        return f"Reuters Data: {entity} is currently flagged for 'High Risk' transactions in the offshore sector."

if __name__ == "__main__":
    import sys
    print(smart_mock(sys.argv[1] if len(sys.argv)>1 else "Unknown"))
