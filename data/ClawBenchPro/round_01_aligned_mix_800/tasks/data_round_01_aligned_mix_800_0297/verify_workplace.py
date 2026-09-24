import os
import sys
import json
import httpx
from openai import OpenAI

# 1. 环境初始化
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
    """通用语义验证接口"""
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

def run_verification():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_dir = os.path.join(workspace, "pta_report")
    score_details = []
    
    # --- 维度 1: 目录结构与文件存在性 (10分) ---
    if os.path.exists(report_dir) and os.path.isdir(report_dir):
        score_details.append({"item": "检查结果目录 pta_report 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录已创建"})
    else:
        score_details.append({"item": "检查结果目录 pta_report 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到报告目录"})

    # 寻找报告文件（可能叫 report.txt, summary.md 等，需遍历）
    report_file = None
    if os.path.exists(report_dir):
        for f in os.listdir(report_dir):
            if any(ext in f.lower() for ext in ['.txt', '.md', '.json']):
                report_file = os.path.join(report_dir, f)
                break
    
    if not report_file:
        score_details.append({"item": "检查报告文件生成", "score": 0, "max_score": 90, "passed": False, "reason": "未在 pta_report 下找到任何报告文件"})
        final_score(score_details)
        return

    with open(report_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # --- 维度 2: 数据计算准确性 (50分) ---
    # 根据设计蓝图计算逻辑：
    # Alice: Sego Lily (Native) -> 3.5
    # Bob: Sagebrush (Native) -> 4.0
    # Charlie: Russian Thistle (Invasive) -> Skip
    # Daisy: Sego Lily (Native) -> 2.0
    # George: Cheatgrass (Invasive) -> Skip
    # Hannah: Bitterbrush (Native) -> 5.5
    # Total Growth = 3.5 + 4.0 + 2.0 + 5.5 = 15.0
    
    target_growth = 15.0
    # 使用 LLM 提取数值，避免正则无法处理单位（如 "15 inches"）
    extraction_prompt = "Does this report explicitly state the total growth of native plants is exactly 15 (or 15.0)?"
    if llm_judge_content(extraction_prompt, content):
        score_details.append({"item": "Native植物总生长量计算 (15.0)", "score": 50, "max_score": 50, "passed": True, "reason": "总生长量匹配"})
    else:
        score_details.append({"item": "Native植物总生长量计算 (15.0)", "score": 0, "max_score": 50, "passed": False, "reason": "总生长量不正确或未提及。正确应为15.0，查阅了：Alice(3.5), Bob(4.0), Daisy(2.0), Hannah(5.5)"})

    # --- 维度 3: 缺失学生比对 (30分) ---
    # Roster: Alice, Bob, Charlie, Daisy, Ethan, Fiona, George, Hannah
    # Submitted: Alice, Bob, Charlie, Daisy, George, Hannah
    # Missing: Ethan, Fiona
    missing_prompt = "Does this report list 'Ethan' and 'Fiona' as the students who skipped the assignment?"
    if llm_judge_content(missing_prompt, content):
        score_details.append({"item": "缺席学生名单核对 (Ethan & Fiona)", "score": 30, "max_score": 30, "passed": True, "reason": "缺席名单匹配"})
    else:
        score_details.append({"item": "缺席学生名单核对 (Ethan & Fiona)", "score": 0, "max_score": 30, "passed": False, "reason": "名单不完整或错误。应包含 Ethan 和 Fiona"})

    # --- 维度 4: 严格过滤与剔除验证 (10分) ---
    # 检查是否混入了 Invasive 植物的数据
    exclusion_prompt = "Check if the report mentions 'Russian Thistle' or 'Cheatgrass' or includes their growth (12.0 or 8.5) in the total. Answer NO if they are correctly excluded."
    is_clean = llm_judge_content("Is this report clean of any Invasive plant data (no Thistle, no Cheatgrass)?", content)
    if is_clean:
        score_details.append({"item": "入侵物种数据剔除", "score": 10, "max_score": 10, "passed": True, "reason": "成功排除了入侵物种数据"})
    else:
        score_details.append({"item": "入侵物种数据剔除", "score": 0, "max_score": 10, "passed": False, "reason": "报告中混入了非本地物种的数据"})

    final_score(score_details)

def final_score(details):
    total_score = sum(d['score'] for d in details)
    result = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    run_verification()
