import os
import sys
import json
import httpx
from openai import OpenAI

# 配置常量
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 初始化 LLM 客户端
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
    results_dir = os.path.join(workspace, "results")
    bracket_path = os.path.join(results_dir, "official_bracket.json")
    trashed_path = os.path.join(results_dir, "trashed_teams.txt")
    
    score = 0
    details = []

    # 1. 基础目录与文件存在性检查 (10分)
    if os.path.exists(results_dir):
        score += 5
        details.append({"item": "Results directory exists", "score": 5, "max_score": 5, "passed": True})
    else:
        details.append({"item": "Results directory exists", "score": 0, "max_score": 5, "passed": False})

    if os.path.exists(bracket_path) and os.path.exists(trashed_path):
        score += 5
        details.append({"item": "Result files exist", "score": 5, "max_score": 5, "passed": True})
    else:
        details.append({"item": "Result files exist", "score": 0, "max_score": 5, "passed": False})

    # 2. 核心逻辑：验证 official_bracket.json (50分)
    # 正确的队伍应该是：Sweat_Lords, Aim_Assist
    try:
        with open(bracket_path, 'r') as f:
            bracket_data = json.load(f)
        
        valid_teams = [t.get("Team") for t in bracket_data if "Team" in t]
        
        # 检查是否包含且仅包含正确的队伍
        correct_teams = {"Sweat_Lords", "Aim_Assist"}
        if set(valid_teams) == correct_teams:
            score += 30
            details.append({"item": "Official bracket contains correct teams", "score": 30, "max_score": 30, "passed": True})
        else:
            details.append({"item": "Official bracket contains correct teams", "score": 0, "max_score": 30, "passed": False, "reason": f"Expected {correct_teams}, got {valid_teams}"})

        # 检查队伍人数规则 (Tri-Cup: 3人)
        size_check = all(len(t.get("Players", [])) == 3 for t in bracket_data)
        if size_check and len(bracket_data) > 0:
            score += 20
            details.append({"item": "Tri-Cup size rule (3 players) enforcement", "score": 20, "max_score": 20, "passed": True})
        else:
            details.append({"item": "Tri-Cup size rule enforcement", "score": 0, "max_score": 20, "passed": False})
            
    except Exception as e:
        details.append({"item": "Parse official_bracket.json", "score": 0, "max_score": 50, "passed": False, "reason": str(e)})

    # 3. 核心逻辑：验证 trashed_teams.txt (20分)
    # 应该被剔除的队伍：Duo_Queue (Size), Squad_Fam (Size), Boomers (Age 19), Squeakers (Age 13)
    try:
        with open(trashed_path, 'r') as f:
            trashed_content = f.read().strip()
        
        required_trashed = ["Duo_Queue", "Squad_Fam", "Boomers", "Squeakers"]
        missing_trashed = [team for team in required_trashed if team not in trashed_content]
        
        if not missing_trashed:
            score += 20
            details.append({"item": "Trashed teams list accuracy", "score": 20, "max_score": 20, "passed": True})
        else:
            details.append({"item": "Trashed teams list accuracy", "score": 0, "max_score": 20, "passed": False, "reason": f"Missing: {missing_trashed}"})
    except Exception as e:
        details.append({"item": "Read trashed_teams.txt", "score": 0, "max_score": 20, "passed": False, "reason": str(e)})

    # 4. LLM 语义验证：检查输出格式严谨性 (20分)
    # 验证 trashed_teams 是否仅仅是名称列表，没有多余的废话
    if os.path.exists(trashed_path):
        with open(trashed_path, 'r') as f:
            content = f.read()
        is_clean = llm_judge_content("Is this file a simple list of team names without any conversational filler or extra JSON structures?", content)
        if is_clean:
            score += 20
            details.append({"item": "Cleanliness of trashed_teams.txt", "score": 20, "max_score": 20, "passed": True})
        else:
            details.append({"item": "Cleanliness of trashed_teams.txt", "score": 0, "max_score": 20, "passed": False, "reason": "LLM judged the file content as messy or containing filler."})

    # 输出结果
    output = {
        "total_score": score,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(output, f, indent=2)

if __name__ == "__main__":
    verify()
