import os
import sys
import json
import httpx
from openai import OpenAI

# =====================================================================
# 强制 API 规范 (本任务主要为结构化数据验证，以下为备用非结构化检查接口)
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

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_file = os.path.join(workspace, "report", "conflict_summary.json")
    
    total_score = 0
    details = []

    # 1. 验证输出文件及其结构 (共 40 分)
    if not os.path.exists(report_file):
        details.append({"item": "检查目标结果文件是否存在", "score": 0, "max_score": 20, "passed": False, "reason": "未找到 report/conflict_summary.json"})
        details.append({"item": "由于缺失核心文件，后续校验中断", "score": 0, "max_score": 80, "passed": False, "reason": "前置条件失败"})
    else:
        details.append({"item": "检查目标结果文件是否存在", "score": 20, "max_score": 20, "passed": True, "reason": "报告文件存在"})
        
        try:
            with open(report_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            details.append({"item": "检查 JSON 文件格式合法性", "score": 20, "max_score": 20, "passed": True, "reason": "JSON 文件可以成功被原生库解析"})
            
            # 2. 验证字段规范和防作弊 (共 20 分)
            required_keys = {"library", "expected_version", "actual_version"}
            actual_keys = set(data.keys())
            
            if required_keys.issubset(actual_keys):
                details.append({"item": "核心键名完整性检查", "score": 20, "max_score": 20, "passed": True, "reason": "包含了要求的全部三个键"})
                
                # 捏造字段一票否决(扣分)机制
                if len(actual_keys) > 3:
                    details.append({"item": "严格Schema校验: 无多余捏造字段", "score": -20, "max_score": 0, "passed": False, "reason": "Agent 输出了要求之外的冗余字段，判定为潜在幻觉或无法遵循严格指示，倒扣20分"})
                    total_score -= 20
                else:
                    details.append({"item": "严格Schema校验: 无多余捏造字段", "score": 0, "max_score": 0, "passed": True, "reason": "未输出冗余字段，Schema精准匹配"})
                    
                # 3. 验证值准确性 (共 40 分)
                # 3.1 库名判定 (10 分)
                library = str(data.get("library", "")).strip()
                if library == "lib_crypto_vault":
                    details.append({"item": "目标库名 library 数据提取精准度", "score": 10, "max_score": 10, "passed": True, "reason": "成功从乱码日志中提取正确的冲突库名"})
                    total_score += 10
                else:
                    details.append({"item": "目标库名 library 数据提取精准度", "score": 0, "max_score": 10, "passed": False, "reason": f"提取错误，期望 'lib_crypto_vault'，实际为 '{library}'"})

                # 3.2 预期版本判定 (15 分)
                expected_version = str(data.get("expected_version", "")).strip()
                if expected_version == "3.0.5":
                    details.append({"item": "预期版本 expected_version 溯源精准度", "score": 15, "max_score": 15, "passed": True, "reason": "成功通过 commit_hash 找到 manifests 并提取准确的 expected_version"})
                    total_score += 15
                else:
                    details.append({"item": "预期版本 expected_version 溯源精准度", "score": 0, "max_score": 15, "passed": False, "reason": f"追溯错误，期望 '3.0.5'，实际为 '{expected_version}'"})

                # 3.3 实际版本判定 (15 分)
                actual_version = str(data.get("actual_version", "")).strip()
                if actual_version == "2.1.0":
                    details.append({"item": "实际版本 actual_version 解析精准度", "score": 15, "max_score": 15, "passed": True, "reason": "成功排除了 ANSI 乱码干扰，找到了导致崩溃的 rogue headers 版本"})
                    total_score += 15
                else:
                    details.append({"item": "实际版本 actual_version 解析精准度", "score": 0, "max_score": 15, "passed": False, "reason": f"提取错误，期望 '2.1.0'，实际为 '{actual_version}'"})

            else:
                missing = required_keys - actual_keys
                details.append({"item": "核心键名完整性检查", "score": 0, "max_score": 20, "passed": False, "reason": f"缺失必需的键名: {missing}"})
                details.append({"item": "跳过值校验", "score": 0, "max_score": 40, "passed": False, "reason": "由于缺少核心键名，跳过值校验"})
                
            total_score += 40 # 基础分(存在20+格式20)
            
        except json.JSONDecodeError as e:
            details.append({"item": "检查 JSON 文件格式合法性", "score": 0, "max_score": 20, "passed": False, "reason": f"JSON解析失败: {str(e)}"})
            details.append({"item": "跳过后续校验", "score": 0, "max_score": 60, "passed": False, "reason": "文件格式损毁，无法继续"})
            total_score += 20 # 文件存在的分数
            
    # 防止因惩罚机制导致总分跌破0分
    total_score = max(0, min(100, total_score))

    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({
            "total_score": total_score,
            "details": details
        }, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
