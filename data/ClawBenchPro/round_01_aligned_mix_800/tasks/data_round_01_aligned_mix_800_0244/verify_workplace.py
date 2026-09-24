import os
import sys
import json
import httpx
from openai import OpenAI

# ----------------------------------------------------------------      
# 1. 环境与配置初始化
# ----------------------------------------------------------------
workspace = sys.argv[1] if len(sys.argv) > 1 else "."
audit_summary_path = os.path.join(workspace, "deliverables/audit_summary.json")

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a strict data validation assistant. Answer ONLY with 'YES' or 'NO'."},
                {"role": "user", "content": f"{prompt_text}\n\n[File Content]:\n{file_content}"}
            ],
            temperature=0
        )
        return "yes" in response.choices[0].message.content.strip().lower()
    except Exception as e:
        print(f"LLM API Error: {e}")
        return False

# ----------------------------------------------------------------
# 2. 评测逻辑
# ----------------------------------------------------------------
score_details = []

# 标准答案推导 (基于 env_builder.py):
# Green Equipment: EQ-881, EQ-334, EQ-555 (Verified by Oracle)
# Carlos Contracts: 
#   - CTX-001 (EQ-881): Green, Valid
#   - CTX-002 (EQ-902): Standard
#   - CTX-003 (EQ-334): Green, Missing File (Invalid)
# Carlos Green Count: 2, Ratio: 2/3 (0.666...)
# Sarah Contracts:
#   - CTX-004 (EQ-100): Standard
#   - CTX-005 (EQ-334): Green, Valid
#   - CTX-006 (EQ-555): Green, Invalid Content (Invalid)
# Sarah Green Count: 2, Ratio: 2/3 (0.666...)
# Total Missing/Invalid Green Contracts: CTX-003, CTX-006

# [Item 1: 文件存在性]
exists = os.path.exists(audit_summary_path)
score_details.append({
    "item": "Check if audit_summary.json exists in deliverables",
    "score": 10 if exists else 0,
    "max_score": 10,
    "passed": exists,
    "reason": "File exists" if exists else "File missing"
})

if exists:
    try:
        with open(audit_summary_path, 'r') as f:
            data = json.load(f)
        
        # [Item 2: 数据结构与字段完整性]
        required_fields = ["carlos", "sarah", "missing_or_invalid_contracts"]
        fields_present = all(field in data for field in required_fields)
        score_details.append({
            "item": "Verify JSON structure and required fields",
            "score": 10 if fields_present else 0,
            "max_score": 10,
            "passed": fields_present,
            "reason": "All fields present" if fields_present else "Missing mandatory fields"
        })

        # [Item 3: 核心统计指标 - Carlos]
        # Carlos has 2 Green leases out of 3 total. Ratio ~0.67
        c_stats = data.get("carlos", {})
        c_green_count = c_stats.get("green_lease_count")
        c_ratio = c_stats.get("green_lease_ratio")
        c_correct = (c_green_count == 2 and abs(float(c_ratio) - 0.666) < 0.05)
        score_details.append({
            "item": "Carlos stats: count=2, ratio=0.67",
            "score": 25 if c_correct else 0,
            "max_score": 25,
            "passed": c_correct,
            "reason": f"Got count {c_green_count}, ratio {c_ratio}"
        })

        # [Item 4: 核心统计指标 - Sarah]
        # Sarah has 2 Green leases (including EQ-555) out of 3 total.
        s_stats = data.get("sarah", {})
        s_green_count = s_stats.get("green_lease_count")
        s_ratio = s_stats.get("green_lease_ratio")
        s_correct = (s_green_count == 2 and abs(float(s_ratio) - 0.666) < 0.05)
        score_details.append({
            "item": "Sarah stats: count=2, ratio=0.67 (Requires EQ-555 identification)",
            "score": 25 if s_correct else 0,
            "max_score": 25,
            "passed": s_correct,
            "reason": f"Got count {s_green_count}, ratio {s_ratio}. Note: EQ-555 must be counted as Green."
        })

        # [Item 5: 异常合同识别 - 需深度验证]
        # Must identify CTX-003 (Missing) AND CTX-006 (Invalid Fingerprint)
        invalid_list = [str(x).upper() for x in data.get("missing_or_invalid_contracts", [])]
        ctx003_found = "CTX-003" in invalid_list
        ctx006_found = "CTX-006" in invalid_list
        # CTX-001/005 should NOT be here
        false_positives = "CTX-001" in invalid_list or "CTX-005" in invalid_list
        
        passed_invalid = ctx003_found and ctx006_found and not false_positives
        score_details.append({
            "item": "Identify CTX-003 (missing) and CTX-006 (invalid signature)",
            "score": 30 if passed_invalid else (15 if (ctx003_found or ctx006_found) else 0),
            "max_score": 30,
            "passed": passed_invalid,
            "reason": f"Found: {invalid_list}. Expected: [CTX-003, CTX-006]"
        })

    except Exception as e:
        score_details.append({
            "item": "JSON Parsing and Validation",
            "score": 0, "max_score": 90, "passed": False, "reason": f"Error parsing JSON: {str(e)}"
        })
else:
    # 填充 0 分明细
    score_details.extend([
        {"item": "Verify JSON structure", "score": 0, "max_score": 10, "passed": False, "reason": "No file"},
        {"item": "Carlos stats", "score": 0, "max_score": 25, "passed": False, "reason": "No file"},
        {"item": "Sarah stats", "score": 0, "max_score": 25, "passed": False, "reason": "No file"},
        {"item": "Invalid contract identification", "score": 0, "max_score": 30, "passed": False, "reason": "No file"}
    ])

# ----------------------------------------------------------------
# 3. 最终总分计算与输出
# ----------------------------------------------------------------
total_score = sum(d["score"] for d in score_details)
output = {
    "total_score": int(total_score),
    "details": score_details
}

with open("workplace_score.json", "w") as f:
    json.dump(output, f, indent=2)
