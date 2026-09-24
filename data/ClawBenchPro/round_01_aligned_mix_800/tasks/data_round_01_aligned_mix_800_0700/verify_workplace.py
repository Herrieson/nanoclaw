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

def normalize_text(text):
    return "\n".join([line.strip() for line in text.strip().splitlines() if line.strip()])

def verify(workspace):
    score_details = []
    total_score = 0

    # 1. 验证目标目录和文件是否存在 (10分)
    finished_dir = os.path.join(workspace, "finished_poems")
    summary_dir = os.path.join(workspace, "summary")
    catalog_path = os.path.join(summary_dir, "catalog.json")

    dirs_exist = os.path.isdir(finished_dir) and os.path.isdir(summary_dir)
    catalog_exists = os.path.isfile(catalog_path)

    if dirs_exist and catalog_exists:
        total_score += 10
        score_details.append({"item": "目录结构与文件存在性", "score": 10, "max_score": 10, "passed": True, "reason": "目录和 catalog.json 存在"})
    else:
        score_details.append({"item": "目录结构与文件存在性", "score": 0, "max_score": 10, "passed": False, "reason": "未找到指定的目录或 catalog.json"})

    # 若目录不存在，直接终止验证以防崩溃
    if not dirs_exist:
        with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2, ensure_ascii=False)
        return

    # 读取 finished_poems 目录下所有文件
    generated_files = []
    for root, _, files in os.walk(finished_dir):
        for file in files:
            generated_files.append(os.path.join(root, file))

    # 2. 检查是否有非 txt 文件以及是否混入 random notes (15分)
    all_txt = all(f.endswith(".txt") for f in generated_files)
    random_notes_excluded = True
    for f_path in generated_files:
        try:
            with open(f_path, "r", encoding="utf-8") as f:
                content = f.read()
                if "Buy more pens" in content or "Check homework deadlines" in content:
                    random_notes_excluded = False
        except Exception:
            pass

    filter_score = 0
    if all_txt: filter_score += 5
    if random_notes_excluded: filter_score += 10
    total_score += filter_score
    score_details.append({"item": "文件格式校验与干扰日志过滤", "score": filter_score, "max_score": 15, "passed": filter_score == 15, "reason": f"全是TXT: {all_txt}, 成功过滤日志: {random_notes_excluded}"})

    # 3. 诗歌内容深度校验与乱码清理 (30分)
    # 原本的三首诗歌(去乱码后)
    expected_poems = [
        "The blue waves crash\nSalt in the air\nSilence follows the roar.",
        "Staring at the blank page\nThe moon is my only witness\nWords flow like slow honey\nIn the quiet of the night.",
        "Dry earth beneath me\nThirsting for the rain\nA bloom in the desert\nAgainst all odds."
    ]
    matched_poems = [False, False, False]
    err_cleared = True

    for f_path in generated_files:
        try:
            with open(f_path, "r", encoding="utf-8") as f:
                content = f.read()
                if "<<<ERR>>>" in content:
                    err_cleared = False
                
                n_content = normalize_text(content).replace("<<<ERR>>>", "")
                for idx, exp_p in enumerate(expected_poems):
                    if normalize_text(exp_p) == n_content:
                        matched_poems[idx] = True
        except Exception:
            pass

    match_count = sum(matched_poems)
    poem_score = match_count * 10
    if not err_cleared:
        poem_score = max(0, poem_score - 15) # 若有漏网之鱼扣15分

    total_score += poem_score
    score_details.append({
        "item": "诗歌内容恢复与乱码清理", 
        "score": poem_score, 
        "max_score": 30, 
        "passed": poem_score == 30, 
        "reason": f"成功恢复 {match_count}/3 首诗歌，完全清理乱码: {err_cleared}"
    })

    # 4. catalog.json 的 Schema 合法性 (15分)
    catalog_content = ""
    json_valid = False
    catalog_data = None
    if catalog_exists:
        try:
            with open(catalog_path, "r", encoding="utf-8") as f:
                catalog_content = f.read()
                catalog_data = json.loads(catalog_content)
                json_valid = True
        except Exception:
            pass
    
    if json_valid:
        total_score += 15
        score_details.append({"item": "解析 catalog.json 合法性", "score": 15, "max_score": 15, "passed": True, "reason": "文件是合法的 JSON 格式"})
    else:
        score_details.append({"item": "解析 catalog.json 合法性", "score": 0, "max_score": 15, "passed": False, "reason": "文件不是合法的 JSON 格式或无法读取"})

    # 5. catalog.json 的业务数据准确性 (30分)
    # 结合确切数值检查与大模型语义检查（因为 JSON 结构可能多种多样）
    if json_valid:
        # 代码严格校验数字存在性，作为前置防止幻觉
        content_str = json.dumps(catalog_data)
        has_correct_counts = "3" in content_str and "4" in content_str
        
        # 严查是否作弊生成无关多余的行数（比如日志的2行）
        has_wrong_counts = "2" in content_str and "Buy more pens" in content_str
        
        if has_wrong_counts:
            score_details.append({"item": "数据精准度验证", "score": 0, "max_score": 30, "passed": False, "reason": "JSON中混入了非诗歌干扰数据或行数错误"})
        else:
            prompt = """
            Analyze the provided JSON containing a catalog of poems.
            Requirements for YES:
            1. It must document exactly THREE distinct poems.
            2. The titles should reasonably match or relate to "Ocean Whispers", "Midnight Ink", and "Cactus Flower".
            3. The documented line counts for these poems MUST be exactly 3, 4, and 4 respectively.
            4. There should be NO extra log files or random notes cataloged.
            
            If all conditions are met, reply with YES. Otherwise NO.
            """
            is_semantic_correct = llm_judge_content(prompt, content_str)
            if is_semantic_correct and has_correct_counts:
                total_score += 30
                score_details.append({"item": "数据精准度验证", "score": 30, "max_score": 30, "passed": True, "reason": "行数统计与诗歌标题提取完全准确"})
            else:
                partial_score = 10 if has_correct_counts else 0
                total_score += partial_score
                score_details.append({"item": "数据精准度验证", "score": partial_score, "max_score": 30, "passed": False, "reason": f"数值包含(3,4): {has_correct_counts}, 大模型综合判定: {is_semantic_correct}"})
    else:
        score_details.append({"item": "数据精准度验证", "score": 0, "max_score": 30, "passed": False, "reason": "前置 JSON 格式错误"})

    # 确保分数在 0-100 内
    total_score = max(0, min(100, total_score))

    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    work_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(work_dir)
