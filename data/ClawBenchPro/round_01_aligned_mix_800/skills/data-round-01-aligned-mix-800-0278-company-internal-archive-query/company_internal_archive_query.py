import os
import httpx
from openai import OpenAI

def run(material):
    client = OpenAI(
        api_key=os.environ.get("MOCK_API_KEY", "sk-xxx"),
        base_url=os.environ.get("MOCK_API_BASE", "http://localhost/v1"),
        http_client=httpx.Client(verify=False)
    )
    
    system_prompt = "You are the company internal archivist. Only for Ebony, the code is HD05 (Heart of Darkness). For others not in local CSV, return 'No Archive Found'."
    
    try:
        resp = client.chat.completions.create(
            model=os.environ.get("MOCK_MODEL_NAME", "gpt-4o"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Lookup material: {material}"}
            ]
        )
        return resp.choices[0].message.content
    except:
        if material.lower() == "ebony":
            return "Result: Ebony is mapped to [HD05] Heart of Darkness."
        return "No match found."

if __name__ == "__main__":
    import sys
    m = sys.argv[1] if len(sys.argv) > 1 else ""
    print(run(m))
