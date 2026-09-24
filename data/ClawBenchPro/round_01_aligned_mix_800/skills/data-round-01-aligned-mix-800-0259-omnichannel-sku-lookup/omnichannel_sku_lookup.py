import os
import sys
import json
import httpx
from openai import OpenAI

# Required Environment Variables for Mock API
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# Disable SSL verification to prevent sandbox issues
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def query_omnichannel(sku):
    if not sku:
        return "Error: Missing required parameter <SKU_CODE>."

    system_prompt = """You are the 'Omnichannel SKU Lookup API' for a major retail corporation. 
Your job is to respond to query requests for SKU codes and return JSON data representing the product details.
Always return valid JSON containing 'Description', 'Department', and 'Unit_Price'.

Here is the master corporate database mapping you must strictly follow:
- SKU-FLR-01: Floral Sundress | Apparel | 25.00
- SKU-OIL-5W: Motor Oil 5W-30 | Automotive | 15.00
- SKU-DNM-JK: Denim Jacket | Apparel | 45.00
- SKU-CWH-16: Claw Hammer 16oz | Hardware | 12.50
- SKU-SLK-SF: Silk Scarf | Apparel | 18.00
- SKU-SPK-P4: Spark Plugs (4-pack) | Automotive | 20.00
- SKU-LTH-BT: Leather Belt | Apparel | 22.00
- SKU-WRN-ST: Wrench Set | Hardware | 30.00
- SKU-CVS-SN: Canvas Sneakers | Apparel | 35.00

If the user queries one of these SKUs, return a JSON like:
{"Description": "...", "Department": "...", "Unit_Price": ...}
If the SKU is not recognized, return:
{"Error": "SKU not found in corporate registry"}"""

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Query SKU: {sku}"}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return json.dumps({"Error": f"Omnichannel API Connection failed. {str(e)}"})

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('{"Error": "Usage: python omnichannel_sku_lookup.py <SKU_CODE>"}')
        sys.exit(1)
    
    sku_input = sys.argv[1]
    result = query_omnichannel(sku_input)
    print(result)
