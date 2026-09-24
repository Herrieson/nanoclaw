import os
import sys
import json
import httpx
from openai import OpenAI
import re

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
    """
    统一的非结构化文本语义检测接口。
    用于判断 Agent 生成的文本文件中是否包含用户明令禁止的"多余寒暄/解释"。
    """
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
    results_dir = os.path.join(workspace, "results")
    playlist_file = os.path.join(results_dir, "workout_playlist.txt")
    costs_file = os.path.join(results_dir, "windshield_costs.txt")

    total_score = 0
    details = []

    # 1. 验证目标目录是否存在 (10分)
    if os.path.isdir(results_dir):
        total_score += 10
        details.append({"item": "检查 results 目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "results 目录已成功创建"})
    else:
        details.append({"item": "检查 results 目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到要求的 results 目录"})
        # 核心目录不存在则直接结束
        with open("workplace_score.json", "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2, ensure_ascii=False)
        return

    # 2. 验证 workout_playlist.txt (总计 50分)
    if os.path.isfile(playlist_file):
        total_score += 10
        details.append({"item": "检查 workout_playlist.txt 文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件已创建"})
        
        with open(playlist_file, "r", encoding="utf-8") as f:
            playlist_content = f.read()
        content_lower = playlist_content.lower()

        # 检查是否包含 4 首正确的曲目 (20分)
        correct_tracks = ["iron will", "adrenaline rush", "heavy lifts", "max reps"]
        found_correct = [track for track in correct_tracks if track in content_lower]
        score_correct = len(found_correct) * 5
        total_score += score_correct
        details.append({
            "item": "验证播放列表内的曲目完整性",
            "score": score_correct, "max_score": 20, "passed": score_correct == 20,
            "reason": f"找到了 {len(found_correct)} 个符合 BPM > 120 的正确曲目: {found_correct}"
        })

        # 检查是否排除了噪音曲目 (10分)
        wrong_tracks = ["soft lullaby", "windshield wipers in the rain", "sunday morning"]
        found_wrong = [track for track in wrong_tracks if track in content_lower]
        if not found_wrong:
            total_score += 10
            details.append({"item": "验证是否成功剔除了无效曲目", "score": 10, "max_score": 10, "passed": True, "reason": "完美过滤了所有低BPM噪音及干扰项"})
        else:
            details.append({"item": "验证是否成功剔除了无效曲目", "score": 0, "max_score": 10, "passed": False, "reason": f"未严格按照 BPM>120 过滤，错误包含: {found_wrong}"})

        # 结合 LLM 判断用户要求的 Persona 和行文语气 (10分)
        llm_prompt = "The user explicitly requested 'Don't give me a whole presentation. Just get the files made'. Evaluate if the file content strictly contains ONLY the track names without ANY conversational filler, greetings, bullet points intro (like 'Here is the playlist:') or extra explanations. Answer 'YES' if it is strictly raw data with NO fluff. Answer 'NO' if it contains conversational text or presentations."
        is_clean = llm_judge_content(llm_prompt, playlist_content)
        if is_clean:
            total_score += 10
            details.append({"item": "LLM语义检测：播放列表是否简洁无冗余交流", "score": 10, "max_score": 10, "passed": True, "reason": "文件内容纯粹是音乐曲目，不含废话，符合用户的急性子人设"})
        else:
            details.append({"item": "LLM语义检测：播放列表是否简洁无冗余交流", "score": 0, "max_score": 10, "passed": False, "reason": "大模型判定文件中包含了多余的汇报或解释，违反指令"})
    else:
        details.append({"item": "检查 workout_playlist.txt 文件", "score": 0, "max_score": 50, "passed": False, "reason": "未生成 workout_playlist.txt 文件"})

    # 3. 验证 windshield_costs.txt (总计 40分)
    if os.path.isfile(costs_file):
        total_score += 10
        details.append({"item": "检查 windshield_costs.txt 文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件已创建"})

        with open(costs_file, "r", encoding="utf-8") as f:
            costs_content = f.read()
        
        # 严谨的正则寻找文件中的所有浮点数
        numbers = re.findall(r'\d+(?:\.\d+)?', costs_content)
        has_correct_sum = any(abs(float(n) - 625.75) < 0.01 for n in numbers)
        has_wrong_molding_sum = any(abs(float(n) - 647.75) < 0.01 for n in numbers) # 210.5 + 185.25 + 230 + 22(Molding) = 647.75
        has_all_sum = any(abs(float(n) - 906.25) < 0.01 for n in numbers)

        if has_correct_sum and not has_wrong_molding_sum and not has_all_sum:
            total_score += 20
            details.append({"item": "验证挡风玻璃成本计算的精准度", "score": 20, "max_score": 20, "passed": True, "reason": "金额精准匹配为 625.75，成功排除了 Windshield Molding、Adhesive、Shop Towels 等陷阱项目"})
        elif has_wrong_molding_sum:
            total_score += 5
            details.append({"item": "验证挡风玻璃成本计算的精准度", "score": 5, "max_score": 20, "passed": False, "reason": "幻觉失误：将 'Windshield Molding' 也计算为了挡风玻璃成本 (算出647.75)。"})
        elif has_all_sum:
            total_score += 0
            details.append({"item": "验证挡风玻璃成本计算的精准度", "score": 0, "max_score": 20, "passed": False, "reason": "完全未做过滤，汇总了所有发票金额 (算出906.25)。"})
        else:
            details.append({"item": "验证挡风玻璃成本计算的精准度", "score": 0, "max_score": 20, "passed": False, "reason": f"未找到正确金额 625.75。文件中解析到的数字有：{numbers}"})
        
        # 结合 LLM 同样判断财务数据的输出格式
        llm_prompt2 = "The user explicitly requested 'Don't give me a whole presentation. Just get the files made'. Evaluate if the file content strictly contains ONLY the final sum (with or without a currency symbol) without ANY conversational filler, greetings, or extra text like 'The total cost for the windshields is'. Answer 'YES' if it is strictly just the number with NO fluff. Answer 'NO' if it contains conversational text."
        is_clean_2 = llm_judge_content(llm_prompt2, costs_content)
        if is_clean_2:
            total_score += 10
            details.append({"item": "LLM语义检测：发票结果是否简洁无冗余交流", "score": 10, "max_score": 10, "passed": True, "reason": "输出仅保留金额结果，符合用户迅速发短信给老板的要求"})
        else:
            details.append({"item": "LLM语义检测：发票结果是否简洁无冗余交流", "score": 0, "max_score": 10, "passed": False, "reason": "在金额文件内放置了多余的句型或废话"})
    else:
        details.append({"item": "检查 windshield_costs.txt 文件", "score": 0, "max_score": 40, "passed": False, "reason": "未生成 windshield_costs.txt 文件"})

    # 将所有评测结果落盘
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
