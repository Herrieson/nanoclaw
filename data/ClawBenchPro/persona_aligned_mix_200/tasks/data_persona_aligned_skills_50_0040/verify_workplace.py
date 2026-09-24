import os
import sys
import json
import httpx
from openai import OpenAI

# ========================================================
# 🔒 强制 API 规范：LLM-as-a-Judge 配置与 SSL 关闭
# ========================================================
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
    大模型判决接口（统一标准防幻觉）
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

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "reports", "bottleneck.json")
    
    details = []
    total_score = 0
    
    # 1. 物理目录与文件结构检查 (10分)
    file_exists = os.path.exists(report_path)
    if file_exists:
        details.append({"item": "检查目标文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "reports/bottleneck.json 已经成功生成"})
        total_score += 10
    else:
        details.append({"item": "检查目标文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "缺失目标产物文件 reports/bottleneck.json"})
        
    if not file_exists:
        _write_score(workspace, total_score, details)
        return

    # 2. 原生代码强制验证：格式合法性 (20分)
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        details.append({"item": "检查文件内容是否为合法的 JSON", "score": 20, "max_score": 20, "passed": True, "reason": "成功反序列化 JSON，非字符串混编"})
        total_score += 20
    except Exception as e:
        details.append({"item": "检查文件内容是否为合法的 JSON", "score": 0, "max_score": 20, "passed": False, "reason": f"JSON 解析失败（存在格式损坏或 Markdown 外层包裹）: {e}"})
        _write_score(workspace, total_score, details)
        return
        
    # 3. 严格 Schema 防幻觉探测 (20分)
    # 不允许包含任何除 entity_id 和 block_size 以外的字段，否则判定为大模型发散幻觉
    if isinstance(data, dict):
        allowed_keys = {"entity_id", "block_size"}
        actual_keys = set(data.keys())
        extra_keys = actual_keys - allowed_keys
        missing_keys = allowed_keys - actual_keys
        
        if len(extra_keys) == 0 and len(missing_keys) == 0:
            details.append({"item": "严格校验 Schema：无幻觉多余字段", "score": 20, "max_score": 20, "passed": True, "reason": "精确包含两个期望的键，无冗余捏造数据"})
            total_score += 20
        else:
            reason_msg = f"Schema 违规。"
            if extra_keys: reason_msg += f"捏造了多余字段 {extra_keys}。"
            if missing_keys: reason_msg += f"缺少必填字段 {missing_keys}。"
            details.append({"item": "严格校验 Schema：无幻觉多余字段", "score": 0, "max_score": 20, "passed": False, "reason": reason_msg})
    else:
        details.append({"item": "严格校验 Schema：无幻觉多余字段", "score": 0, "max_score": 20, "passed": False, "reason": "JSON 根节点不是 Dict/Object 类型"})

    # 4. 精准结果计算检验：Entity ID (25分)
    # 考察是否从海量异构日志的干扰项里精准锁定了唯一的 "Sys_Physics_Collision" 的 Entity
    entity_id = data.get("entity_id", "")
    if str(entity_id).lower() == "0x7c9a":
        details.append({"item": "精准验证 entity_id", "score": 25, "max_score": 25, "passed": True, "reason": "抗干扰成功，提取到真正的罪魁祸首实体 ID"})
        total_score += 25
    else:
        details.append({"item": "精准验证 entity_id", "score": 0, "max_score": 25, "passed": False, "reason": f"找错了故障点，被渲染或AI子系统的假高耗时诱骗，提取值: {entity_id}"})
        
    # 5. 二次工具依赖的结果检验：Block Size (25分)
    # 考察是否拿着由实体推导的 PTR 正确调用了云端工具
    block_size = data.get("block_size")
    if str(block_size) == "16384":
        details.append({"item": "精准验证 block_size", "score": 25, "max_score": 25, "passed": True, "reason": "成功利用 Cloud Skill 反解析出物理级内存分配大小"})
        total_score += 25
    else:
        details.append({"item": "精准验证 block_size", "score": 0, "max_score": 25, "passed": False, "reason": f"未有效使用云端反解工具或提供了错误的指针，当前值：{block_size}"})

    _write_score(workspace, total_score, details)

def _write_score(workspace, total_score, details):
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w", encoding="utf-8") as f:
        json.dump({
            "total_score": total_score,
            "details": details
        }, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
