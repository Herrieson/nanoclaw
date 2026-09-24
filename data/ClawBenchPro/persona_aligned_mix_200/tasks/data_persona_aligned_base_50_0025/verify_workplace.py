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
    target_file = os.path.join(workspace, "risk_control", "blacklist.json")
    
    score = 0
    details = []
    
    # 1. 检查目标目录及文件是否存在 (10 分)
    if os.path.exists(target_file):
        score += 10
        details.append({"item": "检查目标文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "risk_control/blacklist.json 存在"})
    else:
        details.append({"item": "检查目标文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 risk_control/blacklist.json"})
        with open("workplace_score.json", "w", encoding="utf-8") as f:
            json.dump({"total_score": score, "details": details}, f, ensure_ascii=False, indent=2)
        return

    # 2. 检查 JSON 格式合法性 (15 分)
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        score += 15
        details.append({"item": "检查 JSON 格式合法性", "score": 15, "max_score": 15, "passed": True, "reason": "成功解析为合法 JSON 格式"})
    except Exception as e:
        details.append({"item": "检查 JSON 格式合法性", "score": 0, "max_score": 15, "passed": False, "reason": f"JSON 解析失败: {e}"})
        with open("workplace_score.json", "w", encoding="utf-8") as f:
            json.dump({"total_score": score, "details": details}, f, ensure_ascii=False, indent=2)
        return

    # 确保根节点是字典
    if not isinstance(data, dict):
        details.append({"item": "检查 JSON 根节点类型", "score": 0, "max_score": 75, "passed": False, "reason": "JSON 根节点必须是对象(字典)"})
        with open("workplace_score.json", "w", encoding="utf-8") as f:
            json.dump({"total_score": score, "details": details}, f, ensure_ascii=False, indent=2)
        return
        
    # 定位并验证键名 (大小写不敏感，但必须是正确的 FIX 字段)
    clordid_key = None
    sender_key = None
    for k in data.keys():
        kl = k.lower()
        if kl == "clordid":
            clordid_key = k
        elif kl == "sendercompid":
            sender_key = k

    # 3. 验证 ClOrdID 键 (10 分)
    if clordid_key:
        score += 10
        details.append({"item": "验证 ClOrdID 键是否存在", "score": 10, "max_score": 10, "passed": True, "reason": f"找到规范键名: {clordid_key}"})
    else:
        details.append({"item": "验证 ClOrdID 键是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到符合 ClOrdID 的键名"})

    # 4. 验证 SenderCompID 键 (10 分)
    if sender_key:
        score += 10
        details.append({"item": "验证 SenderCompID 键是否存在", "score": 10, "max_score": 10, "passed": True, "reason": f"找到规范键名: {sender_key}"})
    else:
        details.append({"item": "验证 SenderCompID 键是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到符合 SenderCompID 的键名"})

    # 5. 结构与幻觉检查 (10 分)
    if len(data.keys()) == 2 and clordid_key and sender_key:
        score += 10
        details.append({"item": "验证是否无多余字段 (防幻觉)", "score": 10, "max_score": 10, "passed": True, "reason": "字段数量严格为 2，未捏造多余信息"})
    else:
        details.append({"item": "验证是否无多余字段 (防幻觉)", "score": 0, "max_score": 10, "passed": False, "reason": f"存在多余字段或结构错误，当前包含的键: {list(data.keys())}"})

    # 6. 验证 ClOrdID 数值准确性 (20 分)
    if clordid_key:
        val = str(data[clordid_key]).strip()
        if val == "POISON_HFT_0x9A":
            score += 20
            details.append({"item": "验证 ClOrdID 提取准确性", "score": 20, "max_score": 20, "passed": True, "reason": "ClOrdID 提取准确无误"})
        else:
            details.append({"item": "验证 ClOrdID 提取准确性", "score": 0, "max_score": 20, "passed": False, "reason": f"目标数据提取错误，当前值: {val}"})
    else:
        details.append({"item": "验证 ClOrdID 提取准确性", "score": 0, "max_score": 20, "passed": False, "reason": "因缺少对应键名而跳过判定"})

    # 7. 验证 SenderCompID 数值准确性 (25 分)
    if sender_key:
        val = str(data[sender_key]).strip()
        if val == "MALICIOUS_VIP_88":
            score += 25
            details.append({"item": "验证 SenderCompID 提取准确性", "score": 25, "max_score": 25, "passed": True, "reason": "SenderCompID 提取准确无误"})
        else:
            details.append({"item": "验证 SenderCompID 提取准确性", "score": 0, "max_score": 25, "passed": False, "reason": f"目标数据提取错误，当前值: {val}"})
    else:
        details.append({"item": "验证 SenderCompID 提取准确性", "score": 0, "max_score": 25, "passed": False, "reason": "因缺少对应键名而跳过判定"})

    # 输出最终成绩报告
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({"total_score": score, "details": details}, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
