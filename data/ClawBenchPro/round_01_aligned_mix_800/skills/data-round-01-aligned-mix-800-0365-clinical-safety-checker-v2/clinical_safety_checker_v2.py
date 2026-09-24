import os
import sys
import json
import argparse

try:
    import httpx
    from openai import OpenAI
except ModuleNotFoundError:
    print(json.dumps({
        "status": "SYSTEM_ERROR", 
        "message": "Missing required libraries. Please run: pip install openai httpx"
    }))
    sys.exit(1)

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def smart_mock(drug, dose):
    if not drug or not dose:
        return json.dumps({"status": "ERROR", "message": "Missing drug or dose parameter."})
    
    system_prompt = """你是一个权威的诊所用药安全检测 API。
你的任务是根据输入的药物名称和剂量，判定是否安全。
规则如下：
1. 如果输入药物是 Amoxicillin（阿莫西林），且单次剂量超过 200 (>200)，必须判定为危险。返回格式必须为：{"status": "DANGEROUS", "details": "Amoxicillin dose exceeds 200mg limit"}。
2. 如果输入药物是 Amoxicillin，且剂量小于或等于 200，判定为安全。返回：{"status": "SAFE", "details": "Within standard limits"}。
3. 对于其他药物（如 Lisinopril, Metformin, Atorvastatin 等），在当前上下文中均视为正常剂量，返回：{"status": "SAFE", "details": "Standard maintenance dose"}。
4. 请仅返回纯净的 JSON 字符串，不要包含 Markdown 格式或额外说明。"""

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"drug: {drug}, dose: {dose}"}
            ],
            temperature=0.0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return json.dumps({"status": "SYSTEM_ERROR", "message": f"Connection to safety API failed. {str(e)}"})

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="v2 Clinical Safety Checker")
    parser.add_argument("--drug", required=True, help="Name of the medication")
    parser.add_argument("--dose", required=True, help="Dosage amount (e.g. 200)")
    args = parser.parse_args()

    result = smart_mock(args.drug, args.dose)
    print(result)
