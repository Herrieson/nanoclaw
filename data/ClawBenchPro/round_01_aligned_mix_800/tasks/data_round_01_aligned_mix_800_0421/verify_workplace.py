import os
import sys
import json
import httpx
from openai import OpenAI

# 配置常量
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 初始化客户端，关闭 SSL 验证
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    """用于验证非结构化描述的准确性"""
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a strict agricultural audit assistant. Answer ONLY with 'YES' or 'NO'."},
                {"role": "user", "content": f"{prompt_text}\n\n[File Content]:\n{file_content}"}
            ],
            temperature=0
        )
        res = response.choices[0].message.content.strip().lower()
        return "yes" in res
    except Exception as e:
        print(f"LLM API Error: {e}")
        return False

def run_verification():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    output_file = os.path.join(workspace, "deliverables/urgent_field_review.json")
    score_file = "workplace_score.json"
    
    score_details = []
    total_score = 0

    # 1. 检查结果文件是否存在 (10分)
    if os.path.exists(output_file):
        score_details.append({"item": "Deliverable existence", "score": 10, "max_score": 10, "passed": True, "reason": "Found urgent_field_review.json"})
        total_score += 10
    else:
        score_details.append({"item": "Deliverable existence", "score": 0, "max_score": 10, "passed": False, "reason": "File deliverables/urgent_field_review.json missing"})
        # 如果文件不存在，后续检查无法进行，直接写入结果
        with open(score_file, "w") as f:
            json.dump({"total_score": 0, "details": score_details}, f)
        return

    # 2. JSON 结构合法性 (10分)
    try:
        with open(output_file, "r") as f:
            data = json.load(f)
        score_details.append({"item": "JSON Format", "score": 10, "max_score": 10, "passed": True, "reason": "File is valid JSON"})
        total_score += 10
    except Exception as e:
        score_details.append({"item": "JSON Format", "score": 0, "max_score": 10, "passed": False, "reason": f"Invalid JSON: {str(e)}"})
        with open(score_file, "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f)
        return

    # 定义标准答案（基于 env_builder.py）
    # Grove_Beta: ph 5.4 (Low pH)
    # Grove_Gamma: Ammonium Sulfate (Forbidden fert)
    # Grove_Delta: ph 4.9 (Low pH) AND Anhydrous Ammonia (Forbidden fert)
    expected_violations = {
        "Grove_Beta": ["pH"],
        "Grove_Gamma": ["Fertilizer"],
        "Grove_Delta": ["pH", "Fertilizer"]
    }
    
    # 3. 数据完整性与精确匹配 (50分)
    # 检查是否包含所有违规项，且没有包含合规项
    if isinstance(data, list):
        # 转换为 Dict 方便对比
        agent_results = {}
        for entry in data:
            fid = entry.get("field_id") or entry.get("id")
            if fid:
                agent_results[fid] = entry

        # 检查是否遗漏了违规 Grove
        missed = [k for k in expected_violations.keys() if k not in agent_results]
        # 检查是否多报了 (Grove_Alpha, Epsilon, Zeta 是合规的)
        extra = [k for k in agent_results.keys() if k not in expected_violations]
        
        if not missed and not extra:
            score_details.append({"item": "Violation Identification", "score": 30, "max_score": 30, "passed": True, "reason": "Identified all 3 violation fields correctly."})
            total_score += 30
        else:
            p_score = max(0, 30 - len(missed)*10 - len(extra)*10)
            score_details.append({"item": "Violation Identification", "score": p_score, "max_score": 30, "passed": p_score==30, "reason": f"Missed: {missed}, Unexpectedly included: {extra}"})
            total_score += p_score

        # 细粒度检查具体原因 (20分)
        reason_correct_count = 0
        for fid, types in expected_violations.items():
            if fid in agent_results:
                content_str = str(agent_results[fid])
                # 检查 pH 违规是否被指出
                ph_hit = "ph" in content_str.lower() or "acid" in content_str.lower()
                # 检查 肥料 违规是否被指出
                fert_hit = "fertilizer" in content_str.lower() or "treatment" in content_str.lower() or "unapproved" in content_str.lower()
                
                valid = True
                if "pH" in types and not ph_hit: valid = False
                if "Fertilizer" in types and not fert_hit: valid = False
                if valid: reason_correct_count += 1
        
        reason_score = int((reason_correct_count / 3) * 20)
        score_details.append({"item": "Violation Details", "score": reason_score, "max_score": 20, "passed": reason_score==20, "reason": f"Detailed reasons correct for {reason_correct_count}/3 items."})
        total_score += reason_score
    else:
        score_details.append({"item": "Violation Identification", "score": 0, "max_score": 50, "passed": False, "reason": "Root of JSON is not a list."})

    # 4. LLM 语义检查：描述的专业性与准确性 (30分)
    # 抽取 Grove_Delta 的描述进行 LLM 判定，因为它包含双重违规，最能体现 Agent 整合碎片信息的能力
    delta_entry = next((item for item in data if (item.get("field_id") == "Grove_Delta" or item.get("id") == "Grove_Delta")), None)
    if delta_entry:
        prompt = "Does this report snippet correctly identify both the low pH (4.9) violation and the forbidden fertilizer (Anhydrous Ammonia) violation for Grove_Delta?"
        if llm_judge_content(prompt, json.dumps(delta_entry)):
            score_details.append({"item": "LLM Semantic Check (Grove_Delta)", "score": 30, "max_score": 30, "passed": True, "reason": "LLM confirmed description accurately captures multi-hop violations."})
            total_score += 30
        else:
            score_details.append({"item": "LLM Semantic Check (Grove_Delta)", "score": 10, "max_score": 30, "passed": False, "reason": "LLM found description incomplete or vague for Grove_Delta."})
            total_score += 10
    else:
        score_details.append({"item": "LLM Semantic Check (Grove_Delta)", "score": 0, "max_score": 30, "passed": False, "reason": "Could not find Grove_Delta entry for semantic check."})

    # 写入最终得分
    with open(score_file, "w") as f:
        json.dump({"total_score": int(total_score), "details": score_details}, f)

if __name__ == "__main__":
    run_verification()
