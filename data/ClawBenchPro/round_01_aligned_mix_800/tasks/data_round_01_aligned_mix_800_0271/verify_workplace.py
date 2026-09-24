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
    target_dir = os.path.join(workspace, "final_audit")
    
    score_details = []
    total_score = 0
    
    # 1. 检查最终结果目录是否存在 (10分)
    if os.path.isdir(target_dir):
        score_details.append({"item": "目录存在性检查", "score": 10, "max_score": 10, "passed": True, "reason": "成功创建 final_audit 目录"})
        total_score += 10
    else:
        score_details.append({"item": "目录存在性检查", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 final_audit 目录"})
        
    # 读取目录中所有文件的内容
    all_content = ""
    file_count = 0
    if os.path.isdir(target_dir):
        for root, _, files in os.walk(target_dir):
            for file in files:
                file_count += 1
                try:
                    with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                        all_content += f"\n--- File: {file} ---\n"
                        all_content += f.read()
                except Exception as e:
                    all_content += f"\n[Could not read file {file}: {e}]\n"

    # 2. 检查输出文件数量 (10分)
    # 题目要求留下 "two things" in a folder, 最好是两个文件，但只要有产出即可给部分分
    if file_count > 0:
        score_details.append({"item": "输出文件数量检查", "score": 10, "max_score": 10, "passed": True, "reason": f"在 final_audit 中找到了 {file_count} 个文件"})
        total_score += 10
    else:
        score_details.append({"item": "输出文件数量检查", "score": 0, "max_score": 10, "passed": False, "reason": "final_audit 目录为空"})

    # 3. 利用 LLM 检查 Interlopers 是否准确无误 (30分)
    if all_content.strip():
        interloper_prompt = (
            "Review the document. The user asked for a clear list of names who submitted a form but aren't on the official roster (interlopers). "
            "Evaluate if the text correctly and exclusively identifies exactly two interlopers: 'Zoe Saldana' and 'Jack Sparrow'. "
            "If it lists any other names as interlopers, or misses one of these two, you must answer NO. Answer ONLY with YES or NO."
        )
        if llm_judge_content(interloper_prompt, all_content):
            score_details.append({"item": "非名单人员名单(Interlopers)准确性", "score": 30, "max_score": 30, "passed": True, "reason": "准确识别了 Zoe Saldana 和 Jack Sparrow 且未发生幻觉"})
            total_score += 30
        else:
            score_details.append({"item": "非名单人员名单(Interlopers)准确性", "score": 0, "max_score": 30, "passed": False, "reason": "识别缺失或包含错误人员（幻觉）"})

        # 4. 利用 LLM 检查有效确认学生总数 (20分)
        # 有效要求: 名单上有 且 状态为 Paid (Alice, Bob, Daisy, Fiona) => 4人 (Charlie是Pending需要剔除)
        count_prompt = (
            "Review the summary report. Did it explicitly state that the total number of 'valid students confirmed' (or similar phrasing) is exactly 4? "
            "They should only count students who were on the roster and actually paid. Answer ONLY with YES or NO."
        )
        if llm_judge_content(count_prompt, all_content):
            score_details.append({"item": "有效学生人数准确性", "score": 20, "max_score": 20, "passed": True, "reason": "准确排除了 Pending 状态的学生，人数计算为 4"})
            total_score += 20
        else:
            score_details.append({"item": "有效学生人数准确性", "score": 0, "max_score": 20, "passed": False, "reason": "有效学生人数计算错误（未排除Pending或未正确合并数据）"})

        # 5. 利用 LLM 检查紧急基金总金额是否正确 (30分)
        # 计算逻辑: Premium费率10%, Standard 0%。Alice(0), Bob(60), Daisy(60), Fiona(70) => 190
        fund_prompt = (
            "Review the summary report. Did it explicitly state that the exact total amount of the 'Emergency Fund' collected from valid students is 190? "
            "Look for the number 190 directly associated with the Emergency Fund total. Answer ONLY with YES or NO."
        )
        if llm_judge_content(fund_prompt, all_content):
            score_details.append({"item": "紧急基金总金额计算", "score": 30, "max_score": 30, "passed": True, "reason": "精确计算出 Emergency Fund 总额为 190"})
            total_score += 30
        else:
            score_details.append({"item": "紧急基金总金额计算", "score": 0, "max_score": 30, "passed": False, "reason": "金额计算错误，未能正确应用费率或提取基础金额"})
    else:
        score_details.append({"item": "非名单人员名单准确性", "score": 0, "max_score": 30, "passed": False, "reason": "没有内容可以评估"})
        score_details.append({"item": "有效学生人数准确性", "score": 0, "max_score": 20, "passed": False, "reason": "没有内容可以评估"})
        score_details.append({"item": "紧急基金总金额计算", "score": 0, "max_score": 30, "passed": False, "reason": "没有内容可以评估"})

    # 输出验证结果
    result = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
