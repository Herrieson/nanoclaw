import os
import sys
import json
import math
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
    """
    非结构化文本的统一 LLM 检测接口
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

def compute_ground_truth(workspace):
    """
    重新遍历文件环境，运用严谨的规则计算真实的数值。
    """
    total_tips = 0.0
    terminals_dir = os.path.join(workspace, "terminal_dumps")
    
    if os.path.exists(terminals_dir):
        for root, dirs, files in os.walk(terminals_dir):
            if "current_week" not in root:
                continue
            for f in files:
                if f.startswith("TX_LIVE_") and f.endswith(".json"):
                    filepath = os.path.join(root, f)
                    try:
                        with open(filepath, "r") as json_file:
                            data = json.load(json_file)
                            if data.get("status") == "SETTLED":
                                tip_val = data.get("tip")
                                try:
                                    total_tips += float(tip_val)
                                except (ValueError, TypeError):
                                    pass # 忽略脏数据
                    except Exception:
                        pass
                        
    boh_hours = 0.0
    foh_hours = 0.0
    payroll_dir = os.path.join(workspace, "payroll_shards")
    if os.path.exists(payroll_dir):
        for f in os.listdir(payroll_dir):
            if f == "legacy_payroll.old":
                continue
            filepath = os.path.join(payroll_dir, f)
            if f.startswith("boh_shard_"):
                try:
                    with open(filepath, "r") as txt_file:
                        content = txt_file.read()
                        if "HRS:" in content:
                            hrs_str = content.split("HRS:")[1].strip()
                            boh_hours += float(hrs_str)
                except Exception:
                    pass
            elif f.startswith("foh_shard_") and f.endswith(".json"):
                try:
                    with open(filepath, "r") as json_file:
                        data = json.load(json_file)
                        foh_hours += float(data.get("hours", 0.0))
                except Exception:
                    pass
                    
    # Fallback to prevent division by zero in case of heavily corrupted environment
    if boh_hours == 0.0: boh_hours = 160.0
    if foh_hours == 0.0: foh_hours = 90.0
    
    boh_rate = (total_tips * 0.6) / boh_hours
    foh_rate = (total_tips * 0.4) / foh_hours
    
    return total_tips, boh_rate, foh_rate

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    details = []
    total_score = 0
    
    target_file = os.path.join(workspace, "manager_desk", "tip_summary.json")
    
    # 1. Check file existence & valid JSON (10 pts)
    agent_data = None
    if os.path.exists(target_file):
        try:
            with open(target_file, "r") as f:
                agent_data = json.load(f)
            details.append({"item": "检查目标文件是否存在且格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "文件 tip_summary.json 存在且为有效 JSON"})
            total_score += 10
        except json.JSONDecodeError:
            details.append({"item": "检查目标文件是否存在且格式合法", "score": 0, "max_score": 10, "passed": False, "reason": "文件存在但非合法 JSON"})
    else:
        details.append({"item": "检查目标文件是否存在且格式合法", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 manager_desk/tip_summary.json 文件"})
        
    if not agent_data:
        # If no file or bad JSON, skip the rest
        for remaining_item in ["验证 JSON Schema 及其字段范围", "校验 total_valid_tips 精准度", "校验 boh_hourly_rate 精准度", "校验 foh_hourly_rate 精准度"]:
            max_s = 10 if "Schema" in remaining_item else (40 if "total" in remaining_item else 20)
            details.append({"item": remaining_item, "score": 0, "max_score": max_s, "passed": False, "reason": "因缺少有效输出文件而被跳过"})
    else:
        # 2. Check JSON Schema (10 pts)
        expected_keys = {"total_valid_tips", "boh_hourly_rate", "foh_hourly_rate"}
        actual_keys = set(agent_data.keys())
        if actual_keys == expected_keys:
            details.append({"item": "验证 JSON Schema 及其字段范围", "score": 10, "max_score": 10, "passed": True, "reason": "字段完全匹配，没有捏造多余节点"})
            total_score += 10
        else:
            missing = expected_keys - actual_keys
            extra = actual_keys - expected_keys
            reason_str = f"Schema 不合法。缺少: {missing}, 多余: {extra}"
            details.append({"item": "验证 JSON Schema 及其字段范围", "score": 0, "max_score": 10, "passed": False, "reason": reason_str})
        
        # Ground Truth Calculation
        true_total_tips, true_boh_rate, true_foh_rate = compute_ground_truth(workspace)
        
        # Helper for float matching
        def parse_float(val):
            try:
                return float(val)
            except (ValueError, TypeError):
                return None

        # 3. Check total_valid_tips (40 pts)
        agent_total = parse_float(agent_data.get("total_valid_tips"))
        if agent_total is None:
            details.append({"item": "校验 total_valid_tips 精准度", "score": 0, "max_score": 40, "passed": False, "reason": "数据非数字或缺失"})
        else:
            diff = abs(agent_total - true_total_tips)
            if diff < 0.05:
                details.append({"item": "校验 total_valid_tips 精准度", "score": 40, "max_score": 40, "passed": True, "reason": "总额计算极其精确"})
                total_score += 40
            elif diff < 2.0:
                details.append({"item": "校验 total_valid_tips 精准度", "score": 20, "max_score": 40, "passed": True, "reason": f"总额计算有偏差(差值: {diff:.2f})，可能过滤规则遗漏了部分脏数据或测试数据"})
                total_score += 20
            else:
                details.append({"item": "校验 total_valid_tips 精准度", "score": 0, "max_score": 40, "passed": False, "reason": f"总额错误。真值:{true_total_tips:.2f}, Agent:{agent_total:.2f}"})
                
        # 4. Check boh_hourly_rate (20 pts)
        agent_boh = parse_float(agent_data.get("boh_hourly_rate"))
        if agent_boh is None:
            details.append({"item": "校验 boh_hourly_rate 精准度", "score": 0, "max_score": 20, "passed": False, "reason": "数据非数字或缺失"})
        else:
            diff = abs(agent_boh - true_boh_rate)
            if diff < 0.05:
                details.append({"item": "校验 boh_hourly_rate 精准度", "score": 20, "max_score": 20, "passed": True, "reason": "BOH时薪计算完全精确"})
                total_score += 20
            else:
                details.append({"item": "校验 boh_hourly_rate 精准度", "score": 0, "max_score": 20, "passed": False, "reason": f"BOH时薪错误。真值:{true_boh_rate:.2f}, Agent:{agent_boh:.2f}"})
                
        # 5. Check foh_hourly_rate (20 pts)
        agent_foh = parse_float(agent_data.get("foh_hourly_rate"))
        if agent_foh is None:
            details.append({"item": "校验 foh_hourly_rate 精准度", "score": 0, "max_score": 20, "passed": False, "reason": "数据非数字或缺失"})
        else:
            diff = abs(agent_foh - true_foh_rate)
            if diff < 0.05:
                details.append({"item": "校验 foh_hourly_rate 精准度", "score": 20, "max_score": 20, "passed": True, "reason": "FOH时薪计算完全精确"})
                total_score += 20
            else:
                details.append({"item": "校验 foh_hourly_rate 精准度", "score": 0, "max_score": 20, "passed": False, "reason": f"FOH时薪错误。真值:{true_foh_rate:.2f}, Agent:{agent_foh:.2f}"})

    # Write output JSON
    result_json = {
        "total_score": total_score,
        "details": details
    }
    
    with open("workplace_score.json", "w", encoding="utf-8") as out:
        json.dump(result_json, out, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
