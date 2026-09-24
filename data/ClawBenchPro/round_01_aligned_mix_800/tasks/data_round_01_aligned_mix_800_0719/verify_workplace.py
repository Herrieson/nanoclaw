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
    for_boss_dir = os.path.join(workspace, "workspace", "for_boss")
    
    score_details = []
    total_score = 0
    
    # Item 1: Check if the report directory and file exist
    file_exists = False
    report_content = ""
    if os.path.isdir(for_boss_dir):
        files = os.listdir(for_boss_dir)
        if files:
            file_exists = True
            # Assuming the agent created at least one file here
            report_path = os.path.join(for_boss_dir, files[0])
            try:
                with open(report_path, "r", encoding="utf-8") as f:
                    report_content = f.read()
            except Exception:
                pass

    if file_exists and report_content.strip():
        score_details.append({"item": "检查报告文件是否生成且有内容", "score": 10, "max_score": 10, "passed": True, "reason": "报告文件已生成且非空"})
        total_score += 10
    else:
        score_details.append({"item": "检查报告文件是否生成且有内容", "score": 0, "max_score": 10, "passed": False, "reason": "未找到报告文件或文件为空"})
        # If no file, we cannot proceed with LLM checks, fill rest with 0
        score_details.extend([
            {"item": "利用大模型检查是否正确包含故障机器ID", "score": 0, "max_score": 30, "passed": False, "reason": "缺少报告文件"},
            {"item": "利用大模型检查总金额计算是否正确", "score": 0, "max_score": 30, "passed": False, "reason": "缺少报告文件"},
            {"item": "利用大模型检查是否过滤无关信息", "score": 0, "max_score": 15, "passed": False, "reason": "缺少报告文件"},
            {"item": "利用大模型检查报告专业度", "score": 0, "max_score": 15, "passed": False, "reason": "缺少报告文件"}
        ])
        return total_score, score_details

    # Item 2: Machine IDs check (30 points)
    prompt_ids = "Does the following report explicitly state that 'MACH-002' and 'MACH-003' are the machines that need repair or have a critical status?"
    if llm_judge_content(prompt_ids, report_content):
        score_details.append({"item": "利用大模型检查是否正确包含故障机器ID", "score": 30, "max_score": 30, "passed": True, "reason": "准确识别了 MACH-002 和 MACH-003"})
        total_score += 30
    else:
        score_details.append({"item": "利用大模型检查是否正确包含故障机器ID", "score": 0, "max_score": 30, "passed": False, "reason": "未准确提及 MACH-002 和 MACH-003，或包含错误机器ID"})

    # Item 3: Cost calculation check (30 points) - Exact value check via LLM
    prompt_cost = "Does the following report explicitly state the total cost of the parts as exactly 2050 (or $2050, 2050.00)? It must be exactly 2050."
    if llm_judge_content(prompt_cost, report_content):
        score_details.append({"item": "利用大模型检查总金额计算是否正确", "score": 30, "max_score": 30, "passed": True, "reason": "准确计算并写明总金额为 2050"})
        total_score += 30
    else:
        score_details.append({"item": "利用大模型检查总金额计算是否正确", "score": 0, "max_score": 30, "passed": False, "reason": "总金额计算错误或未在报告中明确给出"})

    # Item 4: Ignore distractions check (15 points)
    prompt_ignore = "Is the following report entirely FREE of any mentions of gardening, vegetables, mustard greens, orchids, or Vietnamese music tracks (Cai luong)? Answer YES if it is clean of these topics."
    if llm_judge_content(prompt_ignore, report_content):
        score_details.append({"item": "利用大模型检查是否过滤无关信息", "score": 15, "max_score": 15, "passed": True, "reason": "报告中不包含园艺或音乐等无关杂物"})
        total_score += 15
    else:
        score_details.append({"item": "利用大模型检查是否过滤无关信息", "score": 0, "max_score": 15, "passed": False, "reason": "报告中混入了用户的个人杂物信息，将被Boss责骂"})

    # Item 5: Professional Tone (15 points)
    prompt_tone = "Is the tone of the following report neat, professional, and appropriate to be handed directly to a boss or manager?"
    if llm_judge_content(prompt_tone, report_content):
        score_details.append({"item": "利用大模型检查报告专业度", "score": 15, "max_score": 15, "passed": True, "reason": "报告具备良好的专业性"})
        total_score += 15
    else:
        score_details.append({"item": "利用大模型检查报告专业度", "score": 0, "max_score": 15, "passed": False, "reason": "报告语气不合适或格式混乱"})

    return total_score, score_details

if __name__ == "__main__":
    score, details = verify()
    
    result = {
        "total_score": score,
        "details": details
    }
    
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
