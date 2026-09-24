import os
import sys
import json
import httpx
from openai import OpenAI

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
    # 此函数为检测非结构化文本的统一接口
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

def extract_ints(obj):
    res = []
    if isinstance(obj, int):
        res.append(obj)
    elif isinstance(obj, str) and obj.isdigit():
        res.append(int(obj))
    elif isinstance(obj, list):
        for item in obj:
            res.extend(extract_ints(item))
    elif isinstance(obj, dict):
        for item in obj.values():
            res.extend(extract_ints(item))
    return res

def extract_coords(obj):
    coords = []
    if isinstance(obj, list):
        if len(obj) == 2 and isinstance(obj[0], (int, float)) and isinstance(obj[1], (int, float)):
            coords.append([int(obj[0]), int(obj[1])])
        else:
            for item in obj:
                coords.extend(extract_coords(item))
    elif isinstance(obj, dict):
        if 'x' in obj and 'y' in obj and isinstance(obj['x'], (int, float)) and isinstance(obj['y'], (int, float)):
            coords.append([int(obj['x']), int(obj['y'])])
        else:
            for item in obj.values():
                coords.extend(extract_coords(item))
    return coords

def verify_workplace(workspace):
    score = 0
    details = []

    # 1. 检查目标目录 (10分)
    triage_dir = os.path.join(workspace, "triage")
    if os.path.exists(triage_dir) and os.path.isdir(triage_dir):
        score += 10
        details.append({"item": "检查目标目录 triage", "score": 10, "max_score": 10, "passed": True, "reason": "triage 目录存在"})
    else:
        details.append({"item": "检查目标目录 triage", "score": 0, "max_score": 10, "passed": False, "reason": "triage 目录不存在"})
    
    # 2. 检查 JSON 文件合法性 (10分)
    json_path = os.path.join(triage_dir, "root_cause.json")
    json_obj = None
    content = ""
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                content = f.read()
            json_obj = json.loads(content)
            score += 10
            details.append({"item": "检查 root_cause.json 合法性", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 文件合法且可通过原生 json.loads 解析"})
        except Exception as e:
            details.append({"item": "检查 root_cause.json 合法性", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败或格式非法: {e}"})
    else:
        details.append({"item": "检查 root_cause.json 合法性", "score": 0, "max_score": 10, "passed": False, "reason": "文件 root_cause.json 不存在"})
        
    # 内容确定性检查
    if json_obj is not None:
        all_ints = extract_ints(json_obj)
        target_pts = 824672800 # (824050000 + 173 * 3600)
        
        # 3. PTS 精准定位 (20分)
        if target_pts in all_ints:
            score += 20
            details.append({"item": "提取目标致命 PTS", "score": 20, "max_score": 20, "passed": True, "reason": f"成功在结构化数据中提取到引发下溢的精准 PTS: {target_pts}"})
        else:
            details.append({"item": "提取目标致命 PTS", "score": 0, "max_score": 20, "passed": False, "reason": "未在结果数据中找到致命故障瞬间对应的准确 PTS 戳"})
            
        # 4. 坐标精准提取 (30分)
        extracted_coords = extract_coords(json_obj)
        target_coords = [[114, 52], [115, 52], [115, 53]]
        matched_coords = []
        for c in target_coords:
            if c in extracted_coords:
                matched_coords.append(c)
        
        coord_score = 0
        if len(matched_coords) == 3:
            coord_score = 30
            details.append({"item": "提取受影响宏块坐标", "score": 30, "max_score": 30, "passed": True, "reason": "成功提取受影响的全部 3 个宏块坐标"})
        else:
            coord_score = len(matched_coords) * 10
            details.append({"item": "提取受影响宏块坐标", "score": coord_score, "max_score": 30, "passed": coord_score > 0, "reason": f"部分匹配，提取了 {len(matched_coords)}/3 个宏块坐标"})
        score += coord_score
        
        # 5. 检查数据纯净度，严查幻觉 (20分)
        # 将超过8亿的数字视为 PTS 戳候选，如果有其他不属于目标 PTS 的时间戳混入，视为数据冗余。
        redundant_pts = [v for v in all_ints if v > 800000000 and v != target_pts]
        # 判断是否包含捏造的坐标
        redundant_coords = [c for c in extracted_coords if c not in target_coords]
        
        penalty_reasons = []
        if redundant_pts:
            penalty_reasons.append("混入了非致错瞬间的冗余 PTS")
        if redundant_coords:
            penalty_reasons.append("捏造或包含了未报错的宏块坐标数据")
            
        if not penalty_reasons:
            score += 20
            details.append({"item": "结构化幻觉及冗余审查", "score": 20, "max_score": 20, "passed": True, "reason": "数据极度纯净，无任何伪造节点或多余不相关参数"})
        else:
            details.append({"item": "结构化幻觉及冗余审查", "score": 0, "max_score": 20, "passed": False, "reason": f"严厉扣分：{'；'.join(penalty_reasons)}"})
        
        # 6. 利用大模型判断非结构化文字的“无废话”原则遵从度 (10分)
        prompt_text = "Does the following file strictly contain only necessary structured data elements without ANY conversational filler, textbook-style explanation, or redundant natural language narrative?"
        llm_passed = llm_judge_content(prompt_text, content)
        if llm_passed:
            score += 10
            details.append({"item": "LLM语义法官：无废话指令检查", "score": 10, "max_score": 10, "passed": True, "reason": "文件纯粹且未包含冗长啰嗦的自然语言推导"})
        else:
            details.append({"item": "LLM语义法官：无废话指令检查", "score": 0, "max_score": 10, "passed": False, "reason": "严重违背了暴躁工程师的『别废话』Persona，包含了教科书式推导内容"})

    else:
        details.append({"item": "提取目标致命 PTS", "score": 0, "max_score": 20, "passed": False, "reason": "JSON 解析失败，依赖结构化的数值提取无法进行"})
        details.append({"item": "提取受影响宏块坐标", "score": 0, "max_score": 30, "passed": False, "reason": "JSON 解析失败，无法提取确定的坐标信息"})
        details.append({"item": "结构化幻觉及冗余审查", "score": 0, "max_score": 20, "passed": False, "reason": "JSON 解析失败"})
        details.append({"item": "LLM语义法官：无废话指令检查", "score": 0, "max_score": 10, "passed": False, "reason": "JSON 格式非法无法评估"})

    result = {
        "total_score": score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify_workplace(workspace)
