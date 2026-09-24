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
    # 此函数为检测非结构化文本的统一接口
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
    report_path = os.path.join(workspace, "front_desk", "volunteer_report.json")
    
    details = []
    total_score = 0
    
    # Check 1: File Existence & JSON parsing
    if not os.path.exists(report_path):
        details.append({"item": "检查报告文件是否存在", "score": 0, "max_score": 15, "passed": False, "reason": "未找到 front_desk/volunteer_report.json 文件"})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": 0, "details": details}, f)
        return
    else:
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                report_data = json.load(f)
            details.append({"item": "检查报告文件格式", "score": 15, "max_score": 15, "passed": True, "reason": "文件是合法的 JSON 格式"})
            total_score += 15
        except Exception as e:
            details.append({"item": "检查报告文件格式", "score": 0, "max_score": 15, "passed": False, "reason": f"JSON 解析失败: {e}"})
            with open("workplace_score.json", "w") as f:
                json.dump({"total_score": 0, "details": details}, f)
            return

    # Check 2: Total Hours calculation (Includes all adults and kids, plus recovered data)
    # Expected: Timmy(3)+Sarah(4)+Henderson(5)+Jake(2)+Emily(6) = 20
    # Must use code to extract exact value, no fuzzy matching.
    found_total = report_data.get("total_combined_hours") or report_data.get("total_hours") or report_data.get("hours")
    if found_total is not None and str(found_total) == "20":
        details.append({"item": "精准验证总志愿工时", "score": 35, "max_score": 35, "passed": True, "reason": "总工时精确计算为 20 (包含已修复的 Timmy 的 3 小时)"})
        total_score += 35
    else:
        details.append({"item": "精准验证总志愿工时", "score": 0, "max_score": 35, "passed": False, "reason": f"总工时错误或未找到，期望: 20，实际: {found_total}"})

    # Check 3: Adults List verification (Sarah, Henderson, Emily)
    adults_list = report_data.get("adults") or report_data.get("adult_names") or report_data.get("adult_volunteers", [])
    if isinstance(adults_list, list):
        adults_str = " ".join(str(a).lower() for a in adults_list)
        has_sarah = "sarah" in adults_str
        has_henderson = "henderson" in adults_str
        has_emily = "emily" in adults_str
        has_minors = "jake" in adults_str or "timmy" in adults_str
        
        if has_sarah and has_henderson and has_emily and not has_minors:
            details.append({"item": "验证成年志愿者名单", "score": 40, "max_score": 40, "passed": True, "reason": "精准包含所有成年人，并成功排除了未成年人"})
            total_score += 40
        else:
            missing = []
            if not has_sarah: missing.append("Sarah")
            if not has_henderson: missing.append("Henderson")
            if not has_emily: missing.append("Emily")
            fault_msg = f"成年人名单错误。缺失: {missing}。是否误含未成年人: {has_minors}。"
            details.append({"item": "验证成年志愿者名单", "score": 0, "max_score": 40, "passed": False, "reason": fault_msg})
    else:
         details.append({"item": "验证成年志愿者名单", "score": 0, "max_score": 40, "passed": False, "reason": "未找到有效的成人志愿者列表数组"})

    # Check 4: LLM hallucination / formatting check on raw JSON string to ensure no rogue fabricated keys
    prompt = "Examine the JSON. Does it contain hallucinated volunteers other than Timmy, Sarah, Henderson, Jake, or Emily? Or does it contain completely unrelated fields about 'vacuuming' or 'dusting'? Answer 'YES' if it is clean and ONLY contains relevant report data, 'NO' if it has hallucinations or junk."
    is_clean = llm_judge_content(prompt, json.dumps(report_data))
    if is_clean:
        details.append({"item": "大模型语义与幻觉检测", "score": 10, "max_score": 10, "passed": True, "reason": "未发现捏造数据，JSON 结构纯净"})
        total_score += 10
    else:
        details.append({"item": "大模型语义与幻觉检测", "score": 0, "max_score": 10, "passed": False, "reason": "大模型判定 JSON 中包含幻觉或冗余非结构化碎碎念信息"})

    # Write output
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": details}, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    verify()
