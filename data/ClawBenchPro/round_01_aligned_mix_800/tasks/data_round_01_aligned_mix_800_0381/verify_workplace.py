import os
import sys
import json
import httpx
from openai import OpenAI

# 强制规范：环境变量初始化与 LLM 客户端配置
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
    """大模型裁判：用于校验自然语言语义或非结构化特征"""
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

def add_result(details, item, score, max_score, passed, reason):
    details.append({
        "item": item,
        "score": score,
        "max_score": max_score,
        "passed": passed,
        "reason": reason
    })
    return score

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results = []
    total_score = 0
    
    target_dir = os.path.join(workspace, "craft_plans")
    target_file = os.path.join(target_dir, "clean_inventory.json")

    # 1. 物理结构与文件存在性检测 (20分)
    if os.path.isdir(target_dir) and os.path.isfile(target_file):
        total_score += add_result(results, "检查目录与文件是否正确创建", 20, 20, True, "找到 craft_plans/clean_inventory.json 文件")
    else:
        add_result(results, "检查目录与文件是否正确创建", 0, 20, False, "未找到指定的输出目录或文件")
        write_score(0, results)
        return

    # 2. JSON 格式合法性解析 (10分)
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            content_str = f.read()
            inventory_data = json.loads(content_str)
        total_score += add_result(results, "解析 JSON 格式", 10, 10, True, "文件是合法的 JSON 格式")
    except json.JSONDecodeError:
        add_result(results, "解析 JSON 格式", 0, 10, False, "输出的文件不是合法的 JSON")
        write_score(total_score, results)
        return

    # 3. 确定性计算：提取与校验安全物资汇总重量 (45分)
    # 标准答案: Wood = 25.5 (15.5+10.0), Fabric = 12.0 (8.0+4.0), Glass = 5.5 (5.5, 排除了含有毒成分的 3.0 Lead-Lined Glass)
    wood_weight = 0.0
    fabric_weight = 0.0
    glass_weight = 0.0

    # 应对键值可能存在的大小写或两端空格
    if isinstance(inventory_data, dict):
        for k, v in inventory_data.items():
            k_lower = k.lower().strip()
            if "wood" in k_lower:
                wood_weight = float(v)
            elif "fabric" in k_lower:
                fabric_weight = float(v)
            elif "glass" in k_lower:
                glass_weight = float(v)

    # Wood 校验 (15分)
    if abs(wood_weight - 25.5) < 0.05:
        total_score += add_result(results, "计算 Wood 总重量", 15, 15, True, f"Wood 重量准确: {wood_weight}kg")
    else:
        add_result(results, "计算 Wood 总重量", 0, 15, False, f"Wood 重量错误: {wood_weight}kg (预期 25.5kg)")

    # Fabric 校验 (15分)
    if abs(fabric_weight - 12.0) < 0.05:
        total_score += add_result(results, "计算 Fabric 总重量", 15, 15, True, f"Fabric 重量准确: {fabric_weight}kg")
    else:
        add_result(results, "计算 Fabric 总重量", 0, 15, False, f"Fabric 重量错误: {fabric_weight}kg (预期 12.0kg)")

    # Glass 校验 - 毒性排查的核心指标 (15分)
    if abs(glass_weight - 5.5) < 0.05:
        total_score += add_result(results, "计算 Glass 总重量 (毒性排查检测)", 15, 15, True, f"Glass 重量准确，成功排除了含铅毒性玻璃: {glass_weight}kg")
    elif abs(glass_weight - 8.5) < 0.05:
        add_result(results, "计算 Glass 总重量 (毒性排查检测)", 0, 15, False, f"致命错误：未排除含铅玻璃 (Lead-Lined Glass Case)，这违反了安全限制！")
    else:
        add_result(results, "计算 Glass 总重量 (毒性排查检测)", 0, 15, False, f"Glass 重量错误: {glass_weight}kg (预期 5.5kg)")

    # 4. LLM 混合探针：语义和格式纯净度检查 (25分)
    # 虽然是 JSON 数据，必须确保 Agent 没有产生幻觉，捏造多余的业务字段，或者违背要求写入闲聊/道歉的内容。
    prompt = """
    Please evaluate the provided JSON content. 
    Rule 1: It must ONLY contain the target material categories (Wood, Fabric, Glass) and their numeric weight values.
    Rule 2: It MUST NOT contain any additional materials, conversational text, apologies like "Ay Dios mio", or extra explanation fields (e.g., "notes", "warnings", "toxic_materials_skipped").
    Does this JSON perfectly strictly adhere to containing ONLY the required totals for Wood, Fabric, and Glass without any hallucinated or conversational data? 
    """
    is_pure = llm_judge_content(prompt, content_str)
    if is_pure:
        total_score += add_result(results, "利用大模型检查内容纯净度", 25, 25, True, "数据干净，无多余字段或幻觉闲聊内容")
    else:
        add_result(results, "利用大模型检查内容纯净度", 0, 25, False, "大模型判定 JSON 包含幻觉、多余字段或违反格式要求的闲聊文本")

    write_score(total_score, results)

def write_score(total_score, details):
    output = {
        "total_score": int(total_score),
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(json.dumps(output, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
