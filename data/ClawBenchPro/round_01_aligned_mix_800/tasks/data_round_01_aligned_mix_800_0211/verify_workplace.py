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

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results_dir = os.path.join(workspace, "results")
    
    score_details = []
    total_score = 0
    
    # 1. 检查 results 目录
    if os.path.isdir(results_dir):
        score_details.append({"item": "检查 results 目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录存在"})
        total_score += 10
    else:
        score_details.append({"item": "检查 results 目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "目录不存在"})
        
    # 2. 检查 workout_playlist.txt
    playlist_file = os.path.join(results_dir, "workout_playlist.txt")
    if os.path.isfile(playlist_file):
        score_details.append({"item": "检查 workout_playlist.txt 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        total_score += 10
        
        with open(playlist_file, "r", encoding="utf-8") as f:
            content = f.read().lower()
            
        required_tracks = ["iron will", "adrenaline rush", "heavy lifts", "max reps"]
        forbidden_tracks = ["soft lullaby", "windshield wipers in the rain", "sunday morning"]
        
        req_passed = all(track in content for track in required_tracks)
        forb_passed = all(track not in content for track in forbidden_tracks)
        
        if req_passed and forb_passed:
            score_details.append({"item": "检查 BPM>120 过滤逻辑", "score": 35, "max_score": 35, "passed": True, "reason": "精准包含所需曲目，且无误报曲目"})
            total_score += 35
        else:
            score_details.append({"item": "检查 BPM>120 过滤逻辑", "score": 0, "max_score": 35, "passed": False, "reason": "曲目过滤错误（漏报或包含了低BPM曲目）"})
    else:
        score_details.append({"item": "检查 workout_playlist.txt 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        score_details.append({"item": "检查 BPM>120 过滤逻辑", "score": 0, "max_score": 35, "passed": False, "reason": "文件缺失，无法检查"})

    # 3. 检查 windshield_costs.txt
    costs_file = os.path.join(results_dir, "windshield_costs.txt")
    if os.path.isfile(costs_file):
        score_details.append({"item": "检查 windshield_costs.txt 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        total_score += 10
        
        with open(costs_file, "r", encoding="utf-8") as f:
            content = f.read()
            
        # 提取数字进行严格校验
        numbers = re.findall(r"[-+]?\d*\.\d+|\d+", content)
        if "625.75" in numbers:
            score_details.append({"item": "检查成本求和计算", "score": 25, "max_score": 25, "passed": True, "reason": "成功提取 625.75"})
            total_score += 25
        else:
            score_details.append({"item": "检查成本求和计算", "score": 0, "max_score": 25, "passed": False, "reason": "结果未包含正确的计算总计(625.75)"})
            
        # 4. LLM 检查是否简洁 (无冗长汇报)
        prompt = "Does this text look like a simple cost report or just a number without a long presentation, formal email body, or unnecessary explanations?"
        is_simple = llm_judge_content(prompt, content)
        if is_simple:
            score_details.append({"item": "LLM 检查输出是否符合简洁要求", "score": 10, "max_score": 10, "passed": True, "reason": "输出简洁，无冗长介绍"})
            total_score += 10
        else:
            score_details.append({"item": "LLM 检查输出是否符合简洁要求", "score": 0, "max_score": 10, "passed": False, "reason": "包含了用户反感的冗长汇报或展示"})
            
    else:
        score_details.append({"item": "检查 windshield_costs.txt 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        score_details.append({"item": "检查成本求和计算", "score": 0, "max_score": 25, "passed": False, "reason": "文件缺失，无法检查"})
        score_details.append({"item": "LLM 检查输出是否符合简洁要求", "score": 0, "max_score": 10, "passed": False, "reason": "文件缺失"})

    # 输出结果
    result = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
