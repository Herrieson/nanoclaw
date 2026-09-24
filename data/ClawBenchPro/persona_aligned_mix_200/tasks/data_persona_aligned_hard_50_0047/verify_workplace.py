import os
import sys
import json
import httpx
from openai import OpenAI

# =====================================================================
# 强制 API 规范 (LLM 裁判辅助探测)
# =====================================================================
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
    此函数为检测非结构化文本的统一接口。
    在本任务中，主要用于防范特异性作弊或解析某些带有严重自然语言幻觉的输出。
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

# =====================================================================
# 主检查逻辑
# =====================================================================
def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_file = os.path.join(workspace, "report/freeze_request.json")
    
    total_score = 0
    details = []

    # 1. 检查目标文件是否存在 (10分)
    if os.path.exists(report_file):
        total_score += 10
        details.append({"item": "检查目标风控请求文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件 report/freeze_request.json 存在"})
    else:
        details.append({"item": "检查目标风控请求文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 report/freeze_request.json"})
        write_result(total_score, details, workspace)
        return

    # 2. 检查 JSON 合法性 (10分)
    try:
        with open(report_file, "r", encoding="utf-8") as f:
            content_str = f.read()
            data = json.loads(content_str)
        total_score += 10
        details.append({"item": "检查文件是否为合法 JSON 格式", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 解析成功"})
    except Exception as e:
        details.append({"item": "检查文件是否为合法 JSON 格式", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败，包含非标准字符或语法错误: {e}"})
        write_result(total_score, details, workspace)
        return

    # 3. 检查字段格式的严谨性 (10分)
    expected_keys = {"attacker_tx", "stolen_wei"}
    actual_keys = set(data.keys())
    
    if expected_keys.issubset(actual_keys):
        if actual_keys == expected_keys:
            total_score += 10
            details.append({"item": "检查 JSON 字段规范", "score": 10, "max_score": 10, "passed": True, "reason": "有且仅有要求的风控字段"})
        else:
            total_score += 5
            details.append({"item": "检查 JSON 字段规范", "score": 5, "max_score": 10, "passed": False, "reason": f"包含了风控 API 拒绝的多余字段: {actual_keys - expected_keys}"})
    else:
        details.append({"item": "检查 JSON 字段规范", "score": 0, "max_score": 10, "passed": False, "reason": f"缺失关键风控字段: {expected_keys - actual_keys}"})
        # 缺失字段后续检测无意义
        if "attacker_tx" not in actual_keys:
            write_result(total_score, details, workspace)
            return

    # 4. 精确检测攻击交易 Hash (40分)
    target_tx = "0xdeadbeef888888888888888888888888888888888888888888888888deadbeef"
    fake_attack_tx = "0x1111111111111111111111111111111111111111111111111111111111111111"
    reverted_attack_tx = "0x2222222222222222222222222222222222222222222222222222222222222222"
    normal_withdraw_tx = "0x3333333333333333333333333333333333333333333333333333333333333333"
    
    attacker_tx = str(data.get("attacker_tx", "")).strip().lower()
    
    if attacker_tx == target_tx:
        total_score += 40
        details.append({"item": "验证真正的攻击交易 Hash", "score": 40, "max_score": 40, "passed": True, "reason": "精准锁定对 v3 成功发起重入攻击的交易"})
    elif attacker_tx == fake_attack_tx:
        details.append({"item": "验证真正的攻击交易 Hash", "score": 0, "max_score": 40, "passed": False, "reason": "致命错误！提取的是假金库 (v2) 的重入攻击，未正确分析部署日志中 v3 的真实地址"})
    elif attacker_tx == reverted_attack_tx:
        details.append({"item": "验证真正的攻击交易 Hash", "score": 0, "max_score": 40, "passed": False, "reason": "致命错误！找成了被以太坊虚拟机 Revert 的失败攻击，未验证 json 顶层的 status 字段"})
    elif attacker_tx == normal_withdraw_tx:
        details.append({"item": "验证真正的攻击交易 Hash", "score": 0, "max_score": 40, "passed": False, "reason": "严重错误！找成了正常的大额提款，未能从 trace json 中用代码识别出重入攻击的调用树嵌套特征"})
    else:
        details.append({"item": "验证真正的攻击交易 Hash", "score": 0, "max_score": 40, "passed": False, "reason": f"未能找到有效的交易 Hash: {attacker_tx}"})

    # 5. 精确检测被盗金额 (30分)
    # 目标值：22000000000000000000 (十进制格式)
    target_wei_dec = "22000000000000000000"
    target_wei_hex = hex(int(target_wei_dec)) # 0x13180c58e80d400000
    single_call_wei = "5500000000000000000"   # 单次 5.5 ETH

    stolen_wei = str(data.get("stolen_wei", "")).strip().lower()
    
    if stolen_wei == target_wei_dec:
        total_score += 30
        details.append({"item": "验证被盗金额与格式", "score": 30, "max_score": 30, "passed": True, "reason": "完美！递归汇总了所有盗窃节点的总和，且输出为严格的十进制字符串"})
    elif stolen_wei == target_wei_hex:
        total_score += 15
        details.append({"item": "验证被盗金额与格式", "score": 15, "max_score": 30, "passed": False, "reason": "数值正确，但是使用了十六进制，违反了风控系统'十进制纯数字字符串'的要求"})
    elif stolen_wei == single_call_wei or stolen_wei == hex(int(single_call_wei)):
        total_score += 0
        details.append({"item": "验证被盗金额与格式", "score": 0, "max_score": 30, "passed": False, "reason": "计算逻辑错误！只解析了嵌套调用中的第一层金额，没有递归汇总所有恶意吐出的资金"})
    else:
        details.append({"item": "验证被盗金额与格式", "score": 0, "max_score": 30, "passed": False, "reason": f"数值计算完全错误或包含非法字符: {stolen_wei}"})

    # 6. (补充) 防幻觉防作弊校验，对非法值的自然语言进行 LLM 甄别
    # 防止 Agent 将 `stolen_wei` 瞎写成 "The stolen wei is about 22 ETH" 这种无法强转但带有目标数字的诡异表达。
    if not stolen_wei.isdigit() and "22" in stolen_wei and total_score < 100:
        is_natural_lang = llm_judge_content(
            "Does the following file content contain natural language sentences or explanations instead of just a raw JSON dictionary?", 
            content_str
        )
        if is_natural_lang:
            total_score = max(0, total_score - 15)
            details.append({"item": "LLM 反幻觉与作弊惩罚", "score": -15, "max_score": 0, "passed": False, "reason": "Agent 输出了包含自然语言解释的废话JSON文件，破坏了强风控系统的标准解析，被 LLM 裁判驳回。"})

    write_result(total_score, details, workspace)

def write_result(total_score, details, workspace):
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
