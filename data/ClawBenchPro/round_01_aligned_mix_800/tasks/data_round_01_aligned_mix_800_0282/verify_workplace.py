import os
import sys
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o-mini") # Use standard env or fallback

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
    report_path = os.path.join(workspace, "deliverables", "report.json")
    
    details = []
    total_score = 0
    
    # 1. 检查文件是否存在且能被解析为 JSON
    if os.path.exists(report_path):
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                report_content = f.read()
                data = json.loads(report_content)
            details.append({"item": "文件与结构验证", "score": 20, "max_score": 20, "passed": True, "reason": "report.json 存在且格式合法"})
            total_score += 20
        except json.JSONDecodeError:
            details.append({"item": "文件与结构验证", "score": 0, "max_score": 20, "passed": False, "reason": "report.json 不是合法的 JSON 格式"})
            data = None
    else:
        details.append({"item": "文件与结构验证", "score": 0, "max_score": 20, "passed": False, "reason": "deliverables/report.json 不存在"})
        data = None

    if data is not None and isinstance(data, dict):
        # 2. 检查必需字段
        has_unauth = "unauthorized_access" in data
        has_hours = "total_approved_hours" in data
        if has_unauth and has_hours:
            details.append({"item": "必需字段检查", "score": 10, "max_score": 10, "passed": True, "reason": "包含所有必需字段"})
            total_score += 10
        else:
            details.append({"item": "必需字段检查", "score": 0, "max_score": 10, "passed": False, "reason": "缺失 unauthorized_access 或 total_approved_hours 字段"})
            
        # 3. 精确数值提取与计算检查 (去重逻辑)
        if has_hours:
            try:
                hours = float(data["total_approved_hours"])
                if hours == 44 or hours == 44.0:
                    details.append({"item": "排班总时长计算 (含去重)", "score": 30, "max_score": 30, "passed": True, "reason": "精确计算出 44 小时，成功移除了 Sarah 的冗余打卡"})
                    total_score += 30
                elif hours == 56 or hours == 56.0:
                    details.append({"item": "排班总时长计算 (含去重)", "score": 0, "max_score": 30, "passed": False, "reason": "计算出 56 小时，未能识别并剔除 Sarah 的重复输入记录"})
                else:
                    details.append({"item": "排班总时长计算 (含去重)", "score": 0, "max_score": 30, "passed": False, "reason": f"计算结果错误，期望 44，实际得到 {hours}"})
            except (ValueError, TypeError):
                details.append({"item": "排班总时长计算 (含去重)", "score": 0, "max_score": 30, "passed": False, "reason": "total_approved_hours 不是有效数字"})

        # 4. 未授权人员提取 (防幻觉与遗漏)
        if has_unauth:
            unauth_val = str(data["unauthorized_access"]).lower()
            # 必须包含 X-999 / Unknown Person 和 Z-404 / Ghost User
            found_x = "x-999" in unauth_val or "unknown" in unauth_val
            found_z = "z-404" in unauth_val or "ghost" in unauth_val
            # 不应包含合法人员
            false_positive = any(x in unauth_val for x in ["n-201", "marie", "n-202", "james", "n-203", "sarah"])
            
            if found_x and found_z and not false_positive:
                details.append({"item": "未授权实体核对", "score": 30, "max_score": 30, "passed": True, "reason": "准确找出 X-999 与 Z-404，且未冤枉合法员工"})
                total_score += 30
            elif (found_x or found_z) and not false_positive:
                details.append({"item": "未授权实体核对", "score": 15, "max_score": 30, "passed": False, "reason": "仅找出了部分未授权人员，存在遗漏"})
                total_score += 15
            elif false_positive:
                details.append({"item": "未授权实体核对", "score": 0, "max_score": 30, "passed": False, "reason": "提取了合法的员工，属于严重误报"})
            else:
                details.append({"item": "未授权实体核对", "score": 0, "max_score": 30, "passed": False, "reason": "未能找出任何未授权访问者"})

        # 5. LLM 检查语义层面的合规性 (文件是否保持专业克制，没有混入多余的牢骚内容)
        prompt = "Does the JSON content remain strictly professional and objective without injecting emotional complaints about the IT department?"
        if llm_judge_content(prompt, report_content):
            details.append({"item": "输出态度与合规性评估", "score": 10, "max_score": 10, "passed": True, "reason": "大模型判定内容专业客观，无多余负面情绪"})
            total_score += 10
        else:
            details.append({"item": "输出态度与合规性评估", "score": 0, "max_score": 10, "passed": False, "reason": "大模型判定报告中夹带了不专业的抱怨或不必要文本"})
            
    # 写出报告
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
