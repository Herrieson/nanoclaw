import os
import sys
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# Initialize client, strictly disabling SSL verification
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    if not file_content.strip():
        return False
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
    results = []
    total_score = 0

    # 1. Check Directory Existence (10 points)
    target_dir = os.path.join(workspace, "community_fair_prep")
    dir_exists = os.path.isdir(target_dir)
    if dir_exists:
        results.append({"item": "检查结果目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录 community_fair_prep 存在"})
        total_score += 10
    else:
        results.append({"item": "检查结果目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 community_fair_prep 目录"})

    # 2. Check File Generation (10 points)
    file_content = ""
    file_exists = False
    if dir_exists:
        files = os.listdir(target_dir)
        valid_files = [f for f in files if os.path.isfile(os.path.join(target_dir, f))]
        if valid_files:
            file_exists = True
            file_path = os.path.join(target_dir, valid_files[0])
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    file_content = f.read()
                results.append({"item": "检查摘要报告文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": f"成功读取文件 {valid_files[0]}"})
                total_score += 10
            except Exception as e:
                results.append({"item": "检查摘要报告文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": f"文件读取失败: {e}"})
        else:
            results.append({"item": "检查摘要报告文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "目录下没有任何文件"})
    else:
        results.append({"item": "检查摘要报告文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "目录不存在，无法检查文件"})

    # 3. LLM Check: Total Valid Volunteer Hours (30 points)
    hours_prompt = (
        "Does the file content explicitly state that the total valid volunteer hours is 12 (or 12.0)? "
        "It must ONLY include valid volunteers (Sarah, David, Jamal, Miriam) and MUST NOT include hours from crashers like Chad or Karen. "
        "The number 12 must be presented as the final aggregated total."
    )
    if file_exists and file_content:
        if llm_judge_content(hours_prompt, file_content):
            results.append({"item": "计算并验证有效志愿服务总时长", "score": 30, "max_score": 30, "passed": True, "reason": "大模型验证：正确排除了未注册人员并计算出总时长为12小时"})
            total_score += 30
        else:
            results.append({"item": "计算并验证有效志愿服务总时长", "score": 0, "max_score": 30, "passed": False, "reason": "大模型验证：总时长计算错误或包含了未注册人员（Chad, Karen）"})
    else:
        results.append({"item": "计算并验证有效志愿服务总时长", "score": 0, "max_score": 30, "passed": False, "reason": "无文件内容可供检查"})

    # 4. LLM Check: Acceptable Donations Filtering (30 points)
    donations_prompt = (
        "Does the file content list the acceptable donated items (Organic Apples, Meditation Cushions, Social Justice Pamphlets, Whole Wheat Bread) "
        "AND completely exclude junk/unhealthy items (Candy Bars, Soda Cans, Processed Cheese Slices)? "
        "If any junk items are mentioned as 'accepted' or if acceptable items are missing, answer 'NO'."
    )
    if file_exists and file_content:
        if llm_judge_content(donations_prompt, file_content):
            results.append({"item": "过滤并汇总有效捐赠物资", "score": 30, "max_score": 30, "passed": True, "reason": "大模型验证：成功筛选出健康/有用物资并剔除了垃圾食品"})
            total_score += 30
        else:
            results.append({"item": "过滤并汇总有效捐赠物资", "score": 0, "max_score": 30, "passed": False, "reason": "大模型验证：捐赠物资列表不完整或未成功剔除垃圾食品(糖果/汽水/加工奶酪)"})
    else:
        results.append({"item": "过滤并汇总有效捐赠物资", "score": 0, "max_score": 30, "passed": False, "reason": "无文件内容可供检查"})

    # 5. LLM Check: Formal Tone and Formatting (20 points)
    tone_prompt = (
        "Is the document formatted as a 'clean, formal summary report'? "
        "It should be professional, well-structured, and suitable for an official community fair prep document. "
        "It should not contain conversational AI filler like 'Here is the report you requested'."
    )
    if file_exists and file_content:
        if llm_judge_content(tone_prompt, file_content):
            results.append({"item": "正式且干净的报告格式", "score": 20, "max_score": 20, "passed": True, "reason": "大模型验证：报告语气正式、干净且没有多余废话"})
            total_score += 20
        else:
            results.append({"item": "正式且干净的报告格式", "score": 0, "max_score": 20, "passed": False, "reason": "大模型验证：格式混乱、非正式或包含了AI对话填充词"})
    else:
        results.append({"item": "正式且干净的报告格式", "score": 0, "max_score": 20, "passed": False, "reason": "无文件内容可供检查"})

    output_data = {
        "total_score": total_score,
        "details": results
    }

    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    verify()
