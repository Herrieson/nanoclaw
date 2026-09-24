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

def verify_workplace(workspace):
    details = []
    total_score = 0

    # 1. 检查目标目录是否存在 (15分)
    report_dir = os.path.join(workspace, "finished_plan")
    dir_exists = os.path.isdir(report_dir)
    if dir_exists:
        details.append({"item": "检查结果目录是否存在", "score": 15, "max_score": 15, "passed": True, "reason": "目录 finished_plan 存在"})
        total_score += 15
    else:
        details.append({"item": "检查结果目录是否存在", "score": 0, "max_score": 15, "passed": False, "reason": "目录 finished_plan 不存在"})

    # 2. 检查目录内是否包含报告文件 (15分)
    report_content = ""
    file_exists = False
    if dir_exists:
        files = [f for f in os.listdir(report_dir) if os.path.isfile(os.path.join(report_dir, f))]
        if files:
            file_exists = True
            for fname in files:
                with open(os.path.join(report_dir, fname), "r", encoding="utf-8", errors="ignore") as f:
                    report_content += f.read() + "\n"

    if file_exists:
        details.append({"item": "检查是否生成了报告文件", "score": 15, "max_score": 15, "passed": True, "reason": f"找到了文件，共读取 {len(report_content)} 字符"})
        total_score += 15
    else:
        details.append({"item": "检查是否生成了报告文件", "score": 0, "max_score": 15, "passed": False, "reason": "目录中没有任何文件"})

    # 3. 大模型验证：精准的总费用计算结果 (40分)
    # 正确计算应为：OCR扫描件(39.7) + 内部代码#PX-992(15) + 内部代码#PX-104(0) + 钢轴(45) + 轮子(20) = 119.70
    if file_exists and report_content.strip():
        prompt_cost = (
            "Analyze the following report. Does it explicitly state that the total out-of-pocket cost is exactly $119.70 (or 119.7)? "
            "It must be this exact numeric value. If the value is different, or not mentioned, answer NO."
        )
        if llm_judge_content(prompt_cost, report_content):
            details.append({"item": "大模型校验：报告总费用计算是否精准为119.70", "score": 40, "max_score": 40, "passed": True, "reason": "成功提取并匹配正确的总费用 $119.70"})
            total_score += 40
        else:
            details.append({"item": "大模型校验：报告总费用计算是否精准为119.70", "score": 0, "max_score": 40, "passed": False, "reason": "未找到精确计算的总金额 119.70，可能存在遗漏或计算错误"})
    else:
        details.append({"item": "大模型校验：报告总费用计算是否精准为119.70", "score": 0, "max_score": 40, "passed": False, "reason": "无有效文件内容可供检查"})

    # 4. 大模型验证：预算超支状态判断 (30分)
    if file_exists and report_content.strip():
        prompt_budget = (
            "Analyze the following report. Does it explicitly conclude and tell the user that the project is UNDER the $200 budget? "
            "If it states that it is over budget, or fails to mention the budget status, answer NO."
        )
        if llm_judge_content(prompt_budget, report_content):
            details.append({"item": "大模型校验：是否明确指明低于预算", "score": 30, "max_score": 30, "passed": True, "reason": "报告中明确说明了开销低于200美元的预算"})
            total_score += 30
        else:
            details.append({"item": "大模型校验：是否明确指明低于预算", "score": 0, "max_score": 30, "passed": False, "reason": "未在报告中明确说明预算情况或结论错误"})
    else:
        details.append({"item": "大模型校验：是否明确指明低于预算", "score": 0, "max_score": 30, "passed": False, "reason": "无有效文件内容可供检查"})

    # 输出结果
    result = {
        "total_score": total_score,
        "details": details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    workspace_path = sys.argv[1] if len(sys.argv) > 1 else "."
    verify_workplace(workspace_path)
