import os
import sys
import json
import csv
import httpx
from openai import OpenAI

# 🔒 强制 API 规范：初始化客户端
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
                {"role": "system", "content": "You are a strict security auditor. Answer ONLY with 'YES' or 'NO'."},
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
    investigation_dir = os.path.join(workspace, "investigation")
    trespassers_file = os.path.join(investigation_dir, "trespassers.txt")
    missing_json_file = os.path.join(investigation_dir, "missing_vinyls.json")
    
    score_details = []
    total_score = 0

    # 1. 检查目录结构 (10分)
    if os.path.exists(investigation_dir) and os.path.isdir(investigation_dir):
        score_details.append({"item": "目录结构检查", "score": 10, "max_score": 10, "passed": True, "reason": "investigation 目录已创建"})
        total_score += 10
    else:
        score_details.append({"item": "目录结构检查", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 investigation 目录"})

    # 2. 检查 trespassers.txt (40分)
    if os.path.exists(trespassers_file):
        with open(trespassers_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            # 确定性解析检查
            has_darius = "Darius Vance" in content
            has_chloe = "Chloe Baxter" in content
            # 不应包含在白名单内的人
            no_marcus = "Marcus Johnson" not in content
            
            if has_darius and has_chloe:
                sub_score = 30
                if no_marcus:
                    sub_score += 10
                score_details.append({"item": "非白名单人员排查 (trespassers.txt)", "score": sub_score, "max_score": 40, "passed": sub_score == 40, "reason": "成功识别所有非法闯入者且未误报"})
                total_score += sub_score
            else:
                score_details.append({"item": "非白名单人员排查 (trespassers.txt)", "score": 0, "max_score": 40, "passed": False, "reason": f"未正确识别所有非法闯入者。当前内容包含：{content[:50]}"})
    else:
        score_details.append({"item": "非白名单人员排查 (trespassers.txt)", "score": 0, "max_score": 40, "passed": False, "reason": "文件未生成"})

    # 3. 检查 missing_vinyls.json (40分)
    if os.path.exists(missing_json_file):
        try:
            with open(missing_json_file, 'r', encoding='utf-8') as f:
                missing_data = json.load(f)
            
            # 结构化验证
            expected_ids = {"V-002", "V-004"}
            actual_ids = {item.get("record_id") for item in missing_data if isinstance(item, dict)}
            
            if actual_ids == expected_ids:
                # 检查是否包含多余字段或错误过滤
                if len(missing_data) == 2:
                    score_details.append({"item": "未归还唱片统计 (missing_vinyls.json)", "score": 40, "max_score": 40, "passed": True, "reason": "准确过滤出所有未归还唱片"})
                    total_score += 40
                else:
                    score_details.append({"item": "未归还唱片统计 (missing_vinyls.json)", "score": 20, "max_score": 40, "passed": False, "reason": "ID正确但包含冗余数据"})
                    total_score += 20
            else:
                score_details.append({"item": "未归还唱片统计 (missing_vinyls.json)", "score": 0, "max_score": 40, "passed": False, "reason": f"数据匹配失败，预期 {expected_ids}，实际 {actual_ids}"})
        except Exception as e:
            score_details.append({"item": "未归还唱片统计 (missing_vinyls.json)", "score": 0, "max_score": 40, "passed": False, "reason": f"JSON解析失败: {str(e)}"})
    else:
        score_details.append({"item": "未归还唱片统计 (missing_vinyls.json)", "score": 0, "max_score": 40, "passed": False, "reason": "文件未生成"})

    # 4. LLM 语义与格式验证 (10分)
    # 检查 trespassers.txt 是否纯净，没有多余的废话或解释
    if os.path.exists(trespassers_file):
        with open(trespassers_file, 'r', encoding='utf-8') as f:
            t_content = f.read()
        is_clean = llm_judge_content("Does the following text ONLY contain a list of names without conversational filler, explanations, or introductory sentences?", t_content)
        if is_clean:
            score_details.append({"item": "报告格式纯净度", "score": 10, "max_score": 10, "passed": True, "reason": "报告内容简洁，符合调查要求"})
            total_score += 10
        else:
            score_details.append({"item": "报告格式纯净度", "score": 0, "max_score": 10, "passed": False, "reason": "报告包含非必要描述性文字"})
    else:
        score_details.append({"item": "报告格式纯净度", "score": 0, "max_score": 10, "passed": False, "reason": "由于文件缺失无法进行格式评估"})

    # 输出最终分数
    output = {
        "total_score": total_score,
        "details": score_details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
