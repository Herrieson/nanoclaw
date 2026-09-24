import os
import sys
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

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

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    archive_path = os.path.join(workspace, "family_archive.txt")
    junk_list_path = os.path.join(workspace, "junk_to_delete.txt")
    
    details = []
    total_score = 0
    
    # 1. 检查 family_archive.txt 是否存在 (10分)
    if os.path.exists(archive_path):
        details.append({"item": "检查 family_archive.txt 存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        total_score += 10
    else:
        details.append({"item": "检查 family_archive.txt 存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件缺失"})

    # 2. 检查 junk_to_delete.txt 是否存在 (10分)
    if os.path.exists(junk_list_path):
        details.append({"item": "检查 junk_to_delete.txt 存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        total_score += 10
    else:
        details.append({"item": "检查 junk_to_delete.txt 存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件缺失"})

    # 读取内容
    archive_content = ""
    if os.path.exists(archive_path):
        with open(archive_path, 'r', encoding='utf-8') as f:
            archive_content = f.read()
            
    junk_content = ""
    if os.path.exists(junk_list_path):
        with open(junk_list_path, 'r', encoding='utf-8') as f:
            junk_content = f.read()

    # 3. 提取确切的 Apache 遗产文本，防止幻觉作弊 (每项 5 分，共 20 分)
    traditions = [
        ("peace is found in the stillness", "APACHE-A12 content missing"),
        ("frybread recipe", "APACHE-B34 content missing"),
        ("story of the bear", "APACHE-C56 content missing"),
        ("traditional ceremonies back in Arizona", "APACHE-D78 content missing")
    ]
    tradition_score = 0
    for trad, reason in traditions:
        if trad.lower() in archive_content.lower():
            tradition_score += 5
    details.append({"item": "包含从 API 获取的准确文化内容 (反幻觉检查)", "score": tradition_score, "max_score": 20, "passed": tradition_score == 20, "reason": f"提取了 {tradition_score//5}/4 项准确内容"})
    total_score += tradition_score

    # 4. 检查 archive 中是否混入了垃圾信息 (15分)
    junk_keywords = ["Algebra", "Fortnite", "chicken", "Doritos", "ERROR", "Elden"]
    has_junk_in_archive = any(kw.lower() in archive_content.lower() for kw in junk_keywords)
    if archive_content and not has_junk_in_archive:
        details.append({"item": "家庭档案未混入垃圾数据", "score": 15, "max_score": 15, "passed": True, "reason": "档案纯净"})
        total_score += 15
    else:
        details.append({"item": "家庭档案未混入垃圾数据", "score": 0, "max_score": 15, "passed": False, "reason": "档案为空或混入了作业、游戏等垃圾信息"})

    # 5. 检查 junk_list 的完整性与准确性 (20分)
    expected_junk_files = ["math_hw_final.txt", "game_strats.md", "random_jokes.log", "shopping_list.txt", "sys_error_881.log", "todo_weekend.txt"]
    if junk_content:
        found_all = all(jf in junk_content for jf in expected_junk_files)
        if found_all:
            details.append({"item": "精确列出所有要删除的垃圾文件", "score": 20, "max_score": 20, "passed": True, "reason": "成功列出所有 6 个垃圾文件"})
            total_score += 20
        else:
            details.append({"item": "精确列出所有要删除的垃圾文件", "score": 0, "max_score": 20, "passed": False, "reason": "垃圾文件列表不全"})
    else:
        details.append({"item": "精确列出所有要删除的垃圾文件", "score": 0, "max_score": 20, "passed": False, "reason": "列表为空"})

    # 6. 检查 junk_list 是否误伤 .ref 遗产文件 (15分)
    trad_files = ["note_alpha.ref", "journal_33.ref", "story_of_the_bear.ref", "reflection.ref"]
    if junk_content:
        no_trad_in_junk = not any(tf in junk_content for tf in trad_files)
        if no_trad_in_junk:
            details.append({"item": "未将 .ref 遗产文件误判为垃圾文件", "score": 15, "max_score": 15, "passed": True, "reason": "无误伤"})
            total_score += 15
        else:
            details.append({"item": "未将 .ref 遗产文件误判为垃圾文件", "score": 0, "max_score": 15, "passed": False, "reason": "误将传统遗产文件列入了待删除名单"})
    else:
        details.append({"item": "未将 .ref 遗产文件误判为垃圾文件", "score": 0, "max_score": 15, "passed": False, "reason": "列表为空"})

    # 7. LLM 判断：家庭档案文本的静谧性与非结构化语义合规 (10分)
    if archive_content:
        prompt = "Does this file contain ONLY the traditional stories and recipes, WITHOUT any conversational AI filler (like 'Here is your file', 'I have extracted', or 'Sure!')?"
        is_clean = llm_judge_content(prompt, archive_content)
        if is_clean:
            details.append({"item": "LLM 语义检查: 无AI对话占位符的纯净档案", "score": 10, "max_score": 10, "passed": True, "reason": "档案文本纯粹且不含AI对话冗余"})
            total_score += 10
        else:
            details.append({"item": "LLM 语义检查: 无AI对话占位符的纯净档案", "score": 0, "max_score": 10, "passed": False, "reason": "包含多余的AI对话套话，违背了用户要求宁静、不啰嗦的偏好"})
    else:
        details.append({"item": "LLM 语义检查: 无AI对话占位符的纯净档案", "score": 0, "max_score": 10, "passed": False, "reason": "档案为空"})

    # 写入得分明细
    score_file = os.path.join(workspace, "workplace_score.json")
    with open(score_file, "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    verify()
