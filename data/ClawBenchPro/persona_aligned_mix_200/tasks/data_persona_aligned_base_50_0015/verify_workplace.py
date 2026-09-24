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
    target_file = os.path.join(workspace, "optimizations", "target_gates.json")
    
    details = []
    total_score = 0
    
    # 1. 检查目标文件是否存在 (10分)
    if os.path.exists(target_file):
        details.append({"item": "检查目标文件 target_gates.json 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件已建立"})
        total_score += 10
    else:
        details.append({"item": "检查目标文件 target_gates.json 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在，未按要求输出"})
        write_score(total_score, details)
        return

    # 2. 检查 JSON 格式合法性 (10分)
    # 此处严禁对结构化数据进行模糊匹配，必须原生解析
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        details.append({"item": "检查 JSON 格式合法性", "score": 10, "max_score": 10, "passed": True, "reason": "可成功解析为 JSON"})
        total_score += 10
    except Exception as e:
        details.append({"item": "检查 JSON 格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": f"非合法 JSON 格式，解析报错: {e}"})
        write_score(total_score, details)
        return

    # 3. 检查 Schema 数据结构合规性 (10分)
    # 题目明确要求输出 3 个逻辑门的 ID
    if isinstance(data, list) and len(data) == 3 and all(isinstance(x, str) for x in data):
        details.append({"item": "检查 Schema（含有3个字符串的数组）", "score": 10, "max_score": 10, "passed": True, "reason": "结构符合要求：一个包含3个字符串元素的列表"})
        total_score += 10
    else:
        details.append({"item": "检查 Schema（含有3个字符串的数组）", "score": 0, "max_score": 10, "passed": False, "reason": f"未返回仅包含 3 个字符串的数组。当前数据：{data}"})
        # 结构不对扣光后续分数，结束验证
        write_score(total_score, details)
        return
        
    # 4. 检查内容：命中率 (30分，每个关键 ID 10分)
    # 根据底层注入规则：数据量最大的 3 个门固定为 F9A1, F9A2, F9A3
    expected_gates = {"GATE_F9A1", "GATE_F9A2", "GATE_F9A3"}
    matched = set(data).intersection(expected_gates)
    hit_count = len(matched)
    hit_score = hit_count * 10
    
    if hit_count == 3:
        details.append({"item": "检查提取目标门 ID 的精确度", "score": 30, "max_score": 30, "passed": True, "reason": "完美找出所有 3 个异常通信量的逻辑门"})
    else:
        missing = expected_gates - set(data)
        details.append({"item": "检查提取目标门 ID 的精确度", "score": hit_score, "max_score": 30, "passed": False, "reason": f"找到了 {hit_count} 个异常逻辑门, 缺失 {missing}"})
    total_score += hit_score
    
    # 5. 检查内容：排序正确性 (40分)
    # 数据量排序：GATE_F9A1(3500B) > GATE_F9A2(2800B) > GATE_F9A3(2100B)
    expected_order = ["GATE_F9A1", "GATE_F9A2", "GATE_F9A3"]
    if data == expected_order:
        details.append({"item": "检查数组降序排序正确性", "score": 40, "max_score": 40, "passed": True, "reason": "元素严格按数据载荷大小从大到小排列"})
        total_score += 40
    else:
        # 如果找齐了三个，但排序错误，可给出部分分数 10 分以作梯度区分，如果没找齐则得 0 分。
        if hit_count == 3:
            details.append({"item": "检查数组降序排序正确性", "score": 10, "max_score": 40, "passed": False, "reason": f"找出了所有门但排序错误，期望 {expected_order}，实际 {data}"})
            total_score += 10
        else:
            details.append({"item": "检查数组降序排序正确性", "score": 0, "max_score": 40, "passed": False, "reason": "由于存在找错的门，排序亦判定为完全失败"})

    write_score(total_score, details)

def write_score(total_score, details):
    res = {
        "total_score": total_score,
        "details": details
    }
    # 确保写入工作目录下的 workplace_score.json
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    verify()
