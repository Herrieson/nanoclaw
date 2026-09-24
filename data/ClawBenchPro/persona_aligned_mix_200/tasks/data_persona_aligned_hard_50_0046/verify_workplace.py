import os
import sys
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 初始化客户端，强制关闭 SSL 验证
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    """用于处理非结构化/包含干扰文本的容错解析"""
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
    target_file = os.path.join(workspace, "emergency_ops", "kill_target.json")

    total_score = 0
    details = []

    # 1. 检查物理文件存在性 (15分)
    if os.path.exists(target_file):
        total_score += 15
        details.append({
            "item": "物理文件存在性检查", 
            "score": 15, "max_score": 15, 
            "passed": True, 
            "reason": "目标文件 emergency_ops/kill_target.json 存在"
        })
    else:
        details.append({
            "item": "物理文件存在性检查", 
            "score": 0, "max_score": 15, 
            "passed": False, 
            "reason": "未找到 emergency_ops/kill_target.json 文件"
        })
        # 文件不存在直接输出全 0 记录并退出
        details.extend([
            {"item": "JSON格式合法性", "score": 0, "max_score": 15, "passed": False, "reason": "文件缺失，无法验证"},
            {"item": "格式纯净度(无幻觉/多余节点)", "score": 0, "max_score": 20, "passed": False, "reason": "文件缺失，无法验证"},
            {"item": "核心结果准确度(XID提取)", "score": 0, "max_score": 50, "passed": False, "reason": "文件缺失，无法验证"}
        ])
        write_score(total_score, details)
        return

    # 2. 核心结构化验证
    with open(target_file, "r", encoding="utf-8") as f:
        content = f.read().strip()
    
    try:
        data = json.loads(content)
        # JSON 格式严格合法 (15分)
        total_score += 15
        details.append({
            "item": "JSON格式合法性", 
            "score": 15, "max_score": 15, 
            "passed": True, 
            "reason": "内容是合法的标准 JSON，无外部 Markdown 包装等脏数据"
        })
        
        # 字段纯净度检测 (20分) - 严查捏造/冗余
        keys = list(data.keys())
        if len(keys) == 1 and keys[0] == "target_xid":
            total_score += 20
            details.append({
                "item": "格式纯净度(无幻觉/多余节点)", 
                "score": 20, "max_score": 20, 
                "passed": True, 
                "reason": "严格遵守 Schema，仅存在单点键 target_xid"
            })
        else:
            details.append({
                "item": "格式纯净度(无幻觉/多余节点)", 
                "score": 0, "max_score": 20, 
                "passed": False, 
                "reason": f"未遵循纯净规范，存在多余或错误字段: {keys}"
            })
            
        # 结果精确度检测 (50分) - 核心答案验证
        target_val = data.get("target_xid", "")
        if str(target_val).strip() == "0x8F4B2A":
            total_score += 50
            details.append({
                "item": "核心结果准确度(XID提取)", 
                "score": 50, "max_score": 50, 
                "passed": True, 
                "reason": "精确匹配出底层的隐藏事务 ID 0x8F4B2A"
            })
        else:
            details.append({
                "item": "核心结果准确度(XID提取)", 
                "score": 0, "max_score": 50, 
                "passed": False, 
                "reason": f"XID 计算错误，提取的值为: {target_val}"
            })

    except json.JSONDecodeError:
        # 格式错误时的防线：使用大模型探针进行容错捞分
        details.append({
            "item": "JSON格式合法性", 
            "score": 0, "max_score": 15, 
            "passed": False, 
            "reason": "原生 JSON 解析失败，文件中可能混杂了 Markdown 字符或注释废话"
        })
        details.append({
            "item": "格式纯净度(无幻觉/多余节点)", 
            "score": 0, "max_score": 20, 
            "passed": False, 
            "reason": "JSON 无法解析，无法进行纯净度验证"
        })
        
        # 借助 LLM 提取自然语言文本中的核心意图
        prompt = "Analyze the text and determine if the user has ultimately identified the hex string '0x8F4B2A' as the target transaction ID (target_xid). It must be an exact match for the ID. Respond with 'YES' if they did, and 'NO' if they did not or if they identified a different ID."
        
        if llm_judge_content(prompt, content):
            total_score += 20
            details.append({
                "item": "核心结果准确度(大模型容错匹配)", 
                "score": 20, "max_score": 50, 
                "passed": False, 
                "reason": "虽未能遵循纯净 JSON 格式，但大模型检测到文本内提到了正确的 XID，给予 20 分挽回同情分"
            })
        else:
            details.append({
                "item": "核心结果准确度(大模型容错匹配)", 
                "score": 0, "max_score": 50, 
                "passed": False, 
                "reason": "格式错误，且大模型判定文件内未传递出正确的 0x8F4B2A 信息"
            })

    write_score(total_score, details)

def write_score(total_score, details):
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(
            {"total_score": total_score, "details": details}, 
            f, 
            ensure_ascii=False, 
            indent=2
        )

if __name__ == "__main__":
    verify()
