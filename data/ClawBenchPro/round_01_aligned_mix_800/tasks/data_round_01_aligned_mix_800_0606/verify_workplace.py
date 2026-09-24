import os
import sys
import json
import httpx
import re
from openai import OpenAI

# 强制 API 规范初始化
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
    """
    统一的 LLM 语义检测接口。
    用于判断非结构化文本、格式规范性和无关冗余对话等。
    """
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

def extract_values(obj):
    """
    递归遍历并展平 JSON 中的所有确定性基础值。
    避免猜测未知的 key，直接审查 Agent 到底有没有成功输出目标的计算结果。
    """
    ints = []
    strings = []
    if isinstance(obj, dict):
        for v in obj.values():
            i, s = extract_values(v)
            ints.extend(i)
            strings.extend(s)
    elif isinstance(obj, list):
        for v in obj:
            i, s = extract_values(v)
            ints.extend(i)
            strings.extend(s)
    elif isinstance(obj, int):
        ints.append(obj)
    elif isinstance(obj, str):
        if obj.isdigit():
            ints.append(int(obj))
        else:
            strings.append(obj)
    return ints, strings

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_file = os.path.join(workspace, "workplace_score.json")
    
    total_score = 0
    details = []
    
    target_file = os.path.join(workspace, "deliverables", "gala_summary.json")
    
    # -------------------------------------------------------------
    # Item 1: 文件探针 - 检查目录和文件是否存在 (10 分)
    # -------------------------------------------------------------
    if os.path.exists(target_file):
        details.append({"item": "检查交付物文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件 deliverables/gala_summary.json 存在"})
        total_score += 10
    else:
        details.append({"item": "检查交付物文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到交付文件 deliverables/gala_summary.json"})
        with open(score_file, "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2, ensure_ascii=False)
        return
        
    # -------------------------------------------------------------
    # Item 2: 原生代码解析 - 结构化数据有效性检测 (10 分)
    # -------------------------------------------------------------
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            content_text = f.read()
            data = json.loads(content_text)
        details.append({"item": "检查 JSON 格式是否合法", "score": 10, "max_score": 10, "passed": True, "reason": "成功读取并解析 JSON 文件结构"})
        total_score += 10
    except Exception as e:
        details.append({"item": "检查 JSON 格式是否合法", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败，不符合结构化数据要求: {e}"})
        with open(score_file, "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2, ensure_ascii=False)
        return

    # -------------------------------------------------------------
    # Item 3: LLM 法官 - 数据纯净度与剧本遵循度 (10 分)
    # -------------------------------------------------------------
    prompt_text = "Does this JSON structurally contain ONLY the requested data (counts and names) without unnecessary conversational filler, email intros, or extra metadata? Return YES if clean."
    is_clean = llm_judge_content(prompt_text, content_text)
    if is_clean:
        details.append({"item": "利用大模型检查 JSON 语义结构是否纯粹", "score": 10, "max_score": 10, "passed": True, "reason": "大模型判定 JSON 结构简洁专业，无口语化冗余"})
        total_score += 10
    else:
        details.append({"item": "利用大模型检查 JSON 语义结构是否纯粹", "score": 0, "max_score": 10, "passed": False, "reason": "大模型判定 JSON 夹杂了冗余对话或违反要求的节点"})
        
    # 展平所有数据节点
    ints, strings = extract_values(data)
    all_text = " ".join(strings).lower()
    
    # -------------------------------------------------------------
    # Item 4: 原生代码精准提取 - 统计儿童书籍总数 (25 分)
    # -------------------------------------------------------------
    # 预期为 9 (Sarah:1 + Alice:1 + Beatrice:4 + Eleanor:3)
    if 9 in ints:
        details.append({"item": "精准验证儿童书数量结果", "score": 25, "max_score": 25, "passed": True, "reason": "成功在 JSON 独立节点值中匹配到精准计算结果: 9"})
        total_score += 25
    else:
        if "9" in all_text.split() or "nine" in all_text.split():
            details.append({"item": "精准验证儿童书数量结果", "score": 10, "max_score": 25, "passed": False, "reason": "数字 9 隐藏在长字符串中，但未能作为独立的 Integer 节点返回。"})
            total_score += 10
        else:
            details.append({"item": "精准验证儿童书数量结果", "score": 0, "max_score": 25, "passed": False, "reason": f"严重计算错误，未能在 JSON 键值中找到正确的总和 9。检测到的数字: {ints}"})
            
    # -------------------------------------------------------------
    # Item 5: 原生代码精准匹配 - 提取所有合法的 VIP 名字 (20 分)
    # -------------------------------------------------------------
    # 预期名单 (Has Book AND BakedGood): Sarah, John, Beatrice, Tom
    vips = ["sarah", "john", "beatrice", "tom"]
    words = re.findall(r'\b\w+\b', all_text)
    
    vip_score = 0
    found_vips = []
    missing_vips = []
    
    for v in vips:
        if v in words:
            vip_score += 5
            found_vips.append(v)
        else:
            missing_vips.append(v)
            
    if vip_score == 20:
        details.append({"item": "验证 VIP 父母名单完整性", "score": 20, "max_score": 20, "passed": True, "reason": "所有满足 VIP 资格的 First Name 均被成功提取"})
    else:
        details.append({"item": "验证 VIP 父母名单完整性", "score": vip_score, "max_score": 20, "passed": False, "reason": f"部分 VIP 数据遗漏或处理错误。已提取: {found_vips}, 遗漏: {missing_vips}"})
    total_score += vip_score
    
    # -------------------------------------------------------------
    # Item 6: 反幻觉与剧本指令扣分探针 - 剔除非 VIP 成员及 Last name (25 分)
    # -------------------------------------------------------------
    non_vips = ["alice", "marcus", "eleanor"]
    last_names = ["connor", "smith", "johnson"]
    
    found_non_vips = [nv for nv in non_vips if nv in words]
    found_last_names = [ln for ln in last_names if ln in words]
    
    rigor_score = 25
    reason_parts = []
    
    if found_non_vips:
        rigor_score -= len(found_non_vips) * 6
        reason_parts.append(f"错误包含了未达标的家长({','.join(found_non_vips)})")
        
    if found_last_names:
        rigor_score -= len(found_last_names) * 3
        reason_parts.append(f"错误包含了 Last Name({','.join(found_last_names)})，未遵循仅提取 First Name 的指令")
        
    if rigor_score < 0: 
        rigor_score = 0
    
    if not reason_parts:
        details.append({"item": "防误判严谨度验证（反幻觉检测）", "score": 25, "max_score": 25, "passed": True, "reason": "数据极度干净：无非VIP人员混入，严格去除了所有的 Last Name"})
    else:
        details.append({"item": "防误判严谨度验证（反幻觉检测）", "score": rigor_score, "max_score": 25, "passed": False, "reason": "存在提取误判或指令违背: " + "；".join(reason_parts)})
    total_score += rigor_score
        
    # 写回沙盒结果
    with open(score_file, "w", encoding="utf-8") as f:
        json.dump({"total_score": int(total_score), "details": details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
