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

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    target_file = os.path.join(workspace, "triage", "root_cause.json")
    
    score = 0
    details = []
    
    # 1. 检查文件是否存在和 JSON 格式 (20分)
    if not os.path.exists(target_file):
        details.append({
            "item": "检查目标文件是否存在", 
            "score": 0, 
            "max_score": 20, 
            "passed": False, 
            "reason": "文件 triage/root_cause.json 不存在"
        })
        return 0, details
        
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        details.append({
            "item": "检查目标文件格式", 
            "score": 20, 
            "max_score": 20, 
            "passed": True, 
            "reason": "成功解析 triage/root_cause.json 文件"
        })
        score += 20
    except Exception as e:
        details.append({
            "item": "检查目标文件格式", 
            "score": 0, 
            "max_score": 20, 
            "passed": False, 
            "reason": f"JSON 解析失败，非合法结构化数据: {e}"
        })
        return score, details
        
    # 2. 验证是否精确提取到发生下溢的 PTS (40分)
    # 使用深度遍历寻找正确的时间戳，兼容各种键名命名
    def find_pts(obj):
        if isinstance(obj, dict):
            for v in obj.values():
                if find_pts(v): return True
        elif isinstance(obj, list):
            for v in obj:
                if find_pts(v): return True
        elif isinstance(obj, int) and obj == 824888000:
            return True
        elif isinstance(obj, str) and obj.strip() == "824888000":
            return True
        return False
        
    if find_pts(data):
        details.append({
            "item": "验证引发下溢的 PTS", 
            "score": 40, 
            "max_score": 40, 
            "passed": True, 
            "reason": "成功在 JSON 中提取到正确的 PTS 值: 824888000"
        })
        score += 40
    else:
        details.append({
            "item": "验证引发下溢的 PTS", 
            "score": 0, 
            "max_score": 40, 
            "passed": False, 
            "reason": "未找到正确的 PTS 值 (预期 824888000)，或提取成了错误的干扰数据。"
        })
        
    # 3. 验证是否提取到了宏块错误坐标且未被噪音诱导 (40分)
    # 展平寻找长度为 2 的数字列表，不限制父级键名，以应对 LLM 自由构建的 schema
    def extract_coords(obj):
        coords = []
        # 判断是否为 [x, y] 格式
        if isinstance(obj, list) and len(obj) == 2 and all(isinstance(x, int) and not isinstance(x, bool) for x in obj):
            coords.append(obj)
        elif isinstance(obj, dict):
            for v in obj.values():
                coords.extend(extract_coords(v))
        elif isinstance(obj, list):
            for v in obj:
                coords.extend(extract_coords(v))
        return coords

    extracted = extract_coords(data)
    expected_coords = {(114, 52), (115, 52), (115, 53)}
    
    # 转为 set，去重同时方便交并集计算
    unique_extracted = set([tuple(c) for c in extracted])
    
    match_count = len(expected_coords.intersection(unique_extracted))
    false_positives = len(unique_extracted) - match_count
    
    coord_score = 0
    if match_count == 3 and false_positives == 0:
        coord_score = 40
        details.append({
            "item": "验证宏块错误坐标", 
            "score": 40, 
            "max_score": 40, 
            "passed": True, 
            "reason": "精确提取到全部 3 个正确坐标且未混入多余的干扰/幻觉数据"
        })
    elif match_count > 0:
        coord_score = 10 * match_count
        reason_str = f"提取到 {match_count} 个正确的宏块坐标。"
        if false_positives > 0:
            reason_str += f"但包含了 {false_positives} 个未报错或属于其他流的错误坐标，判定为被噪音误导，予以扣分。"
            coord_score -= (10 * false_positives)  # 误报一个扣10分
            
        coord_score = max(0, coord_score)
        details.append({
            "item": "验证宏块错误坐标", 
            "score": coord_score, 
            "max_score": 40, 
            "passed": False, 
            "reason": reason_str
        })
    else:
        details.append({
            "item": "验证宏块错误坐标", 
            "score": 0, 
            "max_score": 40, 
            "passed": False, 
            "reason": "未提取到任何正确的宏块坐标 (预期应包含 [114, 52], [115, 52], [115, 53])。"
        })
        
    score += coord_score
    return score, details

if __name__ == "__main__":
    score, details = verify()
    result = {
        "total_score": score,
        "details": details
    }
    with open(os.path.join(sys.argv[1] if len(sys.argv) > 1 else ".", "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
