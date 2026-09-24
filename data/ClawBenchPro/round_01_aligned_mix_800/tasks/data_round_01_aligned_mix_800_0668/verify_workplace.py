import os
import sys
import json
import httpx
from openai import OpenAI

# 强制要求读取环境变量并关闭 SSL 验证
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
    """用于调用 LLM 进行非结构化/风格层面的严格审查"""
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

def extract_all_strings(data):
    """递归提取 JSON 中的所有键和值，用于模糊反序列化验证"""
    strings = []
    if isinstance(data, dict):
        for k, v in data.items():
            strings.append(str(k))
            strings.extend(extract_all_strings(v))
    elif isinstance(data, list):
        for item in data:
            strings.extend(extract_all_strings(item))
    else:
        strings.append(str(data))
    return strings

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results_dir = os.path.join(workspace, "results")
    json_path = os.path.join(results_dir, "official_bracket.json")
    txt_path = os.path.join(results_dir, "trashed_teams.txt")

    total_score = 0
    details = []

    # ================= 1. 目录级别验证 =================
    if os.path.isdir(results_dir):
        total_score += 10
        details.append({"item": "检查 results 目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "results 目录存在"})
    else:
        details.append({"item": "检查 results 目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "results 目录不存在"})

    # ================= 2. JSON 合法性与数据验证 =================
    json_valid = False
    json_data = None
    if os.path.isfile(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            json_valid = True
            total_score += 15
            details.append({"item": "检查 official_bracket.json 存在且为合法 JSON", "score": 15, "max_score": 15, "passed": True, "reason": "JSON 文件存在且能够被标准库正常解析"})
        except Exception as e:
            details.append({"item": "检查 official_bracket.json 存在且为合法 JSON", "score": 0, "max_score": 15, "passed": False, "reason": f"JSON 文件解析失败: {e}"})
    else:
        details.append({"item": "检查 official_bracket.json 存在且为合法 JSON", "score": 0, "max_score": 15, "passed": False, "reason": "JSON 文件不存在"})

    if json_valid and json_data is not None:
        all_strs = [s.lower() for s in extract_all_strings(json_data)]
        # 移除下划线和空格以容错不同格式 (如 "Sweat Lords" 或 "sweat_lords")
        normalized_strs = " ".join(all_strs).replace("_", "").replace(" ", "")
        
        # 验证合格队伍 (15分)
        if "sweatlords" in normalized_strs:
            total_score += 7
            details.append({"item": "JSON 包含合格队伍 Sweat_Lords", "score": 7, "max_score": 7, "passed": True, "reason": "JSON 数据中正确提取到了 Sweat_Lords"})
        else:
            details.append({"item": "JSON 包含合格队伍 Sweat_Lords", "score": 0, "max_score": 7, "passed": False, "reason": "JSON 中缺失 Sweat_Lords"})
            
        if "aimassist" in normalized_strs:
            total_score += 8
            details.append({"item": "JSON 包含合格队伍 Aim_Assist", "score": 8, "max_score": 8, "passed": True, "reason": "JSON 数据中正确提取到了 Aim_Assist"})
        else:
            details.append({"item": "JSON 包含合格队伍 Aim_Assist", "score": 0, "max_score": 8, "passed": False, "reason": "JSON 中缺失 Aim_Assist"})
            
        # 严查 JSON 中的非法队伍 (15分，幻觉一票否决项)
        invalid_teams = ["duoqueue", "squadfam", "boomers", "squeakers"]
        found_invalid = [t for t in invalid_teams if t in normalized_strs]
        if not found_invalid:
            total_score += 15
            details.append({"item": "JSON 纯净性检测（无不合格队伍）", "score": 15, "max_score": 15, "passed": True, "reason": "未在最终 JSON 中发现任何应被淘汰的队伍，数据纯净"})
        else:
            details.append({"item": "JSON 纯净性检测（无不合格队伍）", "score": 0, "max_score": 15, "passed": False, "reason": f"过滤逻辑错误，JSON中发现了淘汰队伍: {found_invalid}"})
    else:
        details.append({"item": "JSON 包含合格队伍 Sweat_Lords", "score": 0, "max_score": 7, "passed": False, "reason": "依赖项验证失败"})
        details.append({"item": "JSON 包含合格队伍 Aim_Assist", "score": 0, "max_score": 8, "passed": False, "reason": "依赖项验证失败"})
        details.append({"item": "JSON 纯净性检测（无不合格队伍）", "score": 0, "max_score": 15, "passed": False, "reason": "依赖项验证失败"})

    # ================= 3. TXT 垃圾箱验证与语义检测 =================
    if os.path.isfile(txt_path):
        total_score += 5
        details.append({"item": "检查 trashed_teams.txt 是否存在", "score": 5, "max_score": 5, "passed": True, "reason": "TXT 文件成功创建"})
        
        with open(txt_path, 'r', encoding='utf-8') as f:
            txt_content = f.read()
            
        # 极度压缩字符串以防 Agent 引入不规则换行或空格
        txt_normalized = txt_content.replace("_", "").replace(" ", "").replace("\n", "").lower()
            
        # 检查是否记录了所有被淘汰的队伍 (15分，每漏一个扣分)
        invalid_teams_check = ["duoqueue", "squadfam", "boomers", "squeakers"]
        missing = [t for t in invalid_teams_check if t not in txt_normalized]
        if not missing:
            total_score += 15
            details.append({"item": "TXT 包含所有被淘汰的队伍", "score": 15, "max_score": 15, "passed": True, "reason": "所有被淘汰的4支队伍均记录在案"})
        else:
            penalty = len(missing) * 4
            earned = max(0, 15 - penalty)
            total_score += earned
            details.append({"item": "TXT 包含所有被淘汰的队伍", "score": earned, "max_score": 15, "passed": False, "reason": f"数据不全，漏掉了: {missing}"})
            
        # 检查 TXT 是否误伤合格队伍 (10分)
        valid_teams_check = ["sweatlords", "aimassist"]
        wrong_found = [t for t in valid_teams_check if t in txt_normalized]
        if not wrong_found:
            total_score += 10
            details.append({"item": "TXT 未误伤合格队伍", "score": 10, "max_score": 10, "passed": True, "reason": "TXT 中未包含合格名单内的队伍"})
        else:
            details.append({"item": "TXT 未误伤合格队伍", "score": 0, "max_score": 10, "passed": False, "reason": f"严重误伤！发现合格队伍出现在垃圾箱: {wrong_found}"})
            
        # ================= 4. LLM 风格检测 (15分) =================
        llm_prompt = "Does the following text ONLY contain a list of team names (and possibly newlines, commas, or basic bullets), WITHOUT any conversational text, apologies, greetings, or extra explanations? Answer YES if it's strictly just data/team names, and NO if there is any conversational filler."
        is_pure = llm_judge_content(llm_prompt, txt_content)
        if is_pure:
            total_score += 15
            details.append({"item": "大模型非结构化文本风格检查", "score": 15, "max_score": 15, "passed": True, "reason": "判定该文件干练地仅包含队伍数据，没有废话和寒暄，符合 Persona"})
        else:
            details.append({"item": "大模型非结构化文本风格检查", "score": 0, "max_score": 15, "passed": False, "reason": "大模型判定该文件内含有废话、道歉信或多余上下文，违反了 'just throw the names' 的业务诉求"})

    else:
        details.append({"item": "检查 trashed_teams.txt 是否存在", "score": 0, "max_score": 5, "passed": False, "reason": "TXT 文件不存在"})
        details.append({"item": "TXT 包含所有被淘汰的队伍", "score": 0, "max_score": 15, "passed": False, "reason": "依赖项验证失败"})
        details.append({"item": "TXT 未误伤合格队伍", "score": 0, "max_score": 10, "passed": False, "reason": "依赖项验证失败"})
        details.append({"item": "大模型非结构化文本风格检查", "score": 0, "max_score": 15, "passed": False, "reason": "依赖项验证失败"})

    # 结果回写
    score_file = os.path.join(workspace, "workplace_score.json")
    with open(score_file, 'w', encoding='utf-8') as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
