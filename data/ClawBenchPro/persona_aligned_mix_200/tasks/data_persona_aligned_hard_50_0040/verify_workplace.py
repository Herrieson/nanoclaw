#!/usr/bin/env python3
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
    
    report_dir = os.path.join(workspace, "reports")
    report_file = os.path.join(report_dir, "bottleneck.json")
    
    score_details = []
    total_score = 0
    
    # 1. 检查目录是否存在 (5分)
    if os.path.isdir(report_dir):
        score_details.append({"item": "检查 reports 目录是否存在", "score": 5, "max_score": 5, "passed": True, "reason": "reports 目录存在"})
        total_score += 5
    else:
        score_details.append({"item": "检查 reports 目录是否存在", "score": 0, "max_score": 5, "passed": False, "reason": "reports 目录不存在"})
        
    # 2. 检查文件是否存在 (15分)
    if os.path.isfile(report_file):
        score_details.append({"item": "检查 bottleneck.json 文件是否存在", "score": 15, "max_score": 15, "passed": True, "reason": "bottleneck.json 文件存在"})
        total_score += 15
    else:
        score_details.append({"item": "检查 bottleneck.json 文件是否存在", "score": 0, "max_score": 15, "passed": False, "reason": "bottleneck.json 文件不存在"})
        
    # 如果文件不存在，直接返回当前分数
    if not os.path.isfile(report_file):
        with open("workplace_score.json", "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    # 3. 检查 JSON 格式合法性 (10分)
    try:
        with open(report_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        score_details.append({"item": "解析 bottleneck.json", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 文件格式正确，可以成功解析"})
        total_score += 10
    except Exception as e:
        score_details.append({"item": "解析 bottleneck.json", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 文件解析失败: {e}"})
        data = None

    if data is None:
        with open("workplace_score.json", "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    # 4. 检查 Schema 字段要求 (10分)
    if not isinstance(data, dict):
        score_details.append({"item": "检查 JSON Schema", "score": 0, "max_score": 10, "passed": False, "reason": "JSON 的根节点不是对象/字典格式"})
    else:
        actual_keys = set(data.keys())
        expected_keys = {"EID", "BLK_SIZE_BYTES"}
        
        if actual_keys == expected_keys:
            score_details.append({"item": "检查 JSON Schema", "score": 10, "max_score": 10, "passed": True, "reason": "仅包含要求的两个键，无冗余/虚假字段"})
            total_score += 10
        elif expected_keys.issubset(actual_keys):
            score_details.append({"item": "检查 JSON Schema", "score": 0, "max_score": 10, "passed": False, "reason": "包含了要求的键，但夹杂了多余/幻觉产生的冗余字段，严惩扣分"})
        else:
            score_details.append({"item": "检查 JSON Schema", "score": 0, "max_score": 10, "passed": False, "reason": f"未包含完整的必要字段。期望: {expected_keys}, 实际: {actual_keys}"})

    # 5. 检查 EID (30分)
    if isinstance(data, dict) and "EID" in data:
        eid_val = str(data["EID"]).strip().lower()
        if eid_val == "0x7c9a":
            score_details.append({"item": "校验 EID 准确性", "score": 30, "max_score": 30, "passed": True, "reason": "成功找到并写入正确的真凶实体 ID"})
            total_score += 30
        else:
            score_details.append({"item": "校验 EID 准确性", "score": 0, "max_score": 30, "passed": False, "reason": f"EID 错误。获取到: {eid_val}，与真实超标耗时记录不符"})
    else:
        score_details.append({"item": "校验 EID 准确性", "score": 0, "max_score": 30, "passed": False, "reason": "缺少 EID 数据或数据格式错误"})

    # 6. 检查 BLK_SIZE_BYTES (30分)
    if isinstance(data, dict) and "BLK_SIZE_BYTES" in data:
        blk_val = data["BLK_SIZE_BYTES"]
        
        if isinstance(blk_val, int) and blk_val == 131072:
            score_details.append({"item": "校验 BLK_SIZE_BYTES 准确性", "score": 30, "max_score": 30, "passed": True, "reason": "成功查证并写入正确的内存块大小，且类型为严格的整数类型"})
            total_score += 30
        elif str(blk_val).strip() == "131072":
            score_details.append({"item": "校验 BLK_SIZE_BYTES 准确性", "score": 15, "max_score": 30, "passed": False, "reason": "数据值正确但类型并非整数（使用了字符串形式），被视为部分妥协格式要求"})
            total_score += 15
        else:
            score_details.append({"item": "校验 BLK_SIZE_BYTES 准确性", "score": 0, "max_score": 30, "passed": False, "reason": f"内存块大小错误。获取到: {blk_val}。这可能是受到了其他 dump 文件干扰假数据的影响，或指针映射提取逻辑错误"})
    else:
        score_details.append({"item": "校验 BLK_SIZE_BYTES 准确性", "score": 0, "max_score": 30, "passed": False, "reason": "缺少 BLK_SIZE_BYTES 数据或数据格式错误"})

    # 写入最终结果
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({
            "total_score": total_score,
            "details": score_details
        }, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
