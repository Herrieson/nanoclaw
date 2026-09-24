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

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "deliverables", "refund_report.json")
    score_file_path = os.path.join(workspace, "workplace_score.json")
    
    details = []
    total_score = 0
    
    # 1. 检查物理文件是否存在 (10分)
    if os.path.exists(report_path):
        details.append({"item": "检查 deliverables/refund_report.json 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "报告文件存在"})
        total_score += 10
    else:
        details.append({"item": "检查 deliverables/refund_report.json 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "报告文件不存在"})
        with open(score_file_path, "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": details}, f, ensure_ascii=False, indent=2)
        return

    # 2. 检查 JSON 格式的严格合法性 (10分)
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        details.append({"item": "验证 JSON 格式合法性", "score": 10, "max_score": 10, "passed": True, "reason": "成功解析标准的 JSON 结构"})
        total_score += 10
    except Exception as e:
        details.append({"item": "验证 JSON 格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败: {e}"})
        with open(score_file_path, "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": details}, f, ensure_ascii=False, indent=2)
        return

    # 3. 验证账号字典全集的准确性与幻觉抵御 (15分)
    expected_keys = {"ACC-7001", "ACC-7002", "ACC-8801", "ACC-8802", "ACC-8803", "ACC-9005", "ACC-9006", "total"}
    actual_keys = set(data.keys())
    missing_keys = expected_keys - actual_keys
    extra_keys = actual_keys - expected_keys

    if not missing_keys and not extra_keys:
        details.append({"item": "验证账号集合的准确性与幻觉抵御", "score": 15, "max_score": 15, "passed": True, "reason": "正确提取了所有账户，无遗漏且未捏造多余/废弃节点"})
        total_score += 15
    else:
        reason_parts = []
        if missing_keys: reason_parts.append(f"遗漏: {missing_keys}")
        if extra_keys: reason_parts.append(f"捏造/未过滤杂质(幻觉): {extra_keys}")
        details.append({"item": "验证账号集合的准确性与幻觉抵御", "score": 0, "max_score": 15, "passed": False, "reason": "; ".join(reason_parts)})

    # 4. 验证 Multi-hop 跨文件映射与叠加业务计算 (20分)
    # ACC-7001 ($300): 来自 GUID-9921，5.5h (>$100) + "gallery" (+$200)
    # ACC-7002 ($250): 来自 GUID-4482，2h (=$50) + "sculpture" (+$200)
    score_4 = 0
    reason_4 = []
    val_7001 = data.get("ACC-7001")
    val_7002 = data.get("ACC-7002")
    if val_7001 == 300: score_4 += 10
    else: reason_4.append(f"ACC-7001金额错误(应为300，实际{val_7001})")
    
    if val_7002 == 250: score_4 += 10
    else: reason_4.append(f"ACC-7002金额错误(应为250，实际{val_7002})")

    details.append({"item": "验证 Multi-hop 元数据映射与关键词叠加组合计算 (ACC-7001, ACC-7002)", "score": score_4, "max_score": 20, "passed": score_4 == 20, "reason": "计算正确" if score_4 == 20 else "; ".join(reason_4)})
    total_score += score_4

    # 5. 验证工时时长判定与特定业务词汇加成规则 (20分)
    # ACC-8802 ($300): 6.0h (>$100) + "exhibition" (+$200)
    # ACC-9005 ($250): 3.5h (=$50) + "painting" (+$200)
    score_5 = 0
    reason_5 = []
    val_8802 = data.get("ACC-8802")
    val_9005 = data.get("ACC-9005")
    if val_8802 == 300: score_5 += 10
    else: reason_5.append(f"ACC-8802金额错误(应为300，实际{val_8802})")
    
    if val_9005 == 250: score_5 += 10
    else: reason_5.append(f"ACC-9005金额错误(应为250，实际{val_9005})")

    details.append({"item": "验证工时时长判定与特定词汇加成提取 (ACC-8802, ACC-9005)", "score": score_5, "max_score": 20, "passed": score_5 == 20, "reason": "计算正确" if score_5 == 20 else "; ".join(reason_5)})
    total_score += score_5

    # 6. 验证基础补偿规则与纯时长计算 (15分)
    # ACC-8801 ($50): 1.5h (=$50)
    # ACC-8803 ($50): 0.5h (=$50)
    # ACC-9006 ($100): 12.0h (>$100)
    score_6 = 0
    reason_6 = []
    val_8801 = data.get("ACC-8801")
    val_8803 = data.get("ACC-8803")
    val_9006 = data.get("ACC-9006")
    
    if val_8801 == 50: score_6 += 5
    else: reason_6.append(f"ACC-8801错误(实际{val_8801})")
    if val_8803 == 50: score_6 += 5
    else: reason_6.append(f"ACC-8803错误(实际{val_8803})")
    if val_9006 == 100: score_6 += 5
    else: reason_6.append(f"ACC-9006错误(实际{val_9006})")

    details.append({"item": "验证基础补偿规则与简单时长计算 (ACC-8801, ACC-8803, ACC-9006)", "score": score_6, "max_score": 15, "passed": score_6 == 15, "reason": "计算正确" if score_6 == 15 else "; ".join(reason_6)})
    total_score += score_6

    # 7. 验证最终金额汇总计算 (10分)
    val_total = data.get("total")
    if val_total == 1300:
        details.append({"item": "验证最终汇总总金额计算 (total)", "score": 10, "max_score": 10, "passed": True, "reason": "Total汇总金额计算正确(1300)"})
        total_score += 10
    else:
        details.append({"item": "验证最终汇总总金额计算 (total)", "score": 0, "max_score": 10, "passed": False, "reason": f"Total汇总错误(应为1300，实际{val_total})"})

    with open(score_file_path, "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": details}, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
