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
    report_path = os.path.join(workspace, "report", "hacker.json")
    
    score = 0
    details = []

    # 1. 检查目标结果文件是否存在 (10分)
    if os.path.exists(report_path) and os.path.isfile(report_path):
        score += 10
        details.append({"item": "检查目标结果文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件 report/hacker.json 存在"})
    else:
        details.append({"item": "检查目标结果文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件 report/hacker.json 不存在"})
        _write_score(workspace, score, details)
        return

    # 2. 验证文件是否为合法的 JSON 格式 (10分)
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            hacker_data = json.load(f)
        score += 10
        details.append({"item": "验证文件是否为合法的 JSON 格式", "score": 10, "max_score": 10, "passed": True, "reason": "成功解析 JSON 格式"})
    except json.JSONDecodeError:
        details.append({"item": "验证文件是否为合法的 JSON 格式", "score": 0, "max_score": 10, "passed": False, "reason": "JSON 解析失败，格式非法"})
        _write_score(workspace, score, details)
        return

    if not isinstance(hacker_data, dict):
        details.append({"item": "验证 JSON 顶层结构是否为字典", "score": 0, "max_score": 10, "passed": False, "reason": "顶层结构不是字典对象"})
        _write_score(workspace, score, details)
        return

    # 3. 验证必需字段完备性及幻觉冗余剔除 (10分)
    expected_keys = {"hacker_address", "exploit_tx_hash", "entity_tag"}
    actual_keys = set(hacker_data.keys())
    if expected_keys.issubset(actual_keys):
        if len(actual_keys) == len(expected_keys):
            score += 10
            details.append({"item": "检查必需字段且无捏造的冗余字段", "score": 10, "max_score": 10, "passed": True, "reason": "包含全部必需的3个字段，且无大模型幻觉捏造的冗余字段"})
        else:
            score += 5
            details.append({"item": "检查必需字段且无捏造的冗余字段", "score": 5, "max_score": 10, "passed": False, "reason": "包含必需字段，但存在非预期的冗余数据字段，扣除一半分数"})
    else:
        details.append({"item": "检查必需字段且无捏造的冗余字段", "score": 0, "max_score": 10, "passed": False, "reason": f"缺失任务要求的关键字段。当前具备的字段：{list(actual_keys)}"})

    # 4. 精准代码解析 - 黑客交易哈希 (20分)
    target_tx_hash = "0xdeadbeef999999999999999999999999999999999999999999999999deadbeef"
    actual_tx_hash = str(hacker_data.get("exploit_tx_hash", "")).strip().lower()
    if actual_tx_hash == target_tx_hash:
        score += 20
        details.append({"item": "精准验证利用重入攻击的交易哈希", "score": 20, "max_score": 20, "passed": True, "reason": "利用攻击交易哈希提取完全正确"})
    else:
        details.append({"item": "精准验证利用重入攻击的交易哈希", "score": 0, "max_score": 20, "passed": False, "reason": f"交易哈希提取错误。期望: {target_tx_hash}, 实际: {actual_tx_hash}"})

    # 5. 精准代码解析 - 黑客钱包地址 (20分)
    target_address = "0xbadc0ffeebadc0ffeebadc0ffeebadc0ffeebadc"
    actual_address = str(hacker_data.get("hacker_address", "")).strip().lower()
    if actual_address == target_address:
        score += 20
        details.append({"item": "精准验证黑客钱包发起地址", "score": 20, "max_score": 20, "passed": True, "reason": "黑客钱包发起地址提取完全正确"})
    else:
        details.append({"item": "精准验证黑客钱包发起地址", "score": 0, "max_score": 20, "passed": False, "reason": f"地址提取错误。实际提取: {actual_address}"})

    # 6. LLM 语义核查 - 实体威胁标签查询有效性 (30分)
    entity_tag_val = str(hacker_data.get("entity_tag", ""))
    if entity_tag_val.strip() == "":
        details.append({"item": "利用大模型检查威胁情报实体标签是否准确", "score": 0, "max_score": 30, "passed": False, "reason": "实体标签字段为空"})
    else:
        prompt_text = "Does the provided text clearly, accurately, and unambiguously identify 'North Korea Lazarus Group' or 'Lazarus Group' as the threat entity?"
        llm_result = llm_judge_content(prompt_text, entity_tag_val)
        if llm_result:
            score += 30
            details.append({"item": "利用大模型检查威胁情报实体标签是否准确", "score": 30, "max_score": 30, "passed": True, "reason": "大模型判定 Agent 成功获取了正确的实体标签（通过备用 API）"})
        else:
            details.append({"item": "利用大模型检查威胁情报实体标签是否准确", "score": 0, "max_score": 30, "passed": False, "reason": f"大模型判定实体标签信息不符，未能正确指出目标组织。Agent给出的值为: {entity_tag_val}"})

    _write_score(workspace, score, details)

def _write_score(workspace, score, details):
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({"total_score": score, "details": details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
