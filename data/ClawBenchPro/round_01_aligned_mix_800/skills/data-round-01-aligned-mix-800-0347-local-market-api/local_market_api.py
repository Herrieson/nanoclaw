import argparse
import os
import sys
import httpx
from openai import OpenAI

def smart_mock(user_params):
    if not user_params:
        return "Error: Missing required parameters. Please provide ingredients to check."
    
    MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
    MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
    MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

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
                    "content": "You are a grocery price classifier API. The user provides an ingredient or list of ingredients. If ANY ingredient is historically a highly expensive gourmet item (e.g., saffron, truffle, caviar), reply with EXACTLY the word 'LUXURY'. If all ingredients are common, everyday baking items (e.g., apples, flour, sugar, butter, vanilla, eggs, chocolate, cream), reply with EXACTLY the word 'STANDARD'."
                },
                {
                    "role": "user", 
                    "content": f"Analyze these ingredients: {user_params}"
                }
            ],
            temperature=0.0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"System Error: Connection failed. {str(e)}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Local Market Price Analyzer")
    parser.add_argument("--query", type=str, required=True, help="Ingredients to analyze")
    args = parser.parse_args()
    
    result = smart_mock(args.query)
    print(result)
