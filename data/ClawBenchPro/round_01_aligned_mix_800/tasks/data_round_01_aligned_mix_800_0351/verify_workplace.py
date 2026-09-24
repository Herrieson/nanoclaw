import os
import sys
import json
import re
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

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

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    deliverables_dir = os.path.join(workspace, "deliverables")
    
    score_details = []
    total_score = 0
    
    # Check 1: deliverables directory (15 points)
    if os.path.isdir(deliverables_dir):
        score_details.append({"item": "检查目标输出目录 deliverables 是否存在", "score": 15, "max_score": 15, "passed": True, "reason": "deliverables 目录存在"})
        total_score += 15
    else:
        score_details.append({"item": "检查目标输出目录 deliverables 是否存在", "score": 0, "max_score": 15, "passed": False, "reason": "deliverables 目录不存在"})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=4)
        return

    # Check 2: Find output file (15 points)
    files = [f for f in os.listdir(deliverables_dir) if os.path.isfile(os.path.join(deliverables_dir, f))]
    if len(files) > 0:
        score_details.append({"item": "检查是否在目录中生成了汇报文档", "score": 15, "max_score": 15, "passed": True, "reason": f"找到文件: {files[0]}"})
        total_score += 15
        
        with open(os.path.join(deliverables_dir, files[0]), "r", encoding="utf-8") as f:
            content = f.read()
            
        # Check 3: Precise Value Extraction for Total Cost (30 points)
        # 150 + 120 + 15.5 + 25 = 310.5
        if "310.50" in content or "310.5" in content:
            score_details.append({"item": "精确匹配安全设备总花费计算结果 ($310.50)", "score": 30, "max_score": 30, "passed": True, "reason": "精确包含数字 310.50"})
            total_score += 30
        else:
            # Check if art supplies were incorrectly included (e.g. 404.00 total)
            if "404" in content:
                score_details.append({"item": "精确匹配安全设备总花费计算结果 ($310.50)", "score": 0, "max_score": 30, "passed": False, "reason": "计算错误，且包含了艺术用品的花费。"})
            else:
                score_details.append({"item": "精确匹配安全设备总花费计算结果 ($310.50)", "score": 0, "max_score": 30, "passed": False, "reason": "未找到正确的总价 310.50"})

        # Check 4: LLM Check for safety hazards from multiple sources (40 points)
        prompt_hazards = """
        Check if the document mentions ALL THREE of the following specific safety hazards:
        1. Crew missing hardhats (or hardhat warnings).
        2. Unstable scaffolding.
        3. Extension cord in a puddle.
        Reply 'YES' only if all three distinct hazards are summarized. Reply 'NO' if any are missing or hallucinated.
        """
        if llm_judge_content(prompt_hazards, content):
            score_details.append({"item": "大模型校验是否完整汇集了多源安全隐患（图片+JSON）", "score": 40, "max_score": 40, "passed": True, "reason": "文档包含了硬帽、脚手架、积水电线三大隐患"})
            total_score += 40
        else:
            score_details.append({"item": "大模型校验是否完整汇集了多源安全隐患（图片+JSON）", "score": 0, "max_score": 40, "passed": False, "reason": "隐患收集不全，可能遗漏了 OCR 或 JSON 数据源"})
            
    else:
        score_details.append({"item": "检查是否在目录中生成了汇报文档", "score": 0, "max_score": 15, "passed": False, "reason": "deliverables 目录为空"})

    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()
