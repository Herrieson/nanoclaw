import os
import sys
import json
import re
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

def extract_json_from_text(content):
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        match = re.search(r'\{[\s\S]*\}', content)
        if match:
            try:
                return json.loads(match.group(0))
            except:
                return None
    return None

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_file = os.path.join(workspace, "output/critical_state.json")
    
    score_details = []
    total_score = 0
    
    # 1. 存在性与格式校验 (20分)
    if not os.path.exists(report_file):
        score_details.append({
            "item": "核心产物存在性",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "未找到产物文件 output/critical_state.json，Agent 失败或路径错误"
        })
        # 若完全没有文件，结构项也是 0 分
        score_details.append({
            "item": "JSON格式与结构化约束",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件不存在，无法校验格式"
        })
        write_score(0, score_details, workspace)
        return

    score_details.append({
        "item": "核心产物存在性",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "成功定位到 output/critical_state.json"
    })
    
    with open(report_file, 'r', encoding='utf-8') as f:
        raw_content = f.read()
        
    parsed_json = extract_json_from_text(raw_content)
    
    if parsed_json is None:
        score_details.append({
            "item": "JSON格式与结构化约束",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件内容不符合严格 JSON 结构，无法被原生代码解析"
        })
        # 如果不是标准 JSON，尝试利用大模型判定是否有相关文本答案作为底裤得分
        has_temp = llm_judge_content("Does the text explicitly state that the max temperature is approximately 124.65?", raw_content)
        has_quat = llm_judge_content("Does the text explicitly contain the quaternion sequence 0.1234, 0.5678, -0.1234, -0.5678?", raw_content)
        
        # 给予少量的非结构化宽容分，但严禁给满分
        fallback_score = 0
        if has_temp: fallback_score += 10
        if has_quat: fallback_score += 10
        
        score_details.append({
            "item": "利用大模型检索非结构化文本的等效结果",
            "score": fallback_score,
            "max_score": 80,
            "passed": fallback_score > 0,
            "reason": "JSON 解析失败，但大模型检测到部分正确的关键计算值。由于未遵守 JSON 契约被严厉扣分。"
        })
        write_score(10 + fallback_score, score_details, workspace)
        return

    # 若 JSON 解析成功
    valid_keys = {"latest_quaternion", "max_temperature"}
    actual_keys = set(parsed_json.keys())
    
    if actual_keys == valid_keys:
        score_details.append({
            "item": "JSON格式与结构化约束",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "完全满足 JSON 键名约束，没有多余的层级与字段"
        })
    else:
        score_details.append({
            "item": "JSON格式与结构化约束",
            "score": 5,
            "max_score": 10,
            "passed": False,
            "reason": f"成功提取 JSON，但包含多余或缺失的键：{actual_keys}"
        })

    # 2. 最高温度精准校验 (40分)
    temp_val = parsed_json.get("max_temperature", None)
    temp_score = 0
    temp_reason = "未能获取 max_temperature 值"
    
    if isinstance(temp_val, (int, float)):
        if abs(temp_val - 124.65) <= 0.02:
            temp_score = 40
            temp_reason = "准确找到真实数据帧内的温度极值 124.65"
        elif abs(temp_val - 888.88) <= 0.02:
            temp_score = 0
            temp_reason = "严重幻觉/误读：提取了 888.88，被旧版同步头的诱饵数据欺骗，未阅读最新应急报告"
        elif abs(temp_val - 987.65) <= 0.02 or abs(temp_val - 555.55) <= 0.02:
            temp_score = 0
            temp_reason = "逻辑缺陷：提取了被宇宙射线污染的假数据，未在代码中执行 APID 的 XOR Checksum 过滤规则"
        else:
            temp_score = 0
            temp_reason = f"数值计算错误或提取偏差：得到了预期外的数值 {temp_val}"
    
    score_details.append({
        "item": "极值温度计算准确度",
        "score": temp_score,
        "max_score": 40,
        "passed": temp_score == 40,
        "reason": temp_reason
    })

    # 3. 最新四元数精准校验 (40分)
    quat_val = parsed_json.get("latest_quaternion", None)
    quat_score = 0
    quat_reason = "未能获取 latest_quaternion 值"
    
    target_quat = [0.1234, 0.5678, -0.1234, -0.5678]
    fake_quat = [0.9999, 0.9999, 0.9999, 0.9999]
    
    if isinstance(quat_val, list) and len(quat_val) == 4 and all(isinstance(x, (int, float)) for x in quat_val):
        diff_target = sum(abs(a - b) for a, b in zip(quat_val, target_quat))
        diff_fake = sum(abs(a - b) for a, b in zip(quat_val, fake_quat))
        
        if diff_target < 0.001:
            quat_score = 40
            quat_reason = "准确通过滑动窗口提取到时间戳最新的真实有效四元数序列"
        elif diff_fake < 0.001:
            quat_score = 0
            quat_reason = "逻辑缺陷：提取到了 1900000000 极高时间戳的诱饵数据，未过滤错误 Checksum 的幽灵帧"
        else:
            quat_score = 0
            quat_reason = f"未找到最新时间戳的数据，或提取了错误的有效帧：{quat_val}"
            
    elif quat_val is not None:
        quat_reason = f"latest_quaternion 数据格式不正确，必须为 4 个浮点数的列表，当前为：{type(quat_val)}"

    score_details.append({
        "item": "有效星象仪四元数解析准确度",
        "score": quat_score,
        "max_score": 40,
        "passed": quat_score == 40,
        "reason": quat_reason
    })
    
    total_score = sum(item["score"] for item in score_details)
    write_score(total_score, score_details, workspace)

def write_score(total_score, details, workspace):
    result = {
        "total_score": total_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
