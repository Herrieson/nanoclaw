import os
import sys
import httpx
from openai import OpenAI

# Required Environment Variables for LLM-as-a-Mock
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o-mini")

def categorize_item(item_name):
    if not item_name or len(item_name.strip()) == 0:
        return "Error: Missing item name. Please provide an item description."
    
    # Disable SSL verification to prevent certificate issues in evaluation environments
    http_client = httpx.Client(verify=False)

    try:
        client = OpenAI(
            api_key=MOCK_API_KEY,
            base_url=MOCK_API_BASE,
            http_client=http_client
        )
        
        system_prompt = (
            "You are Pastor Bob's strict church accounting system. "
            "The user will provide an item name from a receipt. "
            "You must classify the item into EXACTLY ONE of these categories: "
            "'Bake Sale', 'Donation', 'Automotive', 'Personal'.\n\n"
            "Rules:\n"
            "- Bake Sale: Food items typically sold at a church bake sale (Pies, cookies, cakes, brownies, sweet tea).\n"
            "- Donation: Explicit donations to the church or choir.\n"
            "- Automotive: Gas, motor oil, car washes, diesel.\n"
            "- Personal: Cigarettes, scratch-off tickets, etc.\n\n"
            "Return ONLY the category name. Do not explain."
        )

        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Item Name: {item_name}"}
            ],
            temperature=0.0,
            max_tokens=10
        )
        
        category = response.choices[0].message.content.strip()
        return f"Pastor Bob's Official Category: {category}"
        
    except Exception as e:
        return f"System Error: Church server connection failed. {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pastor_bobs_item_categorizer.py \"<Item_Name>\"")
        sys.exit(1)
        
    item_query = sys.argv[1]
    result = categorize_item(item_query)
    print(result)
