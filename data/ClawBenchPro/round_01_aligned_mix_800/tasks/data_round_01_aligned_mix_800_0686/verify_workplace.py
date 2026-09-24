import os
import sys
import json
import glob
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

def extract_all_strings(data):
    """Recursively extract all strings from a parsed JSON structure."""
    strings = []
    if isinstance(data, dict):
        for k, v in data.items():
            strings.extend(extract_all_strings(v))
    elif isinstance(data, list):
        for item in data:
            strings.extend(extract_all_strings(item))
    elif isinstance(data, str):
        strings.append(data.strip())
    else:
        if data is not None:
            strings.append(str(data).strip())
    return strings

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    showcase_dir = os.path.join(workspace, "showcase_prep")
    
    score_details = []
    total_score = 0
    
    # 1. Directory exists (10 points)
    if os.path.isdir(showcase_dir):
        score_details.append({"item": "检查目标输出目录 showcase_prep 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录已成功创建"})
        total_score += 10
    else:
        score_details.append({"item": "检查目标输出目录 showcase_prep 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 showcase_prep 目录"})
        with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2, ensure_ascii=False)
        return

    # 2. Files exist and are valid JSON (10 points)
    json_files = glob.glob(os.path.join(showcase_dir, "*.json"))
    valid_json_contents = []
    if len(json_files) >= 2:
        for jf in json_files:
            try:
                with open(jf, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    valid_json_contents.append(extract_all_strings(data))
            except Exception:
                pass
        
        if len(valid_json_contents) >= 2:
            score_details.append({"item": "检查是否存在至少两个合法的JSON文件", "score": 10, "max_score": 10, "passed": True, "reason": "找到合法JSON文件"})
            total_score += 10
        else:
            score_details.append({"item": "检查是否存在至少两个合法的JSON文件", "score": 5, "max_score": 10, "passed": False, "reason": "存在文件但JSON解析失败，或数量不足"})
            total_score += 5
    else:
        score_details.append({"item": "检查是否存在至少两个合法的JSON文件", "score": 0, "max_score": 10, "passed": False, "reason": "JSON文件数量不足2个"})
    
    # Combine all strings across all valid JSON files to find our targets
    all_extracted_strings = []
    for strings in valid_json_contents:
        all_extracted_strings.extend(strings)
    
    # Flatten and normalize string matching
    # We will do exact matches on substrings to account for structure like ["Bob Builder"]
    all_str_concat = " || ".join(all_extracted_strings)

    # 3. Volunteer verification (40 points)
    target_uncleared = ["Bob Builder", "Karen Smith"]
    cleared_volunteers = ["Maria Silva", "Sarah Jenkins", "Carlos Mendes", "Lucia Santos", "John Doe"]
    
    vol_score = 0
    vol_reasons = []
    if "Bob Builder" in all_str_concat:
        vol_score += 10
        vol_reasons.append("成功识别 Bob Builder")
    else:
        vol_reasons.append("漏掉 Bob Builder")
        
    if "Karen Smith" in all_str_concat:
        vol_score += 10
        vol_reasons.append("成功识别 Karen Smith")
    else:
        vol_reasons.append("漏掉 Karen Smith")
        
    has_cleared = any(cv in all_str_concat for cv in cleared_volunteers)
    if not has_cleared:
        vol_score += 20
        vol_reasons.append("未包含任何已通过背景审查的家长(无幻觉/无误判)")
    else:
        vol_reasons.append("误将已通过背景审查的家长纳入名单")

    score_details.append({
        "item": "验证未通过背景审查的家长名单准确性",
        "score": vol_score,
        "max_score": 40,
        "passed": vol_score == 40,
        "reason": ", ".join(vol_reasons)
    })
    total_score += vol_score

    # 4. Student consultation verification (40 points)
    target_students = ["Mia", "David", "Omar"]
    valid_students = ["Leo", "Sam", "Ana"]
    
    stu_score = 0
    stu_reasons = []
    if "Mia" in all_str_concat:
        stu_score += 10
        stu_reasons.append("成功识别 Mia")
    else:
        stu_reasons.append("漏掉 Mia")
        
    if "David" in all_str_concat:
        stu_score += 10
        stu_reasons.append("成功识别 David")
    else:
        stu_reasons.append("漏掉 David")

    if "Omar" in all_str_concat:
        stu_score += 10
        stu_reasons.append("成功识别 Omar")
    else:
        stu_reasons.append("漏掉 Omar")
        
    has_valid_stu = any(vs in all_str_concat for vs in valid_students)
    if not has_valid_stu:
        stu_score += 10
        stu_reasons.append("未包含任何符合乐器要求的不必要面谈学生(无幻觉/无误判)")
    else:
        stu_reasons.append("误将乐器选择正确的学生纳入面谈名单")

    score_details.append({
        "item": "验证需要乐器面谈的学生名单准确性",
        "score": stu_score,
        "max_score": 40,
        "passed": stu_score == 40,
        "reason": ", ".join(stu_reasons)
    })
    total_score += stu_score

    # Write output
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
