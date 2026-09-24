import os
import sys
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4")

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

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results = []
    total_score = 0
    
    summary_path = os.path.join(workspace, "audit_results", "summary.json")
    
    # 1. 检查目录与文件是否存在 (15 分)
    if os.path.exists(summary_path):
        results.append({
            "item": "检查 summary.json 文件是否存在",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": "成功找到了 audit_results/summary.json"
        })
        total_score += 15
    else:
        results.append({
            "item": "检查 summary.json 文件是否存在",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": "未找到 audit_results/summary.json"
        })
        
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": 0, "details": results}, f, indent=2, ensure_ascii=False)
        return

    # 2. 解析 JSON 并验证格式 (15 分)
    try:
        with open(summary_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        results.append({
            "item": "检查 JSON 格式合法性",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": "JSON 文件可以被成功解析"
        })
        total_score += 15
    except Exception as e:
        results.append({
            "item": "检查 JSON 格式合法性",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": f"JSON 解析失败: {e}"
        })
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": results}, f, indent=2, ensure_ascii=False)
        return

    # 将数据转为字符串以供检索，增加鲁棒性
    data_str = json.dumps(data)

    # 3. 验证失败的 Batch ID 提取 (40 分)
    # 正确的失败列表：B002 (Temp), B004 (Eco), B006 (Temp+Eco), B008 (Eco)
    # B003 应被忽略，其他均 Pass。
    expected_fails = {"B002", "B004", "B006", "B008"}
    found_fails = set()
    for batch_id in ["B001", "B002", "B003", "B004", "B005", "B006", "B007", "B008"]:
        if batch_id in data_str:
            found_fails.add(batch_id)
            
    # 计算得分
    correct_identifications = expected_fails.intersection(found_fails)
    false_positives = found_fails - expected_fails
    
    batch_score = len(correct_identifications) * 10
    batch_score -= len(false_positives) * 10
    batch_score = max(0, min(40, batch_score))
    
    if batch_score == 40:
        reason = "精准找出了所有失败的批次，且没有误报。"
    elif "B003" in found_fails:
        reason = "找出的失败批次有误，且包含了应被忽略的失效反应堆数据 (B003)。"
    else:
        reason = f"失败批次识别不完全或存在误报。期望: {expected_fails}, 实际包含: {found_fails}"

    results.append({
        "item": "验证失败批次 ID 的准确性",
        "score": batch_score,
        "max_score": 40,
        "passed": batch_score == 40,
        "reason": reason
    })
    total_score += batch_score

    # 4. 验证废料计算 (30 分)
    # 正确废料计算：所有有效批次 (排除 B003) 的 (total_weight - output_weight)
    # B001: 50, B002: 60, B004: 100, B005: 50, B006: 50, B007: 10, B008: 100
    # 总计 = 420。 如果包含 B003(20) 则为 440。
    
    # 动态在 JSON 所有 value 中寻找 420 或 440
    values_str = str(data.values()) if isinstance(data, dict) else data_str
    
    if "420" in values_str:
        waste_score = 30
        waste_reason = "废料总计算精确无误 (420 kg)。"
    elif "440" in values_str:
        waste_score = 10
        waste_reason = "计算了废料，但未剔除被停用的反应堆数据 (B003)，导致结果为 440 kg。"
    else:
        # LLM 辅助检查是否有近似废料的描述
        with open(summary_path, "r", encoding="utf-8") as f:
            content = f.read()
        llm_check = llm_judge_content("Does this JSON explicitly state the total waste is exactly 420 or 420.0?", content)
        if llm_check:
            waste_score = 30
            waste_reason = "代码未匹配到数值，但大模型确认包含正确的废料值 (420)。"
        else:
            waste_score = 0
            waste_reason = "未能找到正确的废料总和数据 (应为 420)。"

    results.append({
        "item": "验证总废料计算",
        "score": waste_score,
        "max_score": 30,
        "passed": waste_score == 30,
        "reason": waste_reason
    })
    total_score += waste_score

    # 写入最终成绩
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({
            "total_score": total_score,
            "details": results
        }, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
