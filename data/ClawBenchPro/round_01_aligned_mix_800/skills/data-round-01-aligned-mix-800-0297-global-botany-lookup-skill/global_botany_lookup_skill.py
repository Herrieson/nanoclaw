import sys
import os
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "sk-native-botany-772")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4-vision-preview")

def lookup_species(species):
    # Mandatory LLM-as-a-Mock logic
    client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=httpx.Client(verify=False))
    
    system_prompt = """
    You are a professional botanical database. Given a plant name, return ONLY 'Native' or 'Invasive' based on the following rules:
    - Native: Sego Lily, Sagebrush, Bitterbrush, Rabbitbrush.
    - Invasive: Russian Thistle, Cheatgrass, Dandelion, Knapweed.
    If unknown, return 'Invasive' for safety.
    """
    
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": species}],
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except:
        return "Error: Database connection failed."

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(lookup_species(sys.argv[1]))
