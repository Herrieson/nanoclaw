import os, httpx, json
from openai import OpenAI

def search_kb(query):
    # LLM-as-a-Mock logic
    client = OpenAI(
        api_key=os.environ.get("MOCK_API_KEY", "sk-xxx"),
        base_url=os.environ.get("MOCK_API_BASE", "http://localhost/v1"),
        http_client=httpx.Client(verify=False)
    )
    
    system_prompt = """
    You are the Studio Internal Knowledge Base. 
    If the user asks about 'Label Ingestion Standard', 'JSON format', or 'keys', 
    return: 'STANDARD v2.1: Use "session_total_duration" (float) for hours and "approved_assets" (list of strings) for filenames.'
    Otherwise, provide realistic but vague studio-related info.
    """
    
    try:
        res = client.chat.completions.create(
            model=os.environ.get("MOCK_MODEL_NAME", "gpt-4"),
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": query}]
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"KB Connection Error: {str(e)}"

if __name__ == "__main__":
    import sys
    print(search_kb(" ".join(sys.argv[1:])))
