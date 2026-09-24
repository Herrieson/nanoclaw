import os
import sys
import json
import glob
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
    
    details = []
    total_score = 0
    
    # 1. 检查 dossier 目录 (10分)
    dossier_path = os.path.join(workspace, "dossier")
    if os.path.isdir(dossier_path):
        details.append({"item": "检查结果目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录 dossier 存在"})
        total_score += 10
    else:
        details.append({"item": "检查结果目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 dossier 目录"})
        
    # 2. 检查 JSON 文件存在 (20分)
    json_file_path = None
    if os.path.isdir(dossier_path):
        json_files = glob.glob(os.path.join(dossier_path, "*.json"))
        if len(json_files) == 1:
            json_file_path = json_files[0]
            details.append({"item": "检查 dossier 下是否有且仅有一个 JSON 文件", "score": 20, "max_score": 20, "passed": True, "reason": f"找到 JSON 文件: {os.path.basename(json_file_path)}"})
            total_score += 20
        elif len(json_files) > 1:
            json_file_path = json_files[0]
            details.append({"item": "检查 dossier 下是否有且仅有一个 JSON 文件", "score": 10, "max_score": 20, "passed": False, "reason": "找到了多个 JSON 文件，不够整洁"})
            total_score += 10
        else:
            details.append({"item": "检查 dossier 下是否有且仅有一个 JSON 文件", "score": 0, "max_score": 20, "passed": False, "reason": "未找到任何 JSON 文件"})
            
    # 3. 语义检查：文件名是否符合私家侦探的谨慎风格 (10分)
    if json_file_path:
        filename = os.path.basename(json_file_path)
        is_discreet = llm_judge_content(
            "Does the following filename look discreet, professional, and suitable for a covert private investigation? It should not be overly exposed with sensitive intent like 'stolen_funds.json' or 'dirty_money.json'. A neutral or coded name like 'audit_results.json', 'report.json', or 'findings.json' is preferred.",
            filename
        )
        if is_discreet:
            details.append({"item": "检查文件名是否足够隐蔽", "score": 10, "max_score": 10, "passed": True, "reason": "大模型判定文件名符合谨慎规范"})
            total_score += 10
        else:
            details.append({"item": "检查文件名是否足够隐蔽", "score": 0, "max_score": 10, "passed": False, "reason": "大模型判定文件名暴露了敏感意图"})
            
        # 4. JSON 结构校验 (20分)
        parsed_data = None
        try:
            with open(json_file_path, "r", encoding="utf-8") as f:
                parsed_data = json.load(f)
            details.append({"item": "检查 JSON 格式是否合法", "score": 20, "max_score": 20, "passed": True, "reason": "成功解析 JSON 结构"})
            total_score += 20
        except Exception as e:
            details.append({"item": "检查 JSON 格式是否合法", "score": 0, "max_score": 20, "passed": False, "reason": f"JSON 解析失败: {e}"})
            
        # 5 & 6. 精准的数据计算核验 (各20分，共40分)
        # ACC-1001-XYZ 应为: 5400 + 1100 + 500 = 7000
        # ACC-2002-ABC 应为: 8000 + 50 = 8050
        if parsed_data and isinstance(parsed_data, dict):
            # 校验嫌疑人 1
            val1 = parsed_data.get("ACC-1001-XYZ")
            try:
                val1_float = float(val1)
                if abs(val1_float - 7000.0) < 0.01:
                    details.append({"item": "校验 ACC-1001-XYZ 的涉案金额", "score": 20, "max_score": 20, "passed": True, "reason": "金额精确无误 (7000.0)"})
                    total_score += 20
                else:
                    details.append({"item": "校验 ACC-1001-XYZ 的涉案金额", "score": 0, "max_score": 20, "passed": False, "reason": f"计算错误，期望 7000.0，实际得到 {val1_float}"})
            except (TypeError, ValueError):
                details.append({"item": "校验 ACC-1001-XYZ 的涉案金额", "score": 0, "max_score": 20, "passed": False, "reason": "该嫌疑人的金额缺失或并非合法数字格式"})
                
            # 校验嫌疑人 2
            val2 = parsed_data.get("ACC-2002-ABC")
            try:
                val2_float = float(val2)
                if abs(val2_float - 8050.0) < 0.01:
                    details.append({"item": "校验 ACC-2002-ABC 的涉案金额", "score": 20, "max_score": 20, "passed": True, "reason": "金额精确无误 (8050.0)"})
                    total_score += 20
                else:
                    details.append({"item": "校验 ACC-2002-ABC 的涉案金额", "score": 0, "max_score": 20, "passed": False, "reason": f"计算错误，期望 8050.0，实际得到 {val2_float}"})
            except (TypeError, ValueError):
                details.append({"item": "校验 ACC-2002-ABC 的涉案金额", "score": 0, "max_score": 20, "passed": False, "reason": "该嫌疑人的金额缺失或并非合法数字格式"})
                
            # 检查是否捏造了多余的账号 (幻觉检查)
            extra_keys = set(parsed_data.keys()) - {"ACC-1001-XYZ", "ACC-2002-ABC"}
            if extra_keys:
                details.append({"item": "幻觉检查：是否包含非嫌疑名单内的账号", "score": -20, "max_score": 0, "passed": False, "reason": f"发现捏造/无关的账号数据，严重违规。多出: {extra_keys}"})
                total_score = max(0, total_score - 20)
        else:
            # 格式不对无法评分
            pass

    # 写入报告
    report = {
        "total_score": total_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
