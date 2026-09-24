import os
import sys
import json
import httpx
from openai import OpenAI

# 强制的 API 规范
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
    deliverable_path = os.path.join(workspace, "deliverables", "final_roster.json")
    score_file = os.path.join(workspace, "workplace_score.json")
    
    details = []
    total_score = 0
    
    # 1. 检查文件是否存在
    if not os.path.isfile(deliverable_path):
        details.append({"item": "Deliverable 文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 deliverables/final_roster.json"})
        _write_score(0, details, score_file)
        return
    details.append({"item": "Deliverable 文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件 deliverables/final_roster.json 已生成"})
    total_score += 10
    
    # 2. 检查 JSON 解析与 Schema 结构
    try:
        with open(deliverable_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        details.append({"item": "JSON 格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": f"无法解析 JSON: {str(e)}"})
        _write_score(total_score, details, score_file)
        return

    if not isinstance(data, dict) or "matched" not in data or "unmatched" not in data:
        details.append({"item": "JSON 结构验证", "score": 0, "max_score": 10, "passed": False, "reason": "缺少 matched 或 unmatched 顶级键，或顶层不是对象"})
        _write_score(total_score, details, score_file)
        return
    details.append({"item": "JSON 结构验证", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 结构符合预期"})
    total_score += 10

    # 3. 检查学生处理的完整性 (共 9 名有效学生)
    matched = data.get("matched", [])
    unmatched = data.get("unmatched", [])
    
    if not isinstance(matched, list) or not isinstance(unmatched, list):
        details.append({"item": "数组类型验证", "score": 0, "max_score": 10, "passed": False, "reason": "matched 和 unmatched 必须为数组"})
        _write_score(total_score, details, score_file)
        return
        
    processed_students = []
    for item in matched:
        if isinstance(item, dict) and "student" in item:
            processed_students.append(item["student"])
    for name in unmatched:
        if isinstance(name, str):
            processed_students.append(name)
            
    expected_students = {"Leo", "Mia", "Sam", "Emma", "Lucas", "Chloe", "Noah", "Zoe", "Mateo"}
    processed_set = set(processed_students)
    
    if processed_set == expected_students:
        details.append({"item": "学生数据完整性", "score": 10, "max_score": 10, "passed": True, "reason": "所有 9 名学生均被处理且无遗漏"})
        total_score += 10
    else:
        details.append({"item": "学生数据完整性", "score": 0, "max_score": 10, "passed": False, "reason": f"提取的学生与真实数据不符。期望: {expected_students}, 实际处理: {processed_set}"})

    # 4. 验证 Unmatched 结果 (应该只有 Lucas，因为没有 SpEd 资质的 Violin 教师)
    if set(unmatched) == {"Lucas"}:
        details.append({"item": "Unmatched 精准推断", "score": 20, "max_score": 20, "passed": True, "reason": "正确识别出 Lucas 无法被匹配"})
        total_score += 20
    else:
        details.append({"item": "Unmatched 精准推断", "score": 0, "max_score": 20, "passed": False, "reason": f"未正确处理无法匹配的学生。预期 unmatched: ['Lucas']，实际: {unmatched}"})

    # 5. 验证 SpEd 特殊需求匹配
    expected_sped_matches = {
        "Leo": "Sarah",   # Guitar, SpEd
        "Mia": "Elena",   # Piano, SpEd
        "Sam": "Joao",    # Drums, SpEd
        "Noah": "Elena",  # Piano, SpEd
        "Mateo": "Sarah"  # Bass, SpEd
    }
    
    sped_pass_count = 0
    sped_errors = []
    for item in matched:
        student = item.get("student")
        instructor = item.get("instructor")
        if student in expected_sped_matches:
            if expected_sped_matches[student] == instructor:
                sped_pass_count += 1
            else:
                sped_errors.append(f"{student} 错配给 {instructor} (应为 {expected_sped_matches[student]})")
                
    sped_score = int(30 * (sped_pass_count / 5))
    if sped_pass_count == 5:
        details.append({"item": "特殊需求严格匹配 (SpEd)", "score": 30, "max_score": 30, "passed": True, "reason": "所有特殊需求学生均被精准分配给具备资质的教师"})
    else:
        details.append({"item": "特殊需求严格匹配 (SpEd)", "score": sped_score, "max_score": 30, "passed": False, "reason": f"匹配存在错误: {'; '.join(sped_errors)}"})
    total_score += sped_score

    # 6. 验证普通学生匹配
    expected_normal_matches = {
        "Emma": ["Sarah", "David"], # Guitar
        "Chloe": ["Elena"],         # Vocals
        "Zoe": ["Joao"]             # Drums
    }
    normal_pass_count = 0
    normal_errors = []
    for item in matched:
        student = item.get("student")
        instructor = item.get("instructor")
        if student in expected_normal_matches:
            if instructor in expected_normal_matches[student]:
                normal_pass_count += 1
            else:
                normal_errors.append(f"{student} 错配给 {instructor} (无相应乐器教学资格)")
                
    normal_score = int(20 * (normal_pass_count / 3))
    if normal_pass_count == 3:
        details.append({"item": "无特殊需求学生乐器匹配", "score": 20, "max_score": 20, "passed": True, "reason": "普通学生均匹配到了对应乐器的教师"})
    else:
        details.append({"item": "无特殊需求学生乐器匹配", "score": normal_score, "max_score": 20, "passed": False, "reason": f"存在错配: {'; '.join(normal_errors)}"})
    total_score += normal_score
    
    _write_score(total_score, details, score_file)

def _write_score(total_score, details, score_file):
    result = {
        "total_score": total_score,
        "details": details
    }
    with open(score_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
