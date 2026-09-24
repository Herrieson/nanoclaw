import os
import sys
import json
import re
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

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    resultados_dir = os.path.join(workspace, "resultados")
    
    score_details = []
    total_score = 0
    
    # 1. Check directory
    if os.path.isdir(resultados_dir):
        score_details.append({"item": "检查 'resultados' 目录是否存在", "score": 15, "max_score": 15, "passed": True, "reason": "目录存在"})
        total_score += 15
    else:
        score_details.append({"item": "检查 'resultados' 目录是否存在", "score": 0, "max_score": 15, "passed": False, "reason": "未找到 'resultados' 目录"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    # 2. Check file inside directory
    files = os.listdir(resultados_dir)
    files = [f for f in files if os.path.isfile(os.path.join(resultados_dir, f))]
    
    if len(files) > 0:
        score_details.append({"item": "检查 'resultados' 目录下是否生成了结果文件", "score": 15, "max_score": 15, "passed": True, "reason": f"找到了文件: {files[0]}"})
        total_score += 15
    else:
        score_details.append({"item": "检查 'resultados' 目录下是否生成了结果文件", "score": 0, "max_score": 15, "passed": False, "reason": "目录为空"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    # Read the file content
    file_path = os.path.join(resultados_dir, files[0])
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        score_details.append({"item": "读取结果文件", "score": 0, "max_score": 70, "passed": False, "reason": f"无法读取文件内容: {e}"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    # 3. Code-based parsing for exact answers
    # Bad Cherry Batches: B103, B105, B108
    # Good Cherry Volume: 260 (50 + 200 + 10)
    
    expected_bad_batches = ["B103", "B105", "B108"]
    found_batches = []
    for b in expected_bad_batches:
        if b in content:
            found_batches.append(b)
            
    bad_batch_score = len(found_batches) * 10
    total_score += bad_batch_score
    score_details.append({
        "item": "利用原生代码精确检查坏批次号是否出现在文本中",
        "score": bad_batch_score,
        "max_score": 30,
        "passed": bad_batch_score == 30,
        "reason": f"找到了坏批次: {found_batches}"
    })

    found_volume = "260" in content
    vol_score = 20 if found_volume else 0
    total_score += vol_score
    score_details.append({
        "item": "利用原生代码精确检查好批次总体积 (260) 是否出现在文本中",
        "score": vol_score,
        "max_score": 20,
        "passed": found_volume,
        "reason": "成功提取总体积" if found_volume else "未在文本中找到260"
    })

    # 4. LLM semantic check for correct mapping and tone
    llm_prompt = (
        "Check if the document explicitly states two concepts clearly: "
        "1. The bad cherry batches are specifically B103, B105, and B108. "
        "2. The total volume of good cherry stain is 260 liters. "
        "Are these two facts correctly attributed without mixing them up?"
    )
    llm_pass = llm_judge_content(llm_prompt, content)
    llm_score = 20 if llm_pass else 0
    total_score += llm_score
    score_details.append({
        "item": "利用大模型检查语意和数值指代是否正确",
        "score": llm_score,
        "max_score": 20,
        "passed": llm_pass,
        "reason": "大模型判定内容指代清晰正确" if llm_pass else "大模型判定指代混乱或有误"
    })
    
    # Save score
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2)

if __name__ == "__main__":
    verify()
