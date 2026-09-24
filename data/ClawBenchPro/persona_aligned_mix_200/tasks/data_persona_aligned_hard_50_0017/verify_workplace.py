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
    score_file = os.path.join(workspace, "workplace_score.json")
    target_json_path = os.path.join(workspace, "report", "hacker.json")
    
    details = []
    total_score = 0
    
    # 1. 检查目标目录及文件是否存在 (10分)
    if not os.path.exists(target_json_path):
        details.append({
            "item": "检查目标文件 hacker.json 是否存在", 
            "score": 0, 
            "max_score": 10, 
            "passed": False, 
            "reason": "未找到 report/hacker.json 文件"
        })
        with open(score_file, "w") as f:
            json.dump({"total_score": 0, "details": details}, f, ensure_ascii=False, indent=2)
        return
        
    details.append({
        "item": "检查目标文件 hacker.json 是否存在", 
        "score": 10, 
        "max_score": 10, 
        "passed": True, 
        "reason": "文件已成功生成"
    })
    total_score += 10
    
    # 2. 解析 JSON 结构及严密的键名检查 (20分)
    try:
        with open(target_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        if not isinstance(data, dict):
            raise ValueError("JSON Root 必须是 Object (字典) 类型")
            
        keys = set(data.keys())
        expected_keys = {"hacker_address", "exploit_tx_hash"}
        
        if keys == expected_keys:
            details.append({
                "item": "检查 JSON 格式合法性及必需字段", 
                "score": 20, 
                "max_score": 20, 
                "passed": True, 
                "reason": "完全符合规定的两项精确键名要求，无任何冗余字段"
            })
            total_score += 20
        elif expected_keys.issubset(keys):
            # 存在冗余字段，严重扣分，防止 Agent 幻觉乱塞无关数据
            details.append({
                "item": "检查 JSON 格式合法性及必需字段", 
                "score": 5, 
                "max_score": 20, 
                "passed": False, 
                "reason": f"包含目标键名，但捏造或掺杂了多余字段: {keys - expected_keys}，发生幻觉"
            })
            total_score += 5
        else:
            details.append({
                "item": "检查 JSON 格式合法性及必需字段", 
                "score": 0, 
                "max_score": 20, 
                "passed": False, 
                "reason": f"缺少核心键名。当前包含的键为: {list(keys)}"
            })
            with open(score_file, "w") as f:
                json.dump({"total_score": total_score, "details": details}, f, ensure_ascii=False, indent=2)
            return
            
    except Exception as e:
        details.append({
            "item": "检查 JSON 格式合法性及必需字段", 
            "score": 0, 
            "max_score": 20, 
            "passed": False, 
            "reason": f"JSON 解析崩溃，非纯粹的结构化数据: {str(e)}"
        })
        with open(score_file, "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, ensure_ascii=False, indent=2)
        return

    # 3. 校验黑客地址 hacker_address (35分)
    hacker_addr = str(data.get("hacker_address", "")).strip().lower()
    expected_addr = "0xbadc0ffeebadc0ffeebadc0ffeebadc0ffeebadc".lower()
    
    if hacker_addr == expected_addr:
        details.append({
            "item": "精准提取黑客钱包原始地址", 
            "score": 35, 
            "max_score": 35, 
            "passed": True, 
            "reason": "黑客地址准确无误"
        })
        total_score += 35
    else:
        details.append({
            "item": "精准提取黑客钱包原始地址", 
            "score": 0, 
            "max_score": 35, 
            "passed": False, 
            "reason": f"提取出的黑客地址错误。提取值为: {hacker_addr}"
        })

    # 4. 校验涉事交易哈希 exploit_tx_hash (35分)
    tx_hash = str(data.get("exploit_tx_hash", "")).strip().lower()
    expected_hash = "0xdeadbeef999999999999999999999999999999999999999999999999deadbeef".lower()
    
    if tx_hash == expected_hash:
        details.append({
            "item": "精准锁定重入攻击的致命交易哈希", 
            "score": 35, 
            "max_score": 35, 
            "passed": True, 
            "reason": "攻击交易哈希完全匹配"
        })
        total_score += 35
    else:
        details.append({
            "item": "精准锁定重入攻击的致命交易哈希", 
            "score": 0, 
            "max_score": 35, 
            "passed": False, 
            "reason": f"哈希错误。提取值为: {tx_hash}"
        })

    # 将最终成绩明细写入文件
    with open(score_file, "w") as f:
        json.dump({
            "total_score": total_score,
            "details": details
        }, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    verify()
