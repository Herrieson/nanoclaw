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

def save_result(score, details):
    result = {
        "total_score": score,
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    # 1. 检查 summary 目录是否存在
    summary_dir = os.path.join(workspace, "summary")
    if os.path.isdir(summary_dir):
        score += 10
        details.append({"item": "检查 summary 目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录 summary 存在"})
    else:
        details.append({"item": "检查 summary 目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "目录 summary 不存在"})
        save_result(score, details)
        return

    # 2. 检查目录下是否有报告文件
    files = [f for f in os.listdir(summary_dir) if os.path.isfile(os.path.join(summary_dir, f))]
    if files:
        score += 10
        details.append({"item": "检查报告文件生成", "score": 10, "max_score": 10, "passed": True, "reason": f"找到报告文件: {files[0]}"})
    else:
        details.append({"item": "检查报告文件生成", "score": 0, "max_score": 10, "passed": False, "reason": "summary 目录下未发现文件"})
        save_result(score, details)
        return

    # 汇总报告内容
    content = ""
    for file_name in files:
        try:
            with open(os.path.join(summary_dir, file_name), "r", encoding="utf-8") as f:
                content += f.read() + "\n"
        except Exception:
            pass

    # 3. 检查总工时计算准确性 (Sato: 4+2=6, Tanaka: 3.5, Suzuki: 5, Takahashi: 2, Watanabe: 6 -> 22.5)
    # 用原生代码确定性地查找目标数值
    import re
    # 找寻浮点数形式的 22.5
    if re.search(r'\b22\.5\b', content):
        score += 30
        details.append({"item": "检查总工时数值", "score": 30, "max_score": 30, "passed": True, "reason": "报告中成功提取并计算出了精确的总工时 22.5"})
    else:
        details.append({"item": "检查总工时数值", "score": 0, "max_score": 30, "passed": False, "reason": "未在报告中找到正确的白名单人员总工时(22.5)"})

    # 4. 检查无名英雄提取
    unregistered_heroes = ["Ghost In Shell", "Madara Uchiha", "Aizen Sosuke"]
    found_heroes = []
    for hero in unregistered_heroes:
        if hero.lower() in content.lower():
            found_heroes.append(hero)
    
    hero_score = len(found_heroes) * 10
    if len(found_heroes) == 3:
        score += 30
        details.append({"item": "检查未注册志愿者名单", "score": 30, "max_score": 30, "passed": True, "reason": "准确列出了所有3位未在白名单的记录人员"})
    else:
        score += hero_score
        details.append({"item": "检查未注册志愿者名单", "score": hero_score, "max_score": 30, "passed": False, "reason": f"只找出了 {len(found_heroes)}/3 位，找到的是: {found_heroes}"})

    # 5. LLM 检测报告的语义与排版逻辑
    prompt_text = "Does the report clearly and explicitly separate the 'unregistered/intruder volunteers' and the 'total official hours'? Does it present them in a readable and organized format?"
    is_clear = llm_judge_content(prompt_text, content)
    if is_clear:
        score += 20
        details.append({"item": "非结构化语义与排版清晰度评估", "score": 20, "max_score": 20, "passed": True, "reason": "LLM 判定报告格式清晰且准确传达了要点"})
    else:
        details.append({"item": "非结构化语义与排版清晰度评估", "score": 0, "max_score": 20, "passed": False, "reason": "报告结构混乱或语义表述不清晰"})

    save_result(score, details)

if __name__ == "__main__":
    main()
