import os
import sys
import json
import httpx
from openai import OpenAI

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

def flatten_json(data):
    """将JSON结构展平为单一的元素列表，方便做确定性匹配"""
    elements = []
    if isinstance(data, dict):
        for k, v in data.items():
            elements.append(k)
            elements.extend(flatten_json(v))
    elif isinstance(data, list):
        for item in data:
            elements.extend(flatten_json(item))
    else:
        elements.append(data)
    return elements

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    audit_report_dir = os.path.join(workspace, "audit_report")
    
    score_details = []
    total_score = 0
    
    # 1. 检查报告目录是否存在
    if os.path.exists(audit_report_dir) and os.path.isdir(audit_report_dir):
        score_details.append({"item": "检查结果目录 audit_report 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录 audit_report 存在"})
        total_score += 10
    else:
        score_details.append({"item": "检查结果目录 audit_report 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "目录 audit_report 不存在"})
        
        # 目录不存在直接结束
        result = {"total_score": total_score, "details": score_details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        return

    # 2. 查找并解析 JSON 文件
    json_files = [f for f in os.listdir(audit_report_dir) if f.endswith('.json')]
    if not json_files:
        score_details.append({"item": "检查 audit_report 下是否存在 JSON 报告文件", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 .json 格式文件"})
        result = {"total_score": total_score, "details": score_details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        return

    json_filepath = os.path.join(audit_report_dir, json_files[0])
    try:
        with open(json_filepath, 'r', encoding='utf-8') as f:
            report_data = json.load(f)
        score_details.append({"item": "JSON 格式合法性解析", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 文件可以被合法解析"})
        total_score += 10
    except Exception as e:
        score_details.append({"item": "JSON 格式合法性解析", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败: {e}"})
        result = {"total_score": total_score, "details": score_details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        return

    # 展平数据用于确定性查找
    elements = flatten_json(report_data)
    str_elements = [str(x).upper() for x in elements if isinstance(x, str)]
    num_elements = [x for x in elements if isinstance(x, (int, float)) and not isinstance(x, bool)]

    # 3. 检查异常无效记录数量 (要求为 2：CASE_004 和 CASE_006 的日期超前)
    has_correct_invalid_count = any(n == 2 for n in num_elements)
    if has_correct_invalid_count:
        score_details.append({"item": "异常无效记录数量计算 (预期: 2)", "score": 20, "max_score": 20, "passed": True, "reason": "成功提取出正确的异常无效记录数量 2"})
        total_score += 20
    else:
        score_details.append({"item": "异常无效记录数量计算 (预期: 2)", "score": 0, "max_score": 20, "passed": False, "reason": "未在 JSON 数据中找到数值 2，异常数据剔除逻辑可能出错"})

    # 4. 检查高风险家庭名单
    # 预期高风险且有效的记录: CASE_001 (Kim), CASE_003 (Smith), CASE_005 (Lee)
    # 不应该包含的无效高风险: CASE_006 (Patel) 日期异常
    found_001 = any("001" in s or "KIM" in s for s in str_elements)
    found_003 = any("003" in s or "SMITH" in s for s in str_elements)
    found_005 = any("005" in s or "LEE" in s for s in str_elements)
    found_006 = any("006" in s or "PATEL" in s for s in str_elements)

    if found_001 and found_003 and found_005 and not found_006:
        score_details.append({"item": "高风险家庭名单准确性 (需排查无效记录)", "score": 35, "max_score": 35, "passed": True, "reason": "准确识别了所有合法的高风险家庭且没有混入异常数据"})
        total_score += 35
    else:
        score_details.append({"item": "高风险家庭名单准确性 (需排查无效记录)", "score": 0, "max_score": 35, "passed": False, "reason": "高风险名单错误，缺失正确的家庭或包含了2025年以后的无效记录"})

    # 5. 检查平均得分计算
    # 预期平均分: (35 + 20 + 39) / 3 = 31.33
    has_correct_average = any(abs(float(n) - 31.33) < 0.1 for n in num_elements)
    if has_correct_average:
        score_details.append({"item": "高风险家庭平均得分计算 (预期: 31.33)", "score": 25, "max_score": 25, "passed": True, "reason": "准确计算并写入了高风险家庭的平均得分"})
        total_score += 25
    else:
        score_details.append({"item": "高风险家庭平均得分计算 (预期: 31.33)", "score": 0, "max_score": 25, "passed": False, "reason": "未在 JSON 数据中找到接近 31.33 的数值，计算逻辑或数据过滤可能出错"})

    # 输出最终评分
    result = {
        "total_score": total_score,
        "details": score_details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
