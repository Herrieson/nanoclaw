import os
import sys
import json
import csv
import re
from datetime import datetime
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

def build_ground_truth(workspace):
    """独立于Agent，使用评测机的纯净逻辑重建真值"""
    target_date = datetime(2024, 5, 18)
    
    # 1. 提取 Banlist
    banlist = set()
    banlist_path = os.path.join(workspace, "server_backups/2024_season_live/anticheat/banlist.txt")
    if os.path.exists(banlist_path):
        with open(banlist_path, "r", encoding="utf-8") as f:
            for line in f:
                match = re.search(r'BannedID:\s*(P_BANNED_\d+)', line)
                if match:
                    banlist.add(match.group(1))

    # 2. 提取 2024 Teams
    teams = {}
    teams_dir = os.path.join(workspace, "server_backups/2024_season_live/teams")
    if os.path.exists(teams_dir):
        for file in os.listdir(teams_dir):
            if file.endswith(".json"):
                with open(os.path.join(teams_dir, file), "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                        for t in data:
                            teams[t['team_id']] = t['team_name']
                    except:
                        pass

    # 3. 提取 2024 Players
    players = {}
    players_dir = os.path.join(workspace, "server_backups/2024_season_live/players")
    if os.path.exists(players_dir):
        for root, _, files in os.walk(players_dir):
            for file in files:
                if file.endswith(".csv"):
                    with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                        reader = csv.reader(f)
                        next(reader, None) # skip header
                        for row in reader:
                            if len(row) == 4 and row[0] not in ("N/A", "player_id"):
                                pid, pname, tid, bdate = row
                                if tid not in players:
                                    players[tid] = []
                                players[tid].append((pid, pname, bdate))

    # 4. 判定队伍有效性
    gt_valid = {}
    gt_invalid = set()

    for tid, tname in teams.items():
        if tid not in players or len(players[tid]) != 3:
            gt_invalid.add(tname)
            continue
        
        is_valid = True
        p_names = []
        for pid, pname, bdate in players[tid]:
            p_names.append(pname)
            if pid in banlist:
                is_valid = False
                break
            
            try:
                bday = datetime.strptime(bdate, "%Y-%m-%d")
                age = target_date.year - bday.year - ((target_date.month, target_date.day) < (bday.month, bday.day))
                if not (14 <= age <= 18):
                    is_valid = False
                    break
            except:
                is_valid = False
                break
        
        if is_valid:
            gt_valid[tname] = sorted(p_names)
        else:
            gt_invalid.add(tname)

    return gt_valid, gt_invalid

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results = []
    total_score = 0
    
    # 1. 检查目录与文件存在性 (10分)
    bracket_path = os.path.join(workspace, "results", "official_bracket.json")
    trashed_path = os.path.join(workspace, "results", "trashed_teams.txt")
    
    files_exist = os.path.exists(bracket_path) and os.path.exists(trashed_path)
    if files_exist:
        results.append({"item": "检查产物文件是否完整", "score": 10, "max_score": 10, "passed": True, "reason": "results 目录及要求的两个文件均存在"})
        total_score += 10
    else:
        results.append({"item": "检查产物文件是否完整", "score": 0, "max_score": 10, "passed": False, "reason": "缺失 results 目录或产物文件"})
        # 严重错误提前退出
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": 0, "details": results}, f, indent=2)
        return

    # 获取基准 Truth
    gt_valid, gt_invalid = build_ground_truth(workspace)
    agent_valid = {}
    agent_invalid = set()

    # 2. 检查 JSON 格式与合法性 (10分)
    try:
        with open(bracket_path, "r", encoding="utf-8") as f:
            agent_valid = json.load(f)
        
        is_schema_valid = isinstance(agent_valid, dict) and all(isinstance(v, list) and len(v) == 3 for v in agent_valid.values())
        if is_schema_valid:
            results.append({"item": "校验 JSON Schema 与战队格式", "score": 10, "max_score": 10, "passed": True, "reason": "JSON格式完全符合 Dict[str, List[str]] 且人数均为3"})
            total_score += 10
        else:
            results.append({"item": "校验 JSON Schema 与战队格式", "score": 0, "max_score": 10, "passed": False, "reason": "JSON 数据结构错误或包含非3人的异常队伍"})
    except Exception as e:
        results.append({"item": "校验 JSON Schema 与战队格式", "score": 0, "max_score": 10, "passed": False, "reason": f"解析 JSON 失败: {e}"})

    # 3. 核心计算结果验证 (30分 - Valid Teams)
    if agent_valid:
        # 要求绝对精确，错加或漏加都扣分
        agent_teams = set(agent_valid.keys())
        gt_teams = set(gt_valid.keys())
        
        if agent_teams == gt_teams:
            # 队伍名完全正确，检查队伍内玩家名
            players_match = True
            for team in gt_teams:
                if sorted(agent_valid[team]) != gt_valid[team]:
                    players_match = False
                    break
            
            if players_match:
                results.append({"item": "校验晋级名单(official_bracket)", "score": 30, "max_score": 30, "passed": True, "reason": "合法队伍及成员识别完全精准，没有任何错漏"})
                total_score += 30
            else:
                results.append({"item": "校验晋级名单(official_bracket)", "score": 15, "max_score": 30, "passed": False, "reason": "队伍匹配成功，但队伍内选手提取存在错误或幻觉"})
                total_score += 15
        else:
            diff_missing = len(gt_teams - agent_teams)
            diff_extra = len(agent_teams - gt_teams)
            results.append({"item": "校验晋级名单(official_bracket)", "score": 0, "max_score": 30, "passed": False, "reason": f"过滤逻辑错误，漏掉 {diff_missing} 支队伍，错加 {diff_extra} 支队伍"})
    else:
        results.append({"item": "校验晋级名单(official_bracket)", "score": 0, "max_score": 30, "passed": False, "reason": "晋级名单为空"})

    # 4. 废弃队伍过滤准确度 (25分 - Trashed Teams)
    try:
        with open(trashed_path, "r", encoding="utf-8") as f:
            for line in f:
                t_name = line.strip()
                if t_name:
                    agent_invalid.add(t_name)
        
        if agent_invalid == gt_invalid:
            results.append({"item": "校验违规名单(trashed_teams)", "score": 25, "max_score": 25, "passed": True, "reason": "所有由于人数、年龄、封禁违规的队伍已被精准提取至黑名单"})
            total_score += 25
        else:
            missing = len(gt_invalid - agent_invalid)
            extra = len(agent_invalid - gt_invalid)
            results.append({"item": "校验违规名单(trashed_teams)", "score": 0, "max_score": 25, "passed": False, "reason": f"黑名单校验失败：漏报 {missing} 项，误杀 {extra} 项"})
    except:
        results.append({"item": "校验违规名单(trashed_teams)", "score": 0, "max_score": 25, "passed": False, "reason": "读取 trashed_teams 异常"})

    # 5. 年龄临界点逻辑验证 (15分 - 强制验证周岁计算机制)
    edge_cases_passed = True
    reasons = []
    
    if "Edge_Valid_14" not in agent_valid: edge_cases_passed, reasons = False, reasons + ["误杀恰好满14岁的选手"]
    if "Edge_Valid_18" not in agent_valid: edge_cases_passed, reasons = False, reasons + ["误杀接近但尚未满19岁的选手"]
    if "Edge_Invalid_13" not in agent_invalid: edge_cases_passed, reasons = False, reasons + ["漏判差一天满14岁的选手"]
    if "Edge_Invalid_19" not in agent_invalid: edge_cases_passed, reasons = False, reasons + ["漏判刚好19岁超龄的选手"]

    if edge_cases_passed:
        results.append({"item": "校验周岁计算的边界用例", "score": 15, "max_score": 15, "passed": True, "reason": "闰年和临界日期的周岁计算逻辑完美无瑕"})
        total_score += 15
    else:
        results.append({"item": "校验周岁计算的边界用例", "score": 0, "max_score": 15, "passed": False, "reason": f"边界情况处理失败: {', '.join(reasons)}"})

    # 6. LLM 检查废弃名单文件的纯粹度 (10分 - 防止自然语言废话干扰自动化流程)
    try:
        with open(trashed_path, "r", encoding="utf-8") as f:
            sample_content = f.read(500)
        
        prompt = "Does the following text consist STRICTLY of a clean, unformatted list of team names (e.g., alphanumeric strings with underscores, exactly one per line)? It MUST NOT contain any markdown formatting, headers, conversational text (like 'Here is the list:', 'Trashed teams:'), bullet points, or numbering. Answer YES if it is a pure data list, NO otherwise."
        is_clean = llm_judge_content(prompt, sample_content)
        
        if is_clean:
            results.append({"item": "利用LLM检查黑名单的文本洁净度", "score": 10, "max_score": 10, "passed": True, "reason": "废弃文件不包含任何冗余闲聊或格式符，完全符合自动化管道要求"})
            total_score += 10
        else:
            results.append({"item": "利用LLM检查黑名单的文本洁净度", "score": 0, "max_score": 10, "passed": False, "reason": "LLM检测到包含解释性废话、Markdown语法或格式不合规"})
    except:
        results.append({"item": "利用LLM检查黑名单的文本洁净度", "score": 0, "max_score": 10, "passed": False, "reason": "文件读取或LLM请求异常"})

    # 汇总写入
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": results}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
