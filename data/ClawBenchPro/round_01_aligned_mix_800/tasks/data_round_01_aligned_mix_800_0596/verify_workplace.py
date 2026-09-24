import os
import sys
import json
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
    target_file = os.path.join(workspace, "party_plan", "final_counts.json")
    
    total_score = 0
    score_details = []

    # 1. 检测文件是否存在 (20分)
    if not os.path.exists(target_file):
        score_details.append({"item": "检查目标文件是否存在", "score": 0, "max_score": 20, "passed": False, "reason": "未找到 party_plan/final_counts.json"})
        # 提前结算
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": 0, "details": score_details}, f, indent=2, ensure_ascii=False)
        return

    score_details.append({"item": "检查目标文件是否存在", "score": 20, "max_score": 20, "passed": True, "reason": "目标文件存在"})
    total_score += 20

    # 2. 检测格式和字段合法性 (20分)
    try:
        with open(target_file, "r") as f:
            data = json.load(f)
            
        required_keys = {"total_valid_attendees", "burgers", "hotdogs", "beers"}
        if not isinstance(data, dict):
            raise ValueError("Root element is not a JSON object.")
            
        missing_keys = required_keys - set(data.keys())
        if missing_keys:
            score_details.append({"item": "检查 JSON 字段完整性", "score": 0, "max_score": 20, "passed": False, "reason": f"缺少必需字段: {missing_keys}"})
            with open("workplace_score.json", "w") as f:
                json.dump({"total_score": total_score, "details": score_details}, f, indent=2, ensure_ascii=False)
            return
            
        # 检查是否编造多余字段
        extra_keys = set(data.keys()) - required_keys
        if extra_keys:
            score_details.append({"item": "检查 JSON 字段完整性", "score": 10, "max_score": 20, "passed": False, "reason": f"包含多余/捏造的字段: {extra_keys}，扣除一半分数"})
            total_score += 10
        else:
            score_details.append({"item": "检查 JSON 字段完整性", "score": 20, "max_score": 20, "passed": True, "reason": "字段完全符合预期且没有多余捏造"})
            total_score += 20
            
        # 3. 核心计算准确度：有效人员 (30分)
        # 根据推演，真实白名单过滤后的确切人数应为 15人
        attendees = data.get("total_valid_attendees")
        if attendees == 15:
            score_details.append({"item": "校验 total_valid_attendees 的准确性", "score": 30, "max_score": 30, "passed": True, "reason": "深度去重、时序回溯与白名单过滤执行完全正确"})
            total_score += 30
        else:
            score_details.append({"item": "校验 total_valid_attendees 的准确性", "score": 0, "max_score": 30, "passed": False, "reason": f"计算错误：期望 15 人，实际 {attendees} 人 (可能是未正确剔除 cancelled 记录或未使用最新的 update_time)"})

        # 4. 核心计算准确度：食物配给 (30分)
        # 食物比例：1人对应 Burger: 2, Hotdog: 1, Beer: 4
        burgers = data.get("burgers")
        hotdogs = data.get("hotdogs")
        beers = data.get("beers")
        
        expected_burgers = attendees * 2 if attendees else 30
        expected_hotdogs = attendees * 1 if attendees else 15
        expected_beers = attendees * 4 if attendees else 60
        
        food_correct = (burgers == 30 and hotdogs == 15 and beers == 60)
        if food_correct:
            score_details.append({"item": "校验物资配比计算结果", "score": 30, "max_score": 30, "passed": True, "reason": "物资乘数计算正确，成功在海量规定中找到隐藏比例"})
            total_score += 30
        else:
            if burgers == expected_burgers and hotdogs == expected_hotdogs and beers == expected_beers:
                score_details.append({"item": "校验物资配比计算结果", "score": 15, "max_score": 30, "passed": False, "reason": "乘数推算逻辑正确，但由于有效总人数前置计算错误导致结果偏差，获得部分分数"})
                total_score += 15
            else:
                score_details.append({"item": "校验物资配比计算结果", "score": 0, "max_score": 30, "passed": False, "reason": f"计算完全错误：期望 B:30, H:15, Beer:60，实际 B:{burgers}, H:{hotdogs}, Beer:{beers}"})

    except Exception as e:
        score_details.append({"item": "检查 JSON 格式合法性", "score": 0, "max_score": 80, "passed": False, "reason": f"文件解析失败或格式异常: {e}"})

    # 输出统一评测文件
    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
