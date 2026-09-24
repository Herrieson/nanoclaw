import os
import sys
import json
import httpx
from openai import OpenAI

# =======================================================
# 🔒 核心 API 规范：强制读取环境变量并关闭 SSL 验证
# =======================================================
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
    """大模型统一检测非结构化文本的接口"""
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
    target_file = os.path.join(workspace, "risk_control", "blacklist.json")
    
    total_score = 0
    details = []

    # 1. 结构与存在性检查（10分）
    if os.path.exists(target_file):
        details.append({
            "item": "检查风控挂载目录与结果文件存在性", 
            "score": 10, "max_score": 10, "passed": True, 
            "reason": "成功定位到 risk_control/blacklist.json"
        })
        total_score += 10
    else:
        details.append({
            "item": "检查风控挂载目录与结果文件存在性", 
            "score": 0, "max_score": 10, "passed": False, 
            "reason": "未找到 risk_control/blacklist.json，Agent 可能执行失败或未写入指定路径"
        })
        with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2, ensure_ascii=False)
        return
        
    # 2. JSON 格式解析防幻觉校验（10分）
    data = None
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            details.append({
                "item": "解析 JSON 对象确切性", 
                "score": 10, "max_score": 10, "passed": True, 
                "reason": "产物是合法的 JSON 字典对象，风控引擎可安全加载"
            })
            total_score += 10
        else:
            raise ValueError("Parsed JSON is not a Key-Value Dictionary")
    except Exception as e:
        details.append({
            "item": "解析 JSON 对象确切性", 
            "score": 0, "max_score": 10, "passed": False, 
            "reason": f"文件结构非法，无法作为确定性配置读取: {e}"
        })
        with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2, ensure_ascii=False)
        return

    # 提取所有值为字符串供严格比对（严禁模糊正则表达式匹配）
    str_values = [str(v) for v in data.values()]
    
    # 3. 结果脱敏合规校验（20分：一票否决项）
    has_encrypted = any("ENC:" in val for val in str_values)
    if has_encrypted:
        details.append({
            "item": "合规脱敏限制检查", 
            "score": 0, "max_score": 20, "passed": False, 
            "reason": "黑名单报告中残留加密数据(包含 'ENC:')，Agent 敷衍行事或未成功调用 KMS，严重违反风控合规"
        })
    else:
        details.append({
            "item": "合规脱敏限制检查", 
            "score": 20, "max_score": 20, "passed": True, 
            "reason": "未在最终值中发现底层加密密文标签，已净化数据流"
        })
        total_score += 20

    # 4. 精准值域比对 - 恶毒订单流水号 (20分)
    if "POISON_HFT_0x9A" in str_values:
        details.append({
            "item": "提取毒药订单流水号 (ClOrdID)", 
            "score": 20, "max_score": 20, "passed": True, 
            "reason": "精确检索并写入了由于压差倒挂导致的真实订单流水号 POISON_HFT_0x9A"
        })
        total_score += 20
    else:
        details.append({
            "item": "提取毒药订单流水号 (ClOrdID)", 
            "score": 0, "max_score": 20, "passed": False, 
            "reason": "字典中未能精准匹配到恶意订单的流水号 POISON_HFT_0x9A，跨文件关联检索失败"
        })

    # 5. 精准值域比对 - KMS 解密后的真实机构名 (30分)
    if "MALICIOUS_VIP_88" in str_values:
        details.append({
            "item": "验证真实涉事机构 (SenderCompID)", 
            "score": 30, "max_score": 30, "passed": True, 
            "reason": "精准定位密文、调用 KMS 服务、提取返回 JSON 并写入了真实的机构名 MALICIOUS_VIP_88"
        })
        total_score += 30
    else:
        details.append({
            "item": "验证真实涉事机构 (SenderCompID)", 
            "score": 0, "max_score": 30, "passed": False, 
            "reason": "字典中缺少真实解密后的机构名 MALICIOUS_VIP_88，工具链路中断"
        })

    # 6. 利用大模型辅助审查非结构化键名语义 (10分)
    keys_str = ", ".join(data.keys())
    prompt = "Do these JSON keys semantically represent 'ClOrdID' and 'SenderCompID' based on the FIX protocol (case-insensitive, minor abbreviations are acceptable)?"
    
    if llm_judge_content(prompt, keys_str):
        details.append({
            "item": "大模型校验键名 FIX 协议语义", 
            "score": 10, "max_score": 10, "passed": True, 
            "reason": f"大模型确认键名组合 [{keys_str}] 符合 FIX 业务术语规范，风控系统可识别"
        })
        total_score += 10
    else:
        details.append({
            "item": "大模型校验键名 FIX 协议语义", 
            "score": 0, "max_score": 10, "passed": False, 
            "reason": f"大模型认为生成的键名 [{keys_str}] 没有准确采用 ClOrdID/SenderCompID 相关的风控业务命名格式"
        })

    # 将评分结果写回工作区
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({
            "total_score": total_score,
            "details": details
        }, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
