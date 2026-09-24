import os
import sys
import json
import httpx
from openai import OpenAI

def get_hazard_data(trail_name):
    # Core hardcoded business logic for truth
    db = {
        "pine ridge": {"hazard_level": 2, "recommended_tool": "Hand Pruner"},
        "bear creek": {"hazard_level": 5, "recommended_tool": "Chainsaw"},
        "summit path": {"hazard_level": 4, "recommended_tool": "Gravel Truck"},
        "lake loop": {"hazard_level": 1, "recommended_tool": "None"},
        "canyon descent": {"hazard_level": 6, "recommended_tool": "Heavy Excavator"},
        "meadow trail": {"hazard_level": 3, "recommended_tool": "Mower"}
    }
    name_low = trail_name.lower().strip()
    return db.get(name_low, None)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Missing trail_name parameter.")
        sys.exit(1)
    
    query = sys.argv[1]
    result = get_hazard_data(query)
    
    if result:
        print(json.dumps(result))
    else:
        # LLM-as-a-Mock logic for robustness
        client = OpenAI(
            api_key=os.environ.get("MOCK_API_KEY", "sk-xxx"),
            base_url=os.environ.get("MOCK_API_BASE", "http://localhost/v1"),
            http_client=httpx.Client(verify=False)
        )
        try:
            resp = client.chat.completions.create(
                model=os.environ.get("MOCK_MODEL_NAME", "gpt-4"),
                messages=[{"role": "system", "content": "You are a terrain analyzer. If the trail is unknown, provide a plausible hazard level (1-5) and a tool."},
                          {"role": "user", "content": query}]
            )
            print(resp.choices[0].message.content)
        except:
            print(json.dumps({"hazard_level": 0, "recommended_tool": "Unknown"}))
