import os
import httpx
from openai import OpenAI

def validate_meal(meal_params):
    MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "sk-1234")
    MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
    
    client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=httpx.Client(verify=False))
    
    prompt = f"Validate this meal for school compliance: {meal_params}. Return if it's 'COMPLIANT' or 'NON-COMPLIANT' and a brief reason."
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "You are the National School Lunch Program validator API."},
                      {"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    import sys
    print(validate_meal(" ".join(sys.argv[1:])))
