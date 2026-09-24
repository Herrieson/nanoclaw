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

def extract_all_strings(data):
    """Recursively extract all string values from a JSON object."""
    strings = []
    if isinstance(data, dict):
        for k, v in data.items():
            # Include keys as well, in case the agent used titles as keys
            strings.append(str(k))
            strings.extend(extract_all_strings(v))
    elif isinstance(data, list):
        for item in data:
            strings.extend(extract_all_strings(item))
    elif isinstance(data, str):
        strings.append(data)
    return strings

def extract_all_integers(data):
    """Recursively extract all integer values from a JSON object."""
    ints = []
    if isinstance(data, dict):
        for v in data.values():
            ints.extend(extract_all_integers(v))
    elif isinstance(data, list):
        for item in data:
            ints.extend(extract_all_integers(item))
    elif isinstance(data, int):
        ints.append(data)
    # Also attempt to parse strings that might be integers
    elif isinstance(data, str) and data.isdigit():
        ints.append(int(data))
    return ints

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    submission_dir = os.path.join(workspace, "submission")
    portfolio_file = os.path.join(submission_dir, "final_portfolio.json")

    total_score = 0
    details = []

    # 1. Check if the final file exists (15 pts)
    if not os.path.exists(portfolio_file):
        details.append({"item": "检查目标文件是否存在", "score": 0, "max_score": 15, "passed": False, "reason": f"未找到 {portfolio_file}"})
        # If no file exists, we can't do anything else
        for item in ["JSON格式合法性", "正确提取目标英文诗歌", "正确剔除草稿与西班牙语诗歌", "LLM验证内容合规性", "总行数计算正确性"]:
            details.append({"item": item, "score": 0, "max_score": 0, "passed": False, "reason": "文件不存在，跳过检查"})
        
        with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
            json.dump({"total_score": 0, "details": details}, f, indent=2, ensure_ascii=False)
        return
    
    details.append({"item": "检查目标文件是否存在", "score": 15, "max_score": 15, "passed": True, "reason": "成功找到 final_portfolio.json"})
    total_score += 15

    # 2. Check JSON Schema and format (15 pts)
    try:
        with open(portfolio_file, "r", encoding="utf-8") as f:
            portfolio_data = json.load(f)
            file_content_str = json.dumps(portfolio_data, ensure_ascii=False)
        details.append({"item": "JSON格式合法性", "score": 15, "max_score": 15, "passed": True, "reason": "JSON格式合法且成功解析"})
        total_score += 15
    except Exception as e:
        details.append({"item": "JSON格式合法性", "score": 0, "max_score": 15, "passed": False, "reason": f"JSON解析失败: {e}"})
        with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2, ensure_ascii=False)
        return

    # Extract elements for deterministic checks
    all_strings = extract_all_strings(portfolio_data)
    all_ints = extract_all_integers(portfolio_data)
    combined_text = " ".join(all_strings).lower()

    # 3. Deterministic Poem Inclusion/Exclusion (30 pts)
    # Target English poems: "A Sunny Day" and "Nature's Peace"
    has_poem_a = "sunny day" in combined_text
    has_poem_e = "nature's peace" in combined_text
    
    # Excluded poems: "El Sol" (Spanish), "Writer's Block" (TODO), "Anxiety" (nervous)
    has_poem_b = "el sol" in combined_text or "tarde" in combined_text
    has_poem_c = "writer's block" in combined_text or "todo" in combined_text
    has_poem_d = "anxiety" in combined_text or "nervous" in combined_text

    inclusion_score = 0
    if has_poem_a: inclusion_score += 7
    if has_poem_e: inclusion_score += 8
    
    exclusion_score = 15
    exclusion_reasons = []
    if has_poem_b:
        exclusion_score -= 5
        exclusion_reasons.append("未剔除西班牙语诗歌")
    if has_poem_c:
        exclusion_score -= 5
        exclusion_reasons.append("未剔除包含TODO的草稿")
    if has_poem_d:
        exclusion_score -= 5
        exclusion_reasons.append("未剔除包含nervous情绪的草稿")

    poem_check_score = inclusion_score + exclusion_score
    poem_check_passed = poem_check_score == 30
    reason_str = "正确提取了目标诗歌，并排除了不合格草稿" if poem_check_passed else f"提取/剔除存在错误: 包含A={has_poem_a}, 包含E={has_poem_e}. " + ", ".join(exclusion_reasons)
    
    details.append({
        "item": "正确提取并过滤诗歌",
        "score": poem_check_score,
        "max_score": 30,
        "passed": poem_check_passed,
        "reason": reason_str
    })
    total_score += poem_check_score

    # 4. Total line count verification (20 pts)
    # The selected poems ("A Sunny Day" and "Nature's Peace") have exactly 4 lines of actual poetry each, plus 1 line for the title.
    # We should look for integers representing the count.
    # Usually it's either 8 (only body lines) or 10 (title + body).
    line_count_score = 0
    reason_lines = "未找到合理的总行数统计"
    if 8 in all_ints or 10 in all_ints:
        line_count_score = 20
        reason_lines = "成功找到合理的总行数统计 (8或10)"
    elif any(val > 0 for val in all_ints):
        # Found some other integer, partial points if they tried but miscounted
        line_count_score = 5
        reason_lines = f"找到数值 {all_ints} 但并非预期的 8 或 10"

    details.append({
        "item": "总行数计算正确性",
        "score": line_count_score,
        "max_score": 20,
        "passed": line_count_score == 20,
        "reason": reason_lines
    })
    total_score += line_count_score

    # 5. LLM Semantic Check for tone and strict compliance (20 pts)
    prompt_text = """
    Please evaluate the provided JSON content which represents a student's digital poetry portfolio.
    Check the following strict conditions:
    1. Are ALL the poems and texts strictly in English? (No Spanish or foreign languages)
    2. Are there NO notes of anxiety, stress, or unfinished markers like 'TODO', 'nervous', 'fidget'?
    3. Did the agent refrain from adding hallucinatory commentary or text not belonging to the poems?
    
    If ALL these conditions are met perfectly, answer 'YES'. Otherwise, answer 'NO'.
    """
    is_compliant = llm_judge_content(prompt_text, file_content_str)
    llm_score = 20 if is_compliant else 0
    details.append({
        "item": "LLM验证内容合规性",
        "score": llm_score,
        "max_score": 20,
        "passed": is_compliant,
        "reason": "大模型验证所有内容为纯英文、无冗余草稿标记且未发生幻觉" if is_compliant else "大模型检测出包含非英语内容、不良情绪标记或幻觉内容"
    })
    total_score += llm_score

    # Output final score
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
