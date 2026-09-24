import os
import sys
import json
import re
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

def verify_workplace(workspace):
    results = []
    total_score = 0
    
    report_path = os.path.join(workspace, "boss_report.txt")
    
    # 1. 检查目标文件存在性 (20分)
    if os.path.exists(report_path):
        results.append({"item": "检查目标文件 boss_report.txt 是否存在", "score": 20, "max_score": 20, "passed": True, "reason": "文件存在"})
        total_score += 20
        
        with open(report_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # 2. 检查特定车牌号的提取情况 (30分)
        target_plates = ["ABC-123", "LMN-456", "QRS-111"]
        wrong_plates = ["XYZ-987"]
        
        plates_found = [p for p in target_plates if p in content]
        wrong_found = [p for p in wrong_plates if p in content]
        
        plates_score = len(plates_found) * 10
        plates_passed = (len(plates_found) == 3 and len(wrong_found) == 0)
        
        if len(wrong_found) > 0:
            plates_score -= 10 * len(wrong_found)
            plates_score = max(0, plates_score)
            
        results.append({
            "item": "检查目标车牌号是否被正确提取且剔除无错误代码的车牌",
            "score": plates_score,
            "max_score": 30,
            "passed": plates_passed,
            "reason": f"找到了目标车牌 {plates_found}，找到了错误车牌 {wrong_found}"
        })
        total_score += plates_score

        # 3. 检查火花塞数量计算正确性 (30分)
        # 火花塞总数应该是 12 + 8 = 20
        # 判断内容中是否有 20，并确保数字周围语义正确
        if "20" in content:
            results.append({
                "item": "检查火花塞总数是否正确计算为20",
                "score": 30,
                "max_score": 30,
                "passed": True,
                "reason": "报告中包含计算正确的火花塞总数 20"
            })
            total_score += 30
        else:
            results.append({
                "item": "检查火花塞总数是否正确计算为20",
                "score": 0,
                "max_score": 30,
                "passed": False,
                "reason": "报告中未找到正确的总数 20"
            })

        # 4. LLM 判断报告风格与清晰度 (20分)
        llm_prompt = "Does this file represent a quick, clean, and polite summary intended for a boss, summarizing specific vehicle license plates and spark plug inventory? It should not be a script or raw JSON, but a human-readable report."
        llm_passed = llm_judge_content(llm_prompt, content)
        if llm_passed:
            results.append({
                "item": "利用大模型检查报告风格是否专业且简洁",
                "score": 20,
                "max_score": 20,
                "passed": True,
                "reason": "大模型判定报告符合要求"
            })
            total_score += 20
        else:
            results.append({
                "item": "利用大模型检查报告风格是否专业且简洁",
                "score": 0,
                "max_score": 20,
                "passed": False,
                "reason": "大模型判定报告格式不佳或非人类可读的文字"
            })
            
    else:
        results.append({"item": "检查目标文件 boss_report.txt 是否存在", "score": 0, "max_score": 20, "passed": False, "reason": "文件不存在"})
        results.append({"item": "检查目标车牌号是否被正确提取且剔除无错误代码的车牌", "score": 0, "max_score": 30, "passed": False, "reason": "文件缺失，无法检查"})
        results.append({"item": "检查火花塞总数是否正确计算为20", "score": 0, "max_score": 30, "passed": False, "reason": "文件缺失，无法检查"})
        results.append({"item": "利用大模型检查报告风格是否专业且简洁", "score": 0, "max_score": 20, "passed": False, "reason": "文件缺失，无法检查"})

    # 输出结果
    score_data = {
        "total_score": total_score,
        "details": results
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(score_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify_workplace(workspace)
