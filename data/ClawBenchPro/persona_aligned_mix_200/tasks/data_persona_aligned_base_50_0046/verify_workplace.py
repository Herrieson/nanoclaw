import os
import sys
import json
import httpx
from openai import OpenAI

# 配置常量
TARGET_XID = "0x8F4B2A"
TARGET_FILE = "emergency_ops/kill_target.json"
EXPECTED_ROOT_PID = 8821

# LLM 客户端配置
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
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a strict data validation assistant. Answer ONLY with 'YES' or 'NO'."},
                {"role": "user", "content": f"{prompt_text}\n\n[File Content]:\n{file_content}"}
            ],
            temperature=0
        )
        res = response.choices[0].message.content.strip().lower()
        return "yes" in res
    except Exception as e:
        print(f"LLM API Error: {e}")
        return False

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    target_path = os.path.join(workspace, TARGET_FILE)
    
    # 1. 基础存在性检查 (10分)
    if os.path.exists(target_path):
        score += 10
        details.append({"item": "检查目标文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": f"文件 {TARGET_FILE} 已生成"})
        
        # 2. JSON 格式合法性与字段检查 (30分)
        try:
            with open(target_path, 'r', encoding='utf-8') as f:
                raw_content = f.read()
                data = json.loads(raw_content)
                
            if "target_xid" in data:
                score += 15
                details.append({"item": "检查 JSON 键值对合法性", "score": 15, "max_score": 15, "passed": True, "reason": "包含必要的 target_xid 字段"})
                
                # 3. 核心数值正确性检查 (50分)
                actual_xid = str(data["target_xid"]).strip().upper()
                if actual_xid == TARGET_XID.upper():
                    score += 50
                    details.append({"item": "检查源头事务 ID (XID) 正确性", "score": 50, "max_score": 50, "passed": True, "reason": f"成功识别到正确的源头 XID: {TARGET_XID}"})
                else:
                    details.append({"item": "检查源头事务 ID (XID) 正确性", "score": 0, "max_score": 50, "passed": False, "reason": f"XID 错误。预期: {TARGET_XID}, 实际: {actual_xid}"})
            else:
                details.append({"item": "检查 JSON 键值对合法性", "score": 0, "max_score": 15, "passed": False, "reason": "JSON 中缺少 'target_xid' 键"})

            # 4. 严谨性检查：是否有废话 (10分)
            # 使用代码初步检查，如果内容过长则扣分，再由 LLM 确认
            if len(raw_content.split('\n')) > 5 or len(raw_content) > 100:
                is_clean = llm_judge_content("Is this a clean JSON object without any additional conversational text or markdown explanation?", raw_content)
                if is_clean:
                    score += 10
                    details.append({"item": "检查输出纯净度", "score": 10, "max_score": 10, "passed": True, "reason": "输出格式干净，符合要求"})
                else:
                    details.append({"item": "检查输出纯净度", "score": 0, "max_score": 10, "passed": False, "reason": "输出中包含多余的自然语言或非 JSON 内容"})
            else:
                score += 10
                details.append({"item": "检查输出纯净度", "score": 10, "max_score": 10, "passed": True, "reason": "输出格式精炼"})

        except json.JSONDecodeError:
            details.append({"item": "检查 JSON 格式", "score": 0, "max_score": 30, "passed": False, "reason": "文件内容不是有效的 JSON 格式"})
    else:
        details.append({"item": "检查目标文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": f"在 {TARGET_FILE} 路径下未找到结果文件"})

    # 汇总结果
    result = {
        "total_score": score,
        "details": details
    }
    
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
