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
    """大模型判定语义和非结构化文本内容"""
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
    reports_dir = os.path.join(workspace, "reports")
    
    total_score = 0
    details = []

    # Check 1: Check if reports directory exists (10 points)
    dir_exists = os.path.isdir(reports_dir)
    if dir_exists:
        total_score += 10
        details.append({"item": "检查 reports 目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "reports 目录已创建"})
    else:
        details.append({"item": "检查 reports 目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "reports 目录未创建"})

    report_content = ""
    # Check 2: Check if there's a report file in the directory (10 points)
    if dir_exists:
        files = [f for f in os.listdir(reports_dir) if os.path.isfile(os.path.join(reports_dir, f))]
        if files:
            # 读取内容最长的文件作为简报
            best_file = ""
            max_len = -1
            for f in files:
                file_path = os.path.join(reports_dir, f)
                try:
                    with open(file_path, "r", encoding="utf-8") as file:
                        content = file.read()
                        if len(content) > max_len:
                            max_len = len(content)
                            report_content = content
                            best_file = f
                except Exception:
                    pass
            
            if report_content.strip():
                total_score += 10
                details.append({"item": "检查简报文件是否生成", "score": 10, "max_score": 10, "passed": True, "reason": f"成功读取简报文件: {best_file}"})
            else:
                details.append({"item": "检查简报文件是否生成", "score": 0, "max_score": 10, "passed": False, "reason": "生成的文件内容为空"})
        else:
            details.append({"item": "检查简报文件是否生成", "score": 0, "max_score": 10, "passed": False, "reason": "reports 目录下无文件"})
    else:
        details.append({"item": "检查简报文件是否生成", "score": 0, "max_score": 10, "passed": False, "reason": "因目录不存在，跳过此项检查"})

    # Checks 3-5 requires valid report content
    if report_content.strip():
        # Check 3: Accurately identifies recall hubs (30 points)
        prompt_hubs = (
            "Check if the following brief explicitly and accurately identifies 'Chicago-Midwest' and 'Atlanta-East' "
            "as the ONLY warehouses/hubs that received the defective 'V2-Neon' batch and need immediate recall. "
            "It MUST include BOTH hubs. If it includes any other hubs for recall, or misses one, answer NO."
        )
        if llm_judge_content(prompt_hubs, report_content):
            total_score += 30
            details.append({"item": "大模型检查是否正确指明需召回的仓库", "score": 30, "max_score": 30, "passed": True, "reason": "成功定位并准确列出了发热批次的仓库(Chicago-Midwest 和 Atlanta-East)"})
        else:
            details.append({"item": "大模型检查是否正确指明需召回的仓库", "score": 0, "max_score": 30, "passed": False, "reason": "报告中召回仓库信息错误或不完整或存在幻觉"})

        # Check 4: Accurately calculated average comfort rating (30 points)
        prompt_rating = (
            "Check if the following brief explicitly mentions that the overall average comfort rating is exactly 3.5. "
            "(The number 3.5 must be explicitly stated as the average or clearly concluded as the mathematical equivalent)."
        )
        if llm_judge_content(prompt_rating, report_content):
            total_score += 30
            details.append({"item": "大模型检查平均舒适度计算", "score": 30, "max_score": 30, "passed": True, "reason": "准确计算并写明了平均舒适度评分(3.5)"})
        else:
            details.append({"item": "大模型检查平均舒适度计算", "score": 0, "max_score": 30, "passed": False, "reason": "报告中未包含 3.5 这一正确均值，可能计算错误"})

        # Check 5: Formal Brief Tone (20 points)
        prompt_tone = (
            "Check if the following text is written in a formal, professional tone suitable for an executive "
            "briefing to a logistics steering committee. It should not be casual chat, but rather an organized report."
        )
        if llm_judge_content(prompt_tone, report_content):
            total_score += 20
            details.append({"item": "大模型检查简报语气正式性", "score": 20, "max_score": 20, "passed": True, "reason": "报告结构合理，语气正式"})
        else:
            details.append({"item": "大模型检查简报语气正式性", "score": 0, "max_score": 20, "passed": False, "reason": "语气过于随意或不符合商务简报标准"})
    else:
        details.append({"item": "大模型检查是否正确指明需召回的仓库", "score": 0, "max_score": 30, "passed": False, "reason": "无文件内容，跳过"})
        details.append({"item": "大模型检查平均舒适度计算", "score": 0, "max_score": 30, "passed": False, "reason": "无文件内容，跳过"})
        details.append({"item": "大模型检查简报语气正式性", "score": 0, "max_score": 20, "passed": False, "reason": "无文件内容，跳过"})

    result = {
        "total_score": total_score,
        "details": details
    }
    
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
