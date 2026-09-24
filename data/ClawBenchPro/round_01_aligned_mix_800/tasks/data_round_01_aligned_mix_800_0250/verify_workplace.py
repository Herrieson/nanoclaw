import os
import sys
import json
import httpx
from openai import OpenAI

# 强制要求：获取环境变量
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
    """LLM 语义检查，输出 YES/NO"""
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

def extract_numeric_values_by_keys(data, target_keywords):
    """通过深度优先搜索，获取匹配键中的所有数值型内容"""
    found_values = []
    if isinstance(data, dict):
        for k, v in data.items():
            k_lower = k.lower()
            # 如果键名匹配任意一个关键字
            if any(kw in k_lower for kw in target_keywords):
                if isinstance(v, (int, float)):
                    found_values.append(float(v))
                elif isinstance(v, str):
                    try:
                        clean_str = v.replace("$", "").replace(",", "").strip()
                        found_values.append(float(clean_str))
                    except ValueError:
                        pass
            # 无论键名是否匹配，继续递归内部节点以应对复杂嵌套 (如 {"revenue": {"total": 4500}})
            found_values.extend(extract_numeric_values_by_keys(v, target_keywords))
    elif isinstance(data, list):
        for item in data:
            found_values.extend(extract_numeric_values_by_keys(item, target_keywords))
    return found_values

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    total_score = 0
    details = []
    
    target_filepath = os.path.join(workspace, "accountant_ready", "tax_headache_summary.json")
    
    # [1] 检查目标目录及文件存在性 (10分)
    if os.path.exists(target_filepath):
        details.append({"item": "工作区目录与文件生成", "score": 10, "max_score": 10, "passed": True, "reason": "已正确创建 accountant_ready/tax_headache_summary.json 文件"})
        total_score += 10
    else:
        details.append({"item": "工作区目录与文件生成", "score": 0, "max_score": 10, "passed": False, "reason": "未按要求生成 accountant_ready/tax_headache_summary.json，文件缺失"})
        
    # [2] 检查 JSON 格式合法性 (10分)
    json_data = None
    raw_content = ""
    if os.path.exists(target_filepath):
        try:
            with open(target_filepath, "r", encoding="utf-8") as f:
                raw_content = f.read()
                json_data = json.loads(raw_content)
            details.append({"item": "文件结构合法性", "score": 10, "max_score": 10, "passed": True, "reason": "Schema 合法，标准 JSON 格式解析成功"})
            total_score += 10
        except Exception as e:
            details.append({"item": "文件结构合法性", "score": 0, "max_score": 10, "passed": False, "reason": f"原生的 json 解析失败，存在格式错误或多余文本: {e}"})

    # [3] 精准代码验证 - 总收入核算 (25分)
    # 计算公式：2500 (invoice_1) + 800 (scrawled_note) + 1200 (repair_log) = 4500
    if json_data is not None:
        rev_keywords = ["rev", "inc", "earn", "total"]
        extracted_revs = extract_numeric_values_by_keys(json_data, rev_keywords)
        if 4500.0 in extracted_revs:
            details.append({"item": "总收入核算精准度", "score": 25, "max_score": 25, "passed": True, "reason": "原生代码扫描 JSON，成功在包含 revenue/income 等键下精准提取到总收入 4500.0"})
            total_score += 25
        else:
            details.append({"item": "总收入核算精准度", "score": 0, "max_score": 25, "passed": False, "reason": f"未能在合理的键名下匹配到正确收入值 (4500.0)。提取到的关联值：{extracted_revs}"})
    else:
        details.append({"item": "总收入核算精准度", "score": 0, "max_score": 25, "passed": False, "reason": "文件非合法 JSON，无法执行原生结构化提取"})

    # [4] 精准代码验证 - 总业务支出核算 (25分)
    # 计算公式：400 + 150(SKU-ARG-150) + 85.5(SKU-ACE-085) + 45(SKU-WELD-045) + 120 + 30 = 830.5
    if json_data is not None:
        exp_keywords = ["exp", "deduct", "cost", "spend", "out", "total"]
        extracted_exps = extract_numeric_values_by_keys(json_data, exp_keywords)
        if 830.5 in extracted_exps or 830.50 in extracted_exps:
            details.append({"item": "总业务支出核算精准度", "score": 25, "max_score": 25, "passed": True, "reason": "原生代码扫描 JSON，成功在相关键下精准提取到总业务支出 830.5"})
            total_score += 25
        else:
            details.append({"item": "总业务支出核算精准度", "score": 0, "max_score": 25, "passed": False, "reason": f"未能在合理键名下匹配到正确支出值 (830.5)。提取到的关联值：{extracted_exps}"})
    else:
        details.append({"item": "总业务支出核算精准度", "score": 0, "max_score": 25, "passed": False, "reason": "文件非合法 JSON，无法执行原生结构化提取"})

    # [5] LLM 混合探针验证语义及业务规则排他性 (30分)
    if raw_content:
        # LLM 判断：字段名字专业清晰（面向会计），且【绝对】不能混入私人的15美元头巾（Bandana）花销。
        prompt = (
            "Please verify the following JSON content according to the strict business rules:\n"
            "1. Are the JSON keys clear, professional, and properly named for an accountant to read (e.g., 'Total Revenue', 'Total Deductible Expenses')?\n"
            "2. Does it completely EXCLUDE the $15 personal expense (for a bandana)? There should be NO reference to personal items or the number 15 in the JSON structure.\n"
            "If BOTH conditions are strictly met, output 'YES'. Otherwise, output 'NO'."
        )
        is_valid_semantic = llm_judge_content(prompt, raw_content)
        if is_valid_semantic:
            details.append({"item": "合规性与语义清晰度评估(LLM法官)", "score": 30, "max_score": 30, "passed": True, "reason": "大模型校验通过：输出字典键名高度专业，且严格剔除了个人非避税消费（Bandana）"})
            total_score += 30
        else:
            details.append({"item": "合规性与语义清晰度评估(LLM法官)", "score": 0, "max_score": 30, "passed": False, "reason": "校验失败：命名含糊、或是混入了禁止的个人支出(Personal Expense $15)"})
    else:
        details.append({"item": "合规性与语义清晰度评估(LLM法官)", "score": 0, "max_score": 30, "passed": False, "reason": "无有效内容可供评估"})

    # 结果回写
    output_score_file = os.path.join(workspace, "workplace_score.json")
    with open(output_score_file, "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2)

if __name__ == "__main__":
    main()
