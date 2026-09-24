import os
import sys
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

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

def extract_strings(data):
    """递归提取结构化 JSON 中的所有字符串（键和值），避免模糊正则匹配"""
    strings = set()
    if isinstance(data, dict):
        for k, v in data.items():
            strings.add(str(k).strip())
            strings.update(extract_strings(v))
    elif isinstance(data, list):
        for item in data:
            strings.update(extract_strings(item))
    elif isinstance(data, str):
        strings.add(data.strip())
    return strings

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    deliverable_path = os.path.join(workspace, "deliverables", "shortlist.json")
    score_file = os.path.join(workspace, "workplace_score.json")
    
    score_details = []
    total_score = 0
    
    # 1. 物理目录与 JSON 格式严格检查 (15 分)
    if not os.path.exists(deliverable_path):
        score_details.append({"item": "检查交付物是否存在", "score": 0, "max_score": 15, "passed": False, "reason": "未找到 deliverables/shortlist.json"})
        with open(score_file, "w", encoding="utf-8") as f:
            json.dump({"total_score": 0, "details": score_details}, f, indent=2, ensure_ascii=False)
        return
        
    try:
        with open(deliverable_path, "r", encoding="utf-8") as f:
            file_content = f.read()
            parsed_data = json.loads(file_content)
        score_details.append({"item": "检查交付物是否为合法JSON", "score": 15, "max_score": 15, "passed": True, "reason": "成功通过原生 JSON 解析"})
        total_score += 15
    except Exception as e:
        score_details.append({"item": "检查交付物是否为合法JSON", "score": 0, "max_score": 15, "passed": False, "reason": f"结构化解析失败: {e}"})
        with open(score_file, "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2, ensure_ascii=False)
        return

    extracted_strings = extract_strings(parsed_data)
    valid_candidates = {"Neon Echoes", "The Crimson Void", "Midnight Runners", "Static Noise", "Rebel Yell", "The Blacklisted", "Fading Light", "Pop Sensations", "Electric Dreams"}
    found_bands = extracted_strings.intersection(valid_candidates)

    # 2. 目标对象完整性验证 (25 分)
    expected_bands = {"Neon Echoes", "The Crimson Void", "Fading Light", "Electric Dreams"}
    missing = expected_bands - found_bands
    if not missing:
        total_score += 25
        score_details.append({"item": "验证最终入围名单完整性", "score": 25, "max_score": 25, "passed": True, "reason": "所有 4 个符合条件的乐队均已被精准提取"})
    else:
        earned = int((4 - len(missing)) * 6.25)
        total_score += earned
        score_details.append({"item": "验证最终入围名单完整性", "score": earned, "max_score": 25, "passed": False, "reason": f"遗漏了合规乐队: {missing}"})

    # 3. 约束过滤：预算与流派 (20 分)
    budget_genre_fails = {"Midnight Runners", "Pop Sensations", "Static Noise"}
    bg_included = budget_genre_fails.intersection(found_bands)
    if not bg_included:
        total_score += 20
        score_details.append({"item": "验证预算与流派过滤准确性", "score": 20, "max_score": 20, "passed": True, "reason": "完全剔除了预算超标或流派不符的乐队"})
    else:
        score_details.append({"item": "验证预算与流派过滤准确性", "score": 0, "max_score": 20, "passed": False, "reason": f"未正确应用规则，错误包含了: {bg_included}"})

    # 4. 约束过滤：黑名单与合规审计 (20 分)
    compliance_fails = {"The Blacklisted", "Rebel Yell"}
    c_included = compliance_fails.intersection(found_bands)
    if not c_included:
        total_score += 20
        score_details.append({"item": "验证黑名单与风控合规准确性", "score": 20, "max_score": 20, "passed": True, "reason": "严格排除了在黑名单上或舆情风险评级不达标的乐队"})
    else:
        score_details.append({"item": "验证黑名单与风控合规准确性", "score": 0, "max_score": 20, "passed": False, "reason": f"出现严重合规漏洞，错误包含了高危乐队: {c_included}"})

    # 5. LLM 非结构化语义防御：幻觉与作弊探针 (20 分)
    prompt = """
    The user was required to output a JSON containing ONLY a shortlist of band names and their genres.
    Check the provided JSON string. 
    Does it strictly contain ONLY valid band data, WITHOUT any fabricated band names (not from the original list), conversational filler text, or unrequested nested metadata? 
    Answer 'YES' if it is strictly clean and free of hallucinations. Answer 'NO' if you detect extra fake entities or structural noise.
    """
    is_clean = llm_judge_content(prompt, file_content)
    if is_clean:
        total_score += 20
        score_details.append({"item": "LLM语义防御探针 (幻觉与Schema检验)", "score": 20, "max_score": 20, "passed": True, "reason": "输出干净，无大模型捏造的多余节点或对话文本"})
    else:
        score_details.append({"item": "LLM语义防御探针 (幻觉与Schema检验)", "score": 0, "max_score": 20, "passed": False, "reason": "大模型判定JSON存在明显的幻觉字段、非要求实体或结构被破坏"})

    with open(score_file, "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
