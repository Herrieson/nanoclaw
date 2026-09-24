import os
import sys
import json
import httpx
from openai import OpenAI

# ---------------------------------------------------------
# Environment & Mock LLM Setup
# ---------------------------------------------------------
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

# 必须关闭 SSL 验证
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

# ---------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------
def llm_judge_content(prompt_text, file_content):
    """Fallback LLM judge for pure unstructured semantic checks"""
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

def llm_extract_structured_data(file_content):
    """
    核心防御性编程策略：
    利用大模型将 Agent 生成的非结构化报告转化为标准的 JSON 格式，
    然后交由原生的 Python 代码进行严密且确定的结构化比对。
    这避免了用正则表达式模糊匹配 Agent 报告带来的假阴性/假阳性。
    """
    system_prompt = """
    You are an expert data extractor. Read the provided report and extract:
    1. A list of part names that need to be ordered.
    2. A dictionary of approved volunteers and their total worked hours.
    
    Return EXACTLY a JSON object matching this schema, no markdown blocks, no extra text:
    {
        "ordered_parts": ["string", "string"],
        "volunteer_hours": {
            "Firstname Lastname": numeric_hours
        }
    }
    """
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"[Report Content]:\n{file_content}"}
            ],
            response_format={ "type": "json_object" },
            temperature=0
        )
        return json.loads(response.choices[0].message.content.strip())
    except Exception as e:
        print(f"LLM Extraction Error: {e}")
        return None

