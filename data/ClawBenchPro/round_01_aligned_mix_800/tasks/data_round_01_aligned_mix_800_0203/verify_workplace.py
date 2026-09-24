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
    deliverables_dir = os.path.join(workspace, "deliverables")
    summary_file = os.path.join(deliverables_dir, "board_summary.json")
    
    details = []
    total_score = 0
    
    # 1. 目录检查 (10分)
    if os.path.exists(deliverables_dir) and os.path.isdir(deliverables_dir):
        details.append({"item": "检查交付目录 deliverables 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录存在"})
        total_score += 10
    else:
        details.append({"item": "检查交付目录 deliverables 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "目录不存在"})
        
    # 2. 文件与格式检查 (15分)
    data = None
    if os.path.exists(summary_file):
        try:
            with open(summary_file, 'r', encoding='utf-8') as f:
                content = f.read()
                data = json.loads(content)
            details.append({"item": "检查 board_summary.json 是否存在且为合法 JSON", "score": 15, "max_score": 15, "passed": True, "reason": "文件存在且 JSON 格式合法"})
            total_score += 15
        except json.JSONDecodeError:
            details.append({"item": "检查 board_summary.json 是否存在且为合法 JSON", "score": 0, "max_score": 15, "passed": False, "reason": "JSON 格式解析失败"})
    else:
        details.append({"item": "检查 board_summary.json 是否存在且为合法 JSON", "score": 0, "max_score": 15, "passed": False, "reason": "文件缺失"})

    # 3. 核心字段验证与数值提取 (75分)
    if data:
        # 3.1 检查幻觉字段 (10分)
        expected_keys = {"recycling", "compost", "landfill", "unregistered_intruders"}
        allowed_keys = expected_keys | {"rostered_students_total_weight", "official_roster", "totals", "total_weight", "weights", "rostered_totals"}
        actual_keys = set(data.keys())
        if actual_keys.issubset(allowed_keys):
            details.append({"item": "无多余的捏造字段检查", "score": 10, "max_score": 10, "passed": True, "reason": "没有捏造多余字段"})
            total_score += 10
        else:
            details.append({"item": "无多余的捏造字段检查", "score": 0, "max_score": 10, "passed": False, "reason": f"发现多余字段: {actual_keys - allowed_keys}"})

        # 3.2 检查入侵者名单 (20分)
        intruders = data.get("unregistered_intruders", [])
        if isinstance(intruders, list):
            def _intruder_name(value):
                if isinstance(value, str):
                    return value.lower()
                if isinstance(value, dict):
                    for key in ("name", "student", "student_name", "full_name"):
                        item = value.get(key)
                        if isinstance(item, str):
                            return item.lower()
                    return json.dumps(value, ensure_ascii=False).lower()
                return str(value).lower()
            intruders_lower = [_intruder_name(i) for i in intruders]
            if "mason" in intruders_lower and "sophia" in intruders_lower and len(intruders_lower) == 2:
                details.append({"item": "正确识别非名单学生 (Mason, Sophia)", "score": 20, "max_score": 20, "passed": True, "reason": "完全找出了两名不在 roster 上的学生"})
                total_score += 20
            elif "mason" in intruders_lower or "sophia" in intruders_lower:
                details.append({"item": "正确识别非名单学生 (Mason, Sophia)", "score": 10, "max_score": 20, "passed": False, "reason": "仅找出了部分非名单学生"})
                total_score += 10
            else:
                details.append({"item": "正确识别非名单学生 (Mason, Sophia)", "score": 0, "max_score": 20, "passed": False, "reason": "未正确识别入侵学生"})
        else:
            details.append({"item": "正确识别非名单学生 (Mason, Sophia)", "score": 0, "max_score": 20, "passed": False, "reason": "字段格式错误，不是列表"})

        # 3.3 检查各分类垃圾总重计算 - 必须排除入侵者数据，并且正确映射分类 (45分)
        # Expected totals: R=42, C=20, L=15
        totals_data = data
        for key in ("rostered_students_total_weight", "totals", "total_weight", "weights", "rostered_totals"):
            candidate = data.get(key)
            if isinstance(candidate, dict):
                totals_data = candidate
                break
        val_r = totals_data.get("recycling", 0)
        val_c = totals_data.get("compost", 0)
        val_l = totals_data.get("landfill", 0)
        
        # Recycling Check
        if val_r == 42:
            details.append({"item": "Recycling 总重计算 (42 lbs)", "score": 15, "max_score": 15, "passed": True, "reason": "计算准确"})
            total_score += 15
        else:
            details.append({"item": "Recycling 总重计算 (42 lbs)", "score": 0, "max_score": 15, "passed": False, "reason": f"计算错误，预期 42，实际 {val_r}"})

        # Compost Check
        if val_c == 20:
            details.append({"item": "Compost 总重计算 (20 lbs)", "score": 15, "max_score": 15, "passed": True, "reason": "计算准确"})
            total_score += 15
        else:
            details.append({"item": "Compost 总重计算 (20 lbs)", "score": 0, "max_score": 15, "passed": False, "reason": f"计算错误，预期 20，实际 {val_c}"})

        # Landfill Check
        if val_l == 15:
            details.append({"item": "Landfill 总重计算 (15 lbs)", "score": 15, "max_score": 15, "passed": True, "reason": "计算准确"})
            total_score += 15
        else:
            details.append({"item": "Landfill 总重计算 (15 lbs)", "score": 0, "max_score": 15, "passed": False, "reason": f"计算错误，预期 15，实际 {val_l}"})

    # 将结果写入文件
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({
            "total_score": total_score,
            "details": details
        }, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
