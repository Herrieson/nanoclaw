import os
import sys
import json
import httpx
import re
import random
from openai import OpenAI

# 强制要求 API 规范，用于后续语义检测
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
    """用于对非结构化文本进行语义/幻觉检测的统一接口"""
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

# 地面真理 (Ground Truth)：剔除 Title 及空行后的标准行数
EXPECTED_POEMS = {
    "Ocean Whispers": 3,
    "Midnight Ink": 4,
    "Cactus Flower": 4,
    "Urban Echoes": 3,
    "Fading Embers": 3,
    "Silent Observer": 3,
    "Morning Dew": 3,
    "Rust and Iron": 3,
    "Whispering Pines": 3,
    "Desert Rain": 3,
    "Lost Compass": 3,
    "Clockwork Heart": 3,
    "Fallen Leaves": 3,
    "Stardust": 3,
    "Hidden Cave": 3,
    "Rising Tide": 3,
    "Frozen Lake": 3,
    "Golden Hour": 3,
    "Wildfire": 3,
    "Paper Boats": 3
}

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    total_score = 0
    details = []

    def add_score(item, score, max_score, reason):
        nonlocal total_score
        total_score += score
        details.append({
            "item": item,
            "score": score,
            "max_score": max_score,
            "passed": score == max_score,
            "reason": reason
        })

    poems_dir = os.path.join(workspace, "finished_poems")
    summary_dir = os.path.join(workspace, "summary")
    catalog_path = os.path.join(summary_dir, "catalog.json")

    # [1] 检查核心输出目录存在性 (5分)
    if os.path.exists(poems_dir) and os.path.isdir(poems_dir):
        add_score("检查目标产出目录 finished_poems", 5, 5, "目录已存在")
    else:
        add_score("检查目标产出目录 finished_poems", 0, 5, "目录缺失或并非文件夹")

    # [2] 检查统计文件存在性 (10分)
    if os.path.exists(catalog_path) and os.path.isfile(catalog_path):
        add_score("检查清单文件 summary/catalog.json", 10, 10, "文件已存在")
    else:
        add_score("检查清单文件 summary/catalog.json", 0, 10, "文件缺失")

    # [3] 精确解析 catalog.json (5分)
    json_data = None
    if os.path.exists(catalog_path):
        try:
            with open(catalog_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            add_score("检查 catalog.json 解析格式", 5, 5, "成功解析为原生 JSON")
        except Exception as e:
            add_score("检查 catalog.json 解析格式", 0, 5, f"JSON解析失败: {str(e)}")
    else:
        add_score("检查 catalog.json 解析格式", 0, 5, "文件不存在，跳过解析")

    # [4] 严查 JSON Schema 与字段防伪 (10分)
    is_schema_valid = False
    if json_data is not None:
        if not isinstance(json_data, dict) or "poems" not in json_data:
            add_score("检查 JSON Schema", 0, 10, "缺少顶级 poems 数组对象")
        elif not isinstance(json_data["poems"], list):
            add_score("检查 JSON Schema", 0, 10, "poems 字段不是数组")
        else:
            schema_ok = True
            for p in json_data["poems"]:
                if not isinstance(p, dict) or "title" not in p or "lines" not in p:
                    schema_ok = False; break
                if not isinstance(p["title"], str) or not isinstance(p["lines"], int):
                    schema_ok = False; break
            
            # 严防大模型幻觉与作弊捏造多余节点
            has_extra_fields = any(len(p.keys()) > 2 for p in json_data["poems"] if isinstance(p, dict))

            if not schema_ok:
                add_score("检查 JSON Schema", 0, 10, "poems 数组内的元素缺失 title/lines，或数据类型不匹配")
            elif has_extra_fields:
                add_score("检查 JSON Schema", 0, 10, "严重违规：检测到捏造的多余键字段")
            else:
                is_schema_valid = True
                add_score("检查 JSON Schema", 10, 10, "Schema 完全合法，无冗余字段幻觉")
    else:
        add_score("检查 JSON Schema", 0, 10, "未获得有效 JSON 数据")

    # 获取生成的诗歌物理文件
    txt_files = []
    if os.path.exists(poems_dir) and os.path.isdir(poems_dir):
        txt_files = [f for f in os.listdir(poems_dir) if f.endswith(".txt")]

    # [5] 验证多段逻辑的第一跳：废土噪音免疫 (10分)
    if len(txt_files) == 20:
        add_score("检查文件提取数量是否完美排除诱饵", 10, 10, "提取文件数量严格为 20，未受噪音感染")
    elif len(txt_files) > 0:
        add_score("检查文件提取数量是否完美排除诱饵", 0, 10, f"提取了 {len(txt_files)} 个文件，说明暴力遍历导致混入废初稿，或遗漏目标")
    else:
        add_score("检查文件提取数量是否完美排除诱饵", 0, 10, "未生成任何有效文件")

    # [6] 进一步校验 JSON 内容对真实目标的捕捉 (10分)
    if is_schema_valid:
        titles_in_json = [p["title"] for p in json_data["poems"]]
        unapproved = [t for t in titles_in_json if t not in EXPECTED_POEMS]
        if len(unapproved) == 0 and len(titles_in_json) == 20:
            add_score("检查统计清单是否精准映射白名单", 10, 10, "精准抓取，不含任何未授权标题")
        else:
            add_score("检查统计清单是否精准映射白名单", 0, 10, f"混入了非法标题或抓取数量不足: {unapproved[:3]}")
    else:
        add_score("检查统计清单是否精准映射白名单", 0, 10, "Schema 不合法，跳过校验")

    # [7] 校验命名规则执行能力 (5分)
    if txt_files:
        naming_correct = True
        for f in txt_files:
            if not re.match(r'^[a-z_]+\.txt$', f):
                naming_correct = False
                break
        if naming_correct:
            add_score("检查文件命名规范约束", 5, 5, "完全符合全小写且空格下划线转换规则")
        else:
            add_score("检查文件命名规范约束", 0, 5, "部分文件名存在大写、空格或非法字符遗漏")
    else:
        add_score("检查文件命名规范约束", 0, 5, "无文件可检")

    # [8] 验证正则清洗与乱码修复彻底性 (15分)
    if txt_files:
        has_err = False
        for f in txt_files:
            try:
                with open(os.path.join(poems_dir, f), 'r', encoding='utf-8') as rf:
                    content = rf.read()
                    # 严查是否残留 6位十六进制标签 或 不完整清洗残骸
                    if re.search(r'<<<ERR-[a-fA-F0-9]{6}>>>', content) or '<<<ERR-' in content:
                        has_err = True
                        break
            except Exception:
                has_err = True
        
        if not has_err:
            add_score("检查十六进制乱码标签清洗彻底性", 15, 15, "未发现任何乱码标签残骸")
        else:
            add_score("检查十六进制乱码标签清洗彻底性", 0, 15, "替换逻辑脆弱，文件中发现残留的乱码或结构标签")
    else:
        add_score("检查十六进制乱码标签清洗彻底性", 0, 15, "无文件可检")

    # [9] 考核极端条件下的数值统计精度 (20分)
    if is_schema_valid:
        matched = True
        poems_dict = {p["title"]: p["lines"] for p in json_data["poems"]}
        for t, expected_l in EXPECTED_POEMS.items():
            if t not in poems_dict or poems_dict[t] != expected_l:
                matched = False
                break
        if matched:
            add_score("检查精准且带过滤逻辑的行数统计算法", 20, 20, "完美避开了空行计算、Title 行计算干扰，数值与标准真理毫无偏差")
        else:
            add_score("检查精准且带过滤逻辑的行数统计算法", 0, 20, "存在统计偏差，未能正确 strip 空白行或未排除首行干扰")
    else:
        add_score("检查精准且带过滤逻辑的行数统计算法", 0, 20, "无法进行统计比对")

    # [10] 利用 LLM 进行语意与幻觉审查 (10分)
    if txt_files:
        random_file = random.choice(txt_files)
        try:
            with open(os.path.join(poems_dir, random_file), "r", encoding="utf-8") as rf:
                sample_content = rf.read()
            
            prompt = (
                "Please verify if the following text is a natural, coherent English poem. "
                "It MUST NOT contain any programming logs, python traces, crash codes, JSON fragments, hexadecimal strings, or hallucinated system tags. "
                "If it is purely clean poetry text, return 'YES'. Otherwise, return 'NO'."
            )
            is_clean = llm_judge_content(prompt, sample_content)
            if is_clean:
                add_score("LLM 大模型诗歌语意校验及无痕检查", 10, 10, "经大模型查验，恢复的文本为纯净自然诗歌语意，无代码泄露或幻觉")
            else:
                add_score("LLM 大模型诗歌语意校验及无痕检查", 0, 10, "大模型检测出混杂的系统提示词、代码片段或生硬结构幻觉")
        except Exception as e:
            add_score("LLM 大模型诗歌语意校验及无痕检查", 0, 10, f"验证失败: {str(e)}")
    else:
        add_score("LLM 大模型诗歌语意校验及无痕检查", 0, 10, "无文件可检")

    # 结果固化
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()
