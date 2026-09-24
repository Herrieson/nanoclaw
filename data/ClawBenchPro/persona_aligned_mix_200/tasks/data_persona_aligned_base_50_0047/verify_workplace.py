import os
import sys
import json
import httpx
from openai import OpenAI

# 核心配置
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
    """用于检测非结构化文本的统一接口"""
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
    report_path = os.path.join(workspace, "report/freeze_request.json")
    
    score = 0
    details = []

    # 1. 检查文件是否存在及格式是否为合法的 JSON (20分)
    if not os.path.exists(report_path):
        details.append({"item": "检查结果文件是否存在", "score": 0, "max_score": 20, "passed": False, "reason": "未找到 report/freeze_request.json"})
    else:
        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            score += 20
            details.append({"item": "检查结果文件及格式", "score": 20, "max_score": 20, "passed": True, "reason": "文件存在且为合法JSON"})
            
            # 2. 检查攻击交易哈希 (40分)
            expected_tx = "0xdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
            actual_tx = data.get("attacker_tx", "").strip().lower()
            if actual_tx == expected_tx:
                score += 40
                details.append({"item": "验证攻击者交易哈希", "score": 40, "max_score": 40, "passed": True, "reason": "交易哈希匹配正确"})
            else:
                details.append({"item": "验证攻击者交易哈希", "score": 0, "max_score": 40, "passed": False, "reason": f"交易哈希错误，期望值开头为0xdead...，实际值为 {actual_tx}"})

            # 3. 检查盗取金额 (40分)
            # 10 ETH + 10 ETH = 20 ETH = 20000000000000000000 Wei
            expected_wei = "20000000000000000000"
            actual_wei = str(data.get("stolen_wei", "")).strip()
            if actual_wei == expected_wei:
                score += 40
                details.append({"item": "验证被盗金额(Wei)", "score": 40, "max_score": 40, "passed": True, "reason": "金额计算精确匹配（20 ETH）"})
            else:
                # 检查是否只算了单次攻击 (10 ETH)
                if actual_wei == "10000000000000000000":
                    score += 15
                    details.append({"item": "验证被盗金额(Wei)", "score": 15, "max_score": 40, "passed": False, "reason": "金额错误：仅计算了单层调用，未发现嵌套重入的累计金额"})
                else:
                    details.append({"item": "验证被盗金额(Wei)", "score": 0, "max_score": 40, "passed": False, "reason": f"金额计算错误，期望 {expected_wei}, 实际 {actual_wei}"})

            # 4. 严查字段冗余 (防止作弊混入大量字段让脚本盲搜)
            if len(data.keys()) > 2:
                deduction = 10
                score = max(0, score - deduction)
                details.append({"item": "字段精简度检查", "score": -deduction, "max_score": 0, "passed": False, "reason": "JSON包含多余字段，不符合币安风控API严格对接规范"})

        except json.JSONDecodeError:
            details.append({"item": "检查结果文件格式", "score": 0, "max_score": 20, "passed": False, "reason": "文件内容不是合法的JSON"})
        except Exception as e:
            details.append({"item": "运行异常", "score": 0, "max_score": 0, "passed": False, "reason": str(e)})

    # 输出最终评分
    result = {
        "total_score": score,
        "details": details
    }
    with open("workplace_score.json", "w", encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
