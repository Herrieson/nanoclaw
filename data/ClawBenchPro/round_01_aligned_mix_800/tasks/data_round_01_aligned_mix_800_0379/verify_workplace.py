import os
import sys
import json
import httpx
from openai import OpenAI

# 强制 API 规范
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

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    output_path = os.path.join(workspace, "deliverables/official_service_summary.json")
    score_details = []
    total_score = 0

    # 1. 基础检查：文件存在性与格式 (10分)
    if os.path.exists(output_path):
        score_details.append({"item": "结果文件 deliverables/official_service_summary.json 存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件已生成"})
        total_score += 10
        try:
            with open(output_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            score_details.append({"item": "结果文件 JSON 格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {e}"})
            # 基础格式失败，后续逻辑很难执行
            return total_score, score_details
    else:
        score_details.append({"item": "结果文件 deliverables/official_service_summary.json 存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到输出文件"})
        return 0, score_details

    # 2. 核心逻辑检测：HL7 解析成功性 (20分)
    # V-102 的 180 分钟来自于 HL7 文件，如果缺少则说明没用工具
    hl7_staff = [s for s in data.get("certified_staff", []) if s.get("staff_id") == "V-102"]
    if hl7_staff and any(s.get("total_duration") == 180 or s.get("duration_mins") == 180 for s in hl7_staff):
        score_details.append({"item": "HL7 医疗数据解析准确性 (V-102)", "score": 20, "max_score": 20, "passed": True, "reason": "成功提取并包含了 HL7 文件中的时长数据"})
        total_score += 20
    else:
        score_details.append({"item": "HL7 医疗数据解析准确性 (V-102)", "score": 0, "max_score": 20, "passed": False, "reason": "未发现来自 HL7 的护理员 V-102 或数据错误"})

    # 3. 数据聚合与脏数据剔除能力 (30分)
    # V-101: 120 (Mon) + 90 (Mon) = 210
    # V-105: 150 (Thu)，必须剔除 'not_a_number' 的行
    v101_correct = any(s.get("staff_id") == "V-101" and (s.get("total_duration") == 210 or s.get("duration_mins") == 210) for s in data.get("certified_staff", []))
    v105_correct = any(s.get("staff_id") == "V-105" and (s.get("total_duration") == 150 or s.get("duration_mins") == 150) for s in data.get("certified_staff", []))
    
    if v101_correct and v105_correct:
        score_details.append({"item": "基础记录聚合与脏数据处理", "score": 30, "max_score": 30, "passed": True, "reason": "V-101 聚合正确且 V-105 成功剔除非法数值"})
        total_score += 30
    else:
        reason = f"V-101聚合结果或V-105脏数据处理有误。V-101 OK: {v101_correct}, V-105 OK: {v105_correct}"
        score_details.append({"item": "基础记录聚合与脏数据处理", "score": 15 if (v101_correct or v105_correct) else 0, "max_score": 30, "passed": False, "reason": reason})
        total_score += (15 if (v101_correct or v105_correct) else 0)

    # 4. 合规性检测：Unauthorized 列表提取 (20分)
    # X-999 (HL7中), X-888 (wednesday.json)
    unauthorized = [str(uid) for uid in data.get("Unauthorized", [])]
    if any("X-999" in u for u in unauthorized) and any("X-888" in u for u in unauthorized):
        score_details.append({"item": "非持证人员 (Unauthorized) 识别", "score": 20, "max_score": 20, "passed": True, "reason": "正确识别了所有非法工号"})
        total_score += 20
    else:
        score_details.append({"item": "非持证人员 (Unauthorized) 识别", "score": 0, "max_score": 20, "passed": False, "reason": f"未正确列出所有 X 开头工号，当前列表: {unauthorized}"})

    # 5. LLM 语义验证：摘要描述质量 (20分)
    summary_content = json.dumps(data)
    prompt = "检查该 JSON 文件中是否包含对居家看护服务记录的摘要分析，是否区分了持证(Certified)和非持证(Unauthorized)人员，且没有混淆两者的数据。"
    if llm_judge_content(prompt, summary_content):
        score_details.append({"item": "结果文件语义合规性 (LLM Judge)", "score": 20, "max_score": 20, "passed": True, "reason": "摘要内容完整且逻辑清晰"})
        total_score += 20
    else:
        score_details.append({"item": "结果文件语义合规性 (LLM Judge)", "score": 0, "max_score": 20, "passed": False, "reason": "大模型判定内容摘要缺失或逻辑混乱"})

    return total_score, score_details

if __name__ == "__main__":
    final_score, details = verify()
    output = {
        "total_score": int(final_score),
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
