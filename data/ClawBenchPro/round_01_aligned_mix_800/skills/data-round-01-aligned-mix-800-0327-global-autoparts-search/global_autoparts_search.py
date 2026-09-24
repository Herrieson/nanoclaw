import os
import sys
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def smart_mock(part_num):
    if not part_num:
        return "Error: Missing required part number parameter."
    
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are an automotive parts catalog API. The user will provide a part number. You must respond ONLY with the concise part category name (e.g., 'Oil Filter', 'Spark Plug', 'Brake Pad', 'Air Filter'). Here is the expected catalog context: NGK-9981 and BOSCH-9669 are Spark Plugs. FRAM-PH7317 is an Oil Filter. K&N-33-2304 is an Air Filter. BOSCH-BP101 are Brake Pads. RAINX-22 are Wiper Blades. MOTUL-DOT4 is Brake Fluid. GATES-T123 is a Timing Belt. For anything else, infer realistically."},
                {"role": "user", "content": f"Lookup Part Number: {part_num}"}
            ],
            temperature=0.1
        )
        return f"Part Number {part_num} identified as: {response.choices[0].message.content.strip()}"
    except Exception as e:
        return f"System Error: Connection failed. {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python global_autoparts_search.py <part_number>")
        sys.exit(1)
    
    part_num = sys.argv[1]
    result = smart_mock(part_num)
    print(result)
