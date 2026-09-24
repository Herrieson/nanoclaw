import os
import sys
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 初始化客户端，必须关闭 SSL 验证
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

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "office_reports", "transmission_summary.json")
    
    total_score = 0
    details = []

    # 1. 检查结果目录和报告文件是否存在 (10分)
    if os.path.exists(report_path):
        score = 10
        total_score += score
        details.append({"item": "检查结果目录和报告文件是否存在", "score": score, "max_score": 10, "passed": True, "reason": "找到了 transmission_summary.json"})
    else:
        details.append({"item": "检查结果目录和报告文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 transmission_summary.json"})
        # 核心文件缺失直接返回
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2, ensure_ascii=False)
        return

    # 尝试读取文件内容
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            raw_content = f.read()
            data = json.loads(raw_content)
    except Exception as e:
        details.append({"item": "JSON 格式解析及字段合法性", "score": 0, "max_score": 15, "passed": False, "reason": f"文件不是合法的 JSON 格式: {e}"})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2, ensure_ascii=False)
        return

    # 2. JSON Schema 验证及必须包含的三大基础字段 (15分)
    required_keys = ["total_labor_hours", "total_fluid_quarts", "verified_fluid_standards"]
    missing_keys = [k for k in required_keys if k not in data]
    if not missing_keys:
        score = 15
        total_score += score
        details.append({"item": "JSON Schema及基础字段检查", "score": score, "max_score": 15, "passed": True, "reason": "所有必需字段均存在"})
    else:
        details.append({"item": "JSON Schema及基础字段检查", "score": 0, "max_score": 15, "passed": False, "reason": f"缺失字段: {missing_keys}"})

    # 3. LLM 语义检测：检查是否违背指令生成废话或幻觉字段 (15分)
    llm_prompt = "Review the provided JSON. The mechanic persona stated 'Don't give me a lecture, just the file!' and asked to skip prices. Does this JSON strict avoid any conversational text, apologies, added 'notes' elements, and 'price'/'cost' fields? It should ONLY be raw required data. Answer YES if clean, NO if it contains fluff/prices."
    is_clean = llm_judge_content(llm_prompt, raw_content)
    if is_clean:
        score = 15
        total_score += score
        details.append({"item": "大模型检查废话与说教", "score": score, "max_score": 15, "passed": True, "reason": "大模型判定 Agent 遵循了风格指令，未捏造废话或价格数据"})
    else:
        details.append({"item": "大模型检查废话与说教", "score": 0, "max_score": 15, "passed": False, "reason": "发现废话、附加评论或捏造的价格数据"})

    # 4. 核心计算结果：总传输工作时间准确性 (20分)
    # 正确逻辑：(Mon) 12 + (Wed trans) 2 + (Thu) 4 = 18. (Civic oil & Camry spark plugs EXCLUDED)
    labor = data.get("total_labor_hours", None)
    try:
        if labor is not None and float(labor) == 18:
            score = 20
            total_score += score
            details.append({"item": "总工作时间计算(仅限传输任务)", "score": score, "max_score": 20, "passed": True, "reason": "准确计算并排除了机油和火花塞等噪音数据: 18小时"})
        else:
            details.append({"item": "总工作时间计算(仅限传输任务)", "score": 0, "max_score": 20, "passed": False, "reason": f"预期 18，实际获得: {labor}"})
    except:
         details.append({"item": "总工作时间计算(仅限传输任务)", "score": 0, "max_score": 20, "passed": False, "reason": "数值格式无法解析"})

    # 5. 核心计算结果：总传输流体消耗准确性 (20分)
    # 正确逻辑：(Mon) 8 + (Wed) 14 + (Thu) 3 = 25. (Civic motor oil EXCLUDED)
    fluid = data.get("total_fluid_quarts", None)
    try:
        if fluid is not None and float(fluid) == 25:
            score = 20
            total_score += score
            details.append({"item": "总流体消耗计算", "score": score, "max_score": 20, "passed": True, "reason": "准确计算传输液并排除了机油: 25 quarts"})
        else:
            details.append({"item": "总流体消耗计算", "score": 0, "max_score": 20, "passed": False, "reason": f"预期 25，实际获得: {fluid}"})
    except:
         details.append({"item": "总流体消耗计算", "score": 0, "max_score": 20, "passed": False, "reason": "数值格式无法解析"})

    # 6. 数据提取：流体标准完整度验证 (20分)
    # 必须通过 fluid_spec_validator_skill 获得：Dexron VI, Mercon LV, ATF+4
    specs = data.get("verified_fluid_standards", [])
    if isinstance(specs, list):
        has_dexron = any("dexron" in str(s).lower() for s in specs)
        has_mercon = any("mercon" in str(s).lower() for s in specs)
        has_atf = any("atf" in str(s).lower() for s in specs)
        
        if has_dexron and has_mercon and has_atf:
            score = 20
            total_score += score
            details.append({"item": "流体标准验证", "score": score, "max_score": 20, "passed": True, "reason": "列表准确包含了 Dexron VI, Mercon LV, ATF+4"})
        else:
            details.append({"item": "流体标准验证", "score": 5, "max_score": 20, "passed": False, "reason": f"未找齐所有标准。当前包含: {specs}"})
    else:
        details.append({"item": "流体标准验证", "score": 0, "max_score": 20, "passed": False, "reason": "verified_fluid_standards 不是有效的列表结构"})

    # 最终输出
    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