# ---------------------------------------------------------
# Main Verification Logic
# ---------------------------------------------------------
def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    deliverables_dir = os.path.join(workspace, "deliverables")
    
    details = []
    total_score = 0
    
    # 1. 检查目录与文件存在性 (10分)
    deliverables_exist = os.path.exists(deliverables_dir) and os.path.isdir(deliverables_dir)
    files_in_deliverables = os.listdir(deliverables_dir) if deliverables_exist else []
    
    if deliverables_exist and len(files_in_deliverables) > 0:
        details.append({"item": "Deliverables 目录及文件生成", "score": 10, "max_score": 10, "passed": True, "reason": "成功创建目录并生成文件"})
        total_score += 10
    else:
        details.append({"item": "Deliverables 目录及文件生成", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 deliverables 目录或内部无文件"})
        # 结构毁灭性失败，直接写入结果
        with open("workplace_score.json", "w", encoding="utf-8") as f:
            json.dump({"total_score": 0, "details": details}, f, indent=2)
        return

    # 2. 读取所有交付物内容并尝试合并
    full_content = ""
    for filename in files_in_deliverables:
        filepath = os.path.join(deliverables_dir, filename)
        if os.path.isfile(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as file:
                    full_content += file.read() + "\n"
            except UnicodeDecodeError:
                pass # 忽略非文本文件

    # 3. 通过 LLM 桥接进行结构化提取
    extracted_data = llm_extract_structured_data(full_content)
    
    if not extracted_data or "ordered_parts" not in extracted_data or "volunteer_hours" not in extracted_data:
        details.append({"item": "内容解析与提取", "score": 0, "max_score": 90, "passed": False, "reason": "文件内容不包含清晰的采购列表或工时记录，或格式过于混乱导致解析失败"})
        with open("workplace_score.json", "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 获取统一小写列表用于健壮性代码校验
    ordered_parts_lower = [p.lower() for p in extracted_data.get("ordered_parts", [])]
    volunteer_hours = {k.lower(): v for k, v in extracted_data.get("volunteer_hours", {}).items()}

    # --- 维度 1: 零件采购准确性验证 ---
    # CH-101 (3): Oil Filter (High-Efficiency)
    if any("oil filter" in p for p in ordered_parts_lower):
        details.append({"item": "识别并订购短缺零件: Oil Filter", "score": 10, "max_score": 10, "passed": True, "reason": "成功包含 Oil Filter"})
        total_score += 10
    else:
        details.append({"item": "识别并订购短缺零件: Oil Filter", "score": 0, "max_score": 10, "passed": False, "reason": "漏掉 Oil Filter (High-Efficiency)"})

    # CH-303 (1): 120A Alternator
    if any("alternator" in p for p in ordered_parts_lower):
        details.append({"item": "识别并订购短缺零件: Alternator", "score": 10, "max_score": 10, "passed": True, "reason": "成功包含 120A Alternator"})
        total_score += 10
    else:
        details.append({"item": "识别并订购短缺零件: Alternator", "score": 0, "max_score": 10, "passed": False, "reason": "漏掉 120A Alternator"})

    # CH-505 (4): Iridium Spark Plugs
    if any("spark plug" in p for p in ordered_parts_lower):
        details.append({"item": "识别并订购短缺零件: Spark Plugs", "score": 10, "max_score": 10, "passed": True, "reason": "成功包含 Iridium Spark Plugs"})
        total_score += 10
    else:
        details.append({"item": "识别并订购短缺零件: Spark Plugs", "score": 0, "max_score": 10, "passed": False, "reason": "漏掉 Iridium Spark Plugs"})

    # 反向验证: 是否错误地包含了库存>=5的零件 (Brake Pads, Wiper Blades, Battery)
    if any(any(wrong in p for wrong in ["brake", "wiper", "battery"]) for p in ordered_parts_lower):
        details.append({"item": "精准过滤充足库存 (严查作弊)", "score": 0, "max_score": 10, "passed": False, "reason": "错误地订购了库存充足的零件 (如 Brake Pads/Wiper Blades/Battery)"})
    else:
        details.append({"item": "精准过滤充足库存 (严查作弊)", "score": 10, "max_score": 10, "passed": True, "reason": "正确剔除了不需要订购的零件"})
        total_score += 10

    # --- 维度 2: 志愿者工时统计验证 ---
    # Hector Ramirez (3.5 + 4.5 = 8.0)
    if volunteer_hours.get("hector ramirez") == 8.0:
        details.append({"item": "工时统计: Hector Ramirez", "score": 10, "max_score": 10, "passed": True, "reason": "准确累加计算出 8.0 小时"})
        total_score += 10
    else:
        details.append({"item": "工时统计: Hector Ramirez", "score": 0, "max_score": 10, "passed": False, "reason": f"未找到正确数据，实际值为 {volunteer_hours.get('hector ramirez')}"})

    # Luis Perez / Luis P. (2.0 + 3.0 = 5.0)
    # 考验 Agent 是否调用官方查询工具将 Luis P. 和 Luis Perez 合并
    if volunteer_hours.get("luis perez") == 5.0 or volunteer_hours.get("luis p.") == 5.0:
        details.append({"item": "工时统计与脏数据合并: Luis Perez", "score": 15, "max_score": 15, "passed": True, "reason": "成功将缩写 Luis P. 与全称合并并计算为 5.0 小时"})
        total_score += 15
    else:
        details.append({"item": "工时统计与脏数据合并: Luis Perez", "score": 0, "max_score": 15, "passed": False, "reason": "未成功将 Luis P. 映射或合并失败"})

    # Father Thomas / Fr. Thomas (1.5)
    if volunteer_hours.get("father thomas") == 1.5 or volunteer_hours.get("fr. thomas") == 1.5:
        details.append({"item": "工时统计与脏数据映射: Father Thomas", "score": 10, "max_score": 10, "passed": True, "reason": "成功识别并统计 1.5 小时"})
        total_score += 10
    else:
        details.append({"item": "工时统计与脏数据映射: Father Thomas", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 Father Thomas 的准确数据"})

    # Maria Gonzalez (5.0)
    if volunteer_hours.get("maria gonzalez") == 5.0:
        details.append({"item": "工时统计: Maria Gonzalez", "score": 10, "max_score": 10, "passed": True, "reason": "准确记录 5.0 小时"})
        total_score += 10
    else:
        details.append({"item": "工时统计: Maria Gonzalez", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 Maria Gonzalez 的准确数据"})

    # 反向验证: 是否排除了非白名单人员 (Sketchy Bob, Random Joe)
    if "sketchy bob" in volunteer_hours or "random joe" in volunteer_hours:
        details.append({"item": "严防幻觉与未授权名单排除", "score": 0, "max_score": 5, "passed": False, "reason": "未能过滤掉非教会批准人员 (Sketchy Bob 或 Random Joe)"})
    else:
        details.append({"item": "严防幻觉与未授权名单排除", "score": 5, "max_score": 5, "passed": True, "reason": "正确剔除所有未授权人员"})
        total_score += 5

    # 4. 汇总写入
    result = {
        "total_score": total_score,
        "details": details
    }
    
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
        
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    verify()
