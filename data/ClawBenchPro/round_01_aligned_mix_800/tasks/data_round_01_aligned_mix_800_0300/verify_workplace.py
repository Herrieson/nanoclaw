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

def check_workplace(workspace):
    details = []
    total_score = 0

    finished_dir = os.path.join(workspace, "finished_poems")
    summary_dir = os.path.join(workspace, "summary")
    catalog_path = os.path.join(summary_dir, "catalog.json")

    # 1. 检查目录结构 (10分)
    if os.path.isdir(finished_dir) and os.path.isdir(summary_dir):
        details.append({"item": "检查目标目录是否创建", "score": 10, "max_score": 10, "passed": True, "reason": "finished_poems 和 summary 目录存在"})
        total_score += 10
    else:
        details.append({"item": "检查目标目录是否创建", "score": 0, "max_score": 10, "passed": False, "reason": "缺少 finished_poems 或 summary 目录"})
        return generate_report(total_score, details)

    # 2. 检查干扰文件是否被剔除 (10分)
    finished_files = os.listdir(finished_dir)
    has_interference = any("shopping" in f.lower() or "games" in f.lower() for f in finished_files)
    if not has_interference and len(finished_files) >= 3:
        details.append({"item": "剔除干扰文件", "score": 10, "max_score": 10, "passed": True, "reason": "未发现干扰项目录，且包含所需诗歌"})
        total_score += 10
    else:
        details.append({"item": "剔除干扰文件", "score": 0, "max_score": 10, "passed": False, "reason": "输出了干扰文件或诗歌数量不足"})

    # 读取所有输出的诗歌内容以备检查
    poems_content = {}
    for f_name in finished_files:
        if f_name.endswith('.txt'):
            with open(os.path.join(finished_dir, f_name), 'r', encoding='utf-8') as f:
                poems_content[f_name.lower()] = f.read()

    # 3. 检查 Ocean Whispers 清理 (15分)
    ocean_content = next((v for k, v in poems_content.items() if "ocean" in k), "")
    if ocean_content and "<<<ERR>>>" not in ocean_content and "blue waves" in ocean_content.lower():
        details.append({"item": "Ocean Whispers 清理", "score": 15, "max_score": 15, "passed": True, "reason": "成功提取并清理乱码"})
        total_score += 15
    else:
        details.append({"item": "Ocean Whispers 清理", "score": 0, "max_score": 15, "passed": False, "reason": "未找到或未正确清理 <<<ERR>>>"})

    # 4. 检查 Midnight Ink 解码与清理 (15分)
    midnight_content = next((v for k, v in poems_content.items() if "midnight" in k), "")
    if midnight_content and "<<<ERR>>>" not in midnight_content and "slow honey" in midnight_content.lower():
        details.append({"item": "Midnight Ink 解码与清理", "score": 15, "max_score": 15, "passed": True, "reason": "成功从 Base64 解码并清理乱码"})
        total_score += 15
    else:
        details.append({"item": "Midnight Ink 解码与清理", "score": 0, "max_score": 15, "passed": False, "reason": "未能正确解码二进制/Base64文件或清理失败"})

    # 5. 检查 Cactus Flower OCR 与清理 (15分)
    cactus_content = next((v for k, v in poems_content.items() if "cactus" in k), "")
    if cactus_content and "<<<ERR>>>" not in cactus_content and "bloom in the desert" in cactus_content.lower():
        details.append({"item": "Cactus Flower OCR 识别与清理", "score": 15, "max_score": 15, "passed": True, "reason": "成功通过 OCR 获取内容并清理"})
        total_score += 15
    else:
        details.append({"item": "Cactus Flower OCR 识别与清理", "score": 0, "max_score": 15, "passed": False, "reason": "未能正确获取 OCR 文本或清理失败"})

    # 6. 检查 catalog.json (25分)
    if os.path.exists(catalog_path):
        try:
            with open(catalog_path, 'r', encoding='utf-8') as f:
                catalog_data = json.load(f)
            
            # 需要检查是否是一个列表，或者包含了三首诗的字典
            catalog_str = json.dumps(catalog_data).lower()
            if "official_title" in catalog_str and "valid_lines" in catalog_str:
                details.append({"item": "Catalog 格式与字段验证", "score": 25, "max_score": 25, "passed": True, "reason": "生成了合法的 JSON 且包含指定的结构化元数据"})
                total_score += 25
            else:
                details.append({"item": "Catalog 格式与字段验证", "score": 5, "max_score": 25, "passed": False, "reason": "JSON 缺少 official_title 或 valid_lines 字段"})
                total_score += 5
        except Exception as e:
            details.append({"item": "Catalog 格式与字段验证", "score": 0, "max_score": 25, "passed": False, "reason": f"JSON 解析失败: {e}"})
    else:
        details.append({"item": "Catalog 格式与字段验证", "score": 0, "max_score": 25, "passed": False, "reason": "未找到 catalog.json"})

    # 7. LLM 语义检测：检查输出的诗歌文件是否包含纯文本诗歌内容而没有混入多余的 Agent 对话或解释 (10分)
    all_poems_text = "\n\n".join(poems_content.values())
    prompt = "Check if the following text consists strictly of poetic verses without any conversational filler, markdown explanations, or agent commentary. Does it look like purely extracted poems?"
    if all_poems_text and llm_judge_content(prompt, all_poems_text):
        details.append({"item": "LLM 诗歌纯净度检测", "score": 10, "max_score": 10, "passed": True, "reason": "诗歌文本纯净，无 Agent 的对话冗余"})
        total_score += 10
    else:
        details.append({"item": "LLM 诗歌纯净度检测", "score": 0, "max_score": 10, "passed": False, "reason": "混入了 Markdown 解释、系统提示词或格式不佳"})

    return generate_report(total_score, details)

def generate_report(total_score, details):
    report = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return report

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    check_workplace(workspace)
