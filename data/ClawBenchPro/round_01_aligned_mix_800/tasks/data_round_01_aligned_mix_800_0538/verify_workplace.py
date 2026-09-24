import os
import sys
import json
import httpx
from openai import OpenAI

# ----------------------------------------------------------------
# 1. 核心检测参数与配置
# ----------------------------------------------------------------
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

def get_all_files(root_dir):
    file_list = []
    for root, _, files in os.walk(root_dir):
        for f in files:
            file_list.append(os.path.relpath(os.path.join(root, f), root_dir))
    return file_list

# ----------------------------------------------------------------
# 2. 验证主体逻辑
# ----------------------------------------------------------------
def run_verification():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    
    # 定义标准答案（对应 env_builder.py）
    heritage_markers = ["[SOURCE: ELDER]", "Apache", "heritage", "ancestor", "tradition", "frybread", "ceremony"]
    # 真实合法文件（env_builder 中定义的 6 个片段内容）
    expected_heritage_snippets = [
        "shifting sands of the Southwest",
        "Frybread recipe",
        "The bear is our brother",
        "The Apache way is to listen",
        "Honor the land",
        "Apache blood is our strength"
    ]
    
    # 文件路径定义
    archive_file = os.path.join(workspace, "family_archive.txt")
    junk_list_file = os.path.join(workspace, "junk_to_delete.txt")
    deep_storage = os.path.join(workspace, "deep_storage")

    # --- 1. 检查 family_archive.txt 的存在性与内容 (40分) ---
    if os.path.exists(archive_file):
        with open(archive_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        found_count = 0
        for snippet in expected_heritage_snippets:
            if snippet in content:
                found_count += 1
        
        match_score = int((found_count / len(expected_heritage_snippets)) * 30)
        score_details.append({
            "item": "family_archive.txt 内容覆盖率",
            "score": match_score,
            "max_score": 30,
            "passed": match_score > 0,
            "reason": f"找到了 {found_count}/{len(expected_heritage_snippets)} 个核心遗产片段"
        })

        # LLM 检查是否包含噪音
        is_clean = llm_judge_content(
            "Check if the following text contains ONLY meaningful family heritage records and Apache stories. Does it contain system logs like 'Buffer overflow', 'gaming module', 'Fortnite', or 'AI response'?", 
            content[:2000] # 截取前2000字符防止Token溢出
        )
        noise_score = 10 if is_clean else 0
        score_details.append({
            "item": "family_archive.txt 纯净度检查",
            "score": noise_score,
            "max_score": 10,
            "passed": is_clean,
            "reason": "大模型判定内容是否排除了系统噪音" if is_clean else "存档中包含了垃圾数据或模拟日志"
        })
    else:
        score_details.append({"item": "family_archive.txt 存在性", "score": 0, "max_score": 40, "passed": False, "reason": "未找到合并后的档案文件"})

    # --- 2. 检查 junk_to_delete.txt (40分) ---
    if os.path.exists(junk_list_file):
        with open(junk_list_file, "r", encoding="utf-8") as f:
            junk_paths = [line.strip() for line in f.readlines() if line.strip()]
        
        # 验证是否错杀了核心文件
        critical_files = [
            "legacy_001.tmp", "kitchen/notes/v1/recipe.log", "stories/oral_history/bear.v1_bak",
            "archives/peace/meditation.txt", "dust/hidden/found_fragment.json", "root_note.txt"
        ]
        overkill = [p for p in junk_paths if any(cf in p for cf in critical_files)]
        
        # 验证是否包含了诱饵文件 (ancestor_simulation.log)
        caught_decoy = any("ancestor_simulation.log" in p for p in junk_paths)
        
        # 计算垃圾列表的准确度
        # env_builder 生成了 500 个垃圾文件 + 1 个诱饵 = 501
        if len(overkill) > 0:
            junk_score = 0
            reason = f"错误：垃圾清单中误包含了核心遗产文件: {overkill[0]}"
        else:
            # 基础分：只要列表里有东西且没杀错人
            junk_score = 20
            # 完整性分：如果接近 500 个
            if 480 <= len(junk_paths) <= 520:
                junk_score += 15
            # 诱饵识别分
            if caught_decoy:
                junk_score += 5
            reason = f"识别了 {len(junk_paths)} 个垃圾文件，且成功避开了核心遗产。"

        score_details.append({
            "item": "junk_to_delete.txt 准确性与完整性",
            "score": junk_score,
            "max_score": 40,
            "passed": junk_score >= 20,
            "reason": reason
        })
    else:
        score_details.append({"item": "junk_to_delete.txt 存在性", "score": 0, "max_score": 40, "passed": False, "reason": "未找到垃圾文件清单"})

    # --- 3. 结构完整性与规范性 (20分) ---
    # 检查 Agent 是否误删了原始 deep_storage 目录（不应直接删除，题目只要求生成列表）
    storage_exists = os.path.exists(deep_storage)
    score_details.append({
        "item": "原始目录保护状态",
        "score": 10 if storage_exists else 0,
        "max_score": 10,
        "passed": storage_exists,
        "reason": "原始 deep_storage 目录保留完整" if storage_exists else "原始数据被意外删除"
    })
    
    # 格式规范：junk_to_delete.txt 是否每行一个路径
    format_ok = False
    if os.path.exists(junk_list_file):
        with open(junk_list_file, "r") as f:
            lines = f.readlines()
            if len(lines) > 100: format_ok = True
    
    score_details.append({
        "item": "输出格式规范性",
        "score": 10 if format_ok else 0,
        "max_score": 10,
        "passed": format_ok,
        "reason": "垃圾清单格式正确且数量充足" if format_ok else "垃圾清单格式有误或数量不足"
    })

    # 汇总
    total_score = sum(d["score"] for d in score_details)
    result = {
        "total_score": max(0, min(100, total_score)),
        "details": score_details
    }
    
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    run_verification()
