import os
import sys
import json
import httpx
from openai import OpenAI
import csv

# Setup for LLM
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
    results = {"total_score": 0, "details": []}
    
    def add_detail(item, score, max_score, passed, reason):
        results["details"].append({
            "item": item, "score": score, "max_score": max_score, "passed": passed, "reason": reason
        })
        results["total_score"] += score

    # 1. Check Directory Structure (10 points)
    target_dir = os.path.join(workspace, "for_sale")
    if os.path.isdir(target_dir):
        add_detail("目录结构检查", 10, 10, True, "找到 for_sale 目录")
    else:
        add_detail("目录结构检查", 0, 10, False, "未找到 for_sale 目录")
        # Critical failure, but we continue to check if files are in root
        target_dir = workspace

    # 2. Check catalog.json Logic (50 points total)
    catalog_path = os.path.join(target_dir, "catalog.json")
    if os.path.exists(catalog_path):
        try:
            with open(catalog_path, 'r') as f:
                data = json.load(f)
            
            # Sub-task: Deduplication & Max Score (20 points)
            # Spider-Man 129 should be 9.2, not 8.5
            spidey = next((item for item in data if item["Title"] == "The Amazing Spider-Man" and item["Issue"] == "129"), None)
            if spidey and str(spidey.get("Condition_Score")) == "9.2":
                add_detail("数据去重与最高分保留", 20, 20, True, "成功识别重复项并保留最高Condition_Score")
            else:
                add_detail("数据去重与最高分保留", 0, 20, False, "未正确处理重复项或未选择最高分")

            # Sub-task: Filtering Logic (20 points)
            # Should NOT contain X-Men 1 (4.5), X-Men 101 (5.5), or Fantastic Four 48 (Empty Value)
            titles = [item["Title"] for item in data]
            bad_titles = ["X-Men", "Fantastic Four"] 
            # Note: X-Men Issue 1 and 101 are both < 6.0. FF 48 has no value.
            # Green Lantern (9.4), Action Comics (7.0), Batman (8.0), Iron Man (9.6), Avengers (9.0), Spidey (9.2) should be there.
            filtered_correctly = all(t in ["The Amazing Spider-Man", "Batman", "The Avengers", "Iron Man", "Green Lantern", "Action Comics"] for t in titles)
            if filtered_correctly and len(data) == 6:
                add_detail("数据过滤逻辑", 20, 20, True, "成功过滤低于6.0分及缺少价值的项目")
            else:
                add_detail("数据过滤逻辑", 5, 20, False, f"过滤逻辑有误，结果包含 {len(data)} 项")

            # Sub-task: Sorting Logic (10 points)
            values = [float(item["Market_Value"]) for item in data]
            if values == sorted(values, reverse=True):
                add_detail("排序检查", 10, 10, True, "catalog.json 已按价值降序排列")
            else:
                add_detail("排序检查", 0, 10, False, "未按价值降序排列")

        except Exception as e:
            add_detail("JSON 格式检查", 0, 50, False, f"catalog.json 无法解析: {e}")
    else:
        add_detail("catalog.json 存在性", 0, 50, False, "未找到 catalog.json")

    # 3. Check summary.txt (40 points total)
    summary_path = os.path.join(target_dir, "summary.txt")
    if os.path.exists(summary_path):
        with open(summary_path, 'r') as f:
            content = f.read()
        
        # Sub-task: Quantitative Calculation (20 points)
        # 2500+1500+3000+5000+800+4500 = 17300
        # Count = 6
        correct_sum = "17300" in content
        correct_count = "6" in content
        if correct_sum and correct_count:
            add_detail("数值统计准确性", 20, 20, True, "统计金额 (17300) 和数量 (6) 均正确")
        else:
            add_detail("数值统计准确性", 0, 20, False, f"统计数值不匹配。内容片段: {content[:50]}")

        # Sub-task: Professional Tone & Persona (20 points)
        prompt = "Does this summary sound like a professional report written to help a father sell his collection? Does it clearly state the total value and count as requested?"
        if llm_judge_content(prompt, content):
            add_detail("总结报告语义验证", 20, 20, True, "报告语气专业且包含所有要求要素")
        else:
            add_detail("总结报告语义验证", 0, 20, False, "大模型判定报告语气不符或关键信息缺失")
    else:
        add_detail("summary.txt 存在性", 0, 40, False, "未找到 summary.txt")

    # Final Output
    with open("workplace_score.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    verify()
