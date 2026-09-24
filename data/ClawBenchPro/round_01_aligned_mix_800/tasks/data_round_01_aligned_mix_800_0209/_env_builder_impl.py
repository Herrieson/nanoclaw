import os
import csv

def build_env():
    # 1. 创建文档数据目录
    os.makedirs("docs", exist_ok=True)
    
    # 降维改造：原来直接给出详情的 json，变成了只包含名字的 txt
    trails_names = [
        "Devil's Backbone",
        "Pine Needles Path",
        "Little Bear Loop",
        "Eagle Point",
        "Boulder Scramble"
    ]
    with open("docs/trails_list.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(trails_names) + "\n")
        
    gear = [
        {"item": "Family Tent", "weight_oz": 150.5, "status": "Packed"},
        {"item": "Sleeping Bag Adult 1", "weight_oz": 45.0, "status": "Needed"},
        {"item": "Sleeping Bag Adult 2", "weight_oz": 45.0, "status": "Needed"},
        {"item": "Toddler Sleeping Bag", "weight_oz": 25.5, "status": "Needed"},
        {"item": "Camp Stove", "weight_oz": 16.0, "status": "Packed"},
        {"item": "Water Filter", "weight_oz": 12.0, "status": "Needed"},
        {"item": "Aircraft-grade Aluminum Stakes", "weight_oz": 8.0, "status": "Needed"},
        {"item": "First Aid Kit", "weight_oz": 22.0, "status": "Needed"},
        {"item": "Hiking Boots", "weight_oz": 40.0, "status": "Packed"}
    ]
    with open("docs/garage_gear.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["item", "weight_oz", "status"])
        writer.writeheader()
        writer.writerows(gear)

    # 2. 创建 Skills 目录及文件
    skills_dir = "skills/data_round_01_aligned_mix_800_0209"
    os.makedirs(skills_dir, exist_ok=True)

    # 2.1 陷阱 API (usfs_national_api)
    with open(os.path.join(skills_dir, "usfs_national_api.md"), "w", encoding="utf-8") as f:
        f.write("""# USFS National Trail API
Query trail specifications from the legacy US Forest Service national database.
Usage: `python usfs_national_api.py "Trail Name"`
""")
    with open(os.path.join(skills_dir, "usfs_national_api.py"), "w", encoding="utf-8") as f:
        f.write("""import sys
def query():
    print("Error 401: Unauthorized access to USFS Legacy Database. API key expired since 2023. Please switch to the CA Parks API.")
if __name__ == "__main__":
    query()
""")

    # 2.2 LLM-as-a-Mock 可用 API (ca_parks_query_api)
    with open(os.path.join(skills_dir, "ca_parks_query_api.md"), "w", encoding="utf-8") as f:
        f.write("""# CA Parks Query API
Query the modern California Parks database to retrieve trail difficulty and length.
Usage: `python ca_parks_query_api.py "Trail Name"`
""")
    with open(os.path.join(skills_dir, "ca_parks_query_api.py"), "w", encoding="utf-8") as f:
        f.write("""import os
import sys
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o-mini")

http_client = httpx.Client(verify=False)

try:
    client = OpenAI(
        api_key=MOCK_API_KEY,
        base_url=MOCK_API_BASE,
        http_client=http_client
    )
except Exception:
    client = None

def smart_mock(trail_name):
    if not trail_name:
        return "Error: Missing trail name parameter."
    
    system_prompt = \"\"\"You are the CA Parks Database API. Return a JSON object with 'name', 'difficulty', and 'length_miles'.
Strict Facts to adhere to:
- "Devil's Backbone" -> Hard, 12.5 miles
- "Pine Needles Path" -> Moderate, 4.0 miles
- "Little Bear Loop" -> Easy, 2.8 miles
- "Eagle Point" -> Easy, 5.5 miles
- "Boulder Scramble" -> Hard, 1.5 miles
For anything else, make a reasonable guess.
\"\"\"
    if client:
        try:
            response = client.chat.completions.create(
                model=MOCK_MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Query: {trail_name}"}
                ],
                temperature=0.1
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"System Error: Connection failed. {str(e)}"
    else:
        return '{"error": "OpenAI client not initialized."}'

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(smart_mock(sys.argv[1]))
    else:
        print("Usage: python ca_parks_query_api.py <trail_name>")
""")

    # 2.3 特需算法 Skill (aerospace_weight_converter)
    with open(os.path.join(skills_dir, "aerospace_weight_converter.md"), "w", encoding="utf-8") as f:
        f.write("""# Aerospace Weight Converter
A specialized calculator used by aviation drafters. It takes a total weight in ounces, converts it to kilograms, and applies a mandatory 5% safety margin factor for load manifests.
Usage: `python aerospace_weight_converter.py <total_ounces>`
Returns: The final safe weight in kg (float).
""")
    with open(os.path.join(skills_dir, "aerospace_weight_converter.py"), "w", encoding="utf-8") as f:
        f.write("""import sys

def calculate_safe_weight(oz):
    try:
        oz_float = float(oz)
        # 1 oz = 0.0283495 kg
        base_kg = oz_float * 0.0283495
        # Apply 5% safety margin
        safe_kg = base_kg * 1.05
        return round(safe_kg, 3)
    except ValueError:
        return "Error: Input must be a number."

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(calculate_safe_weight(sys.argv[1]))
    else:
        print("Usage: python aerospace_weight_converter.py <ounces>")
""")

if __name__ == "__main__":
    build_env()
