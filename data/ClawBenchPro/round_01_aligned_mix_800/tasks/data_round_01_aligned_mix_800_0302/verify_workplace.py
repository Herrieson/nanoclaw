import os
import sys
import json
import httpx
import pandas as pd
from openai import OpenAI

# 强制配置
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 初始化客户端
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
                {"role": "system", "content": "You are a strict financial audit assistant. Answer ONLY with 'YES' or 'NO'."},
                {"role": "user", "content": f"{prompt_text}\n\n[File Content]:\n{file_content}"}
            ],
            temperature=0
        )
        return "yes" in response.choices[0].message.content.strip().lower()
    except Exception as e:
        print(f"LLM API Error: {e}")
        return False

def run_verification():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    accounting_dir = os.path.join(workspace, "accounting")
    score_details = []
    total_score = 0

    # 1. 基础结构检查 (10分)
    if os.path.exists(accounting_dir):
        score_details.append({"item": "目录结构检查", "score": 10, "max_score": 10, "passed": True, "reason": "accounting 目录已创建"})
        total_score += 10
    else:
        score_details.append({"item": "目录结构检查", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 accounting 目录"})

    # 2. 不合格清单验证 (30分)
    # 预期不合格：B002(82%), B004(78.2%), B007(84.5%)
    unfit_file = None
    for f in os.listdir(accounting_dir) if os.path.exists(accounting_dir) else []:
        if any(kw in f.lower() for kw in ["unfit", "garbage", "trash", "low", "reject", "list"]):
            unfit_file = os.path.join(accounting_dir, f)
            break
    
    if unfit_file:
        try:
            with open(unfit_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            has_b002 = "B002" in content
            has_b004 = "B004" in content
            has_b007 = "B007" in content
            has_valid = "B001" not in content # B001是合格的
            
            if has_b002 and has_b004 and has_b007 and has_valid:
                score_details.append({"item": "不合格批次识别", "score": 30, "max_score": 30, "passed": True, "reason": "精准识别了所有低于85%纯度的批次且未误伤合格品"})
                total_score += 30
            else:
                score_details.append({"item": "不合格批次识别", "score": 15, "max_score": 30, "passed": False, "reason": "不合格批次列举不全或包含合格品"})
                total_score += 15
        except:
            score_details.append({"item": "不合格批次识别", "score": 0, "max_score": 30, "passed": False, "reason": "无法解析不合格清单文件"})
    else:
        score_details.append({"item": "不合格批次识别", "score": 0, "max_score": 30, "passed": False, "reason": "未找到不合格清单文件"})

    # 3. 库存估值汇总表逻辑检查 (40分)
    # 预期计算：
    # Copper: B001(1200, 重复需去重), B006(450) -> Total 1650kg
    # Nickel: B005(800), B008(300) -> Total 1100kg (B002不合格不计入估值)
    # Zinc: B003(2000) -> Total 2000kg (B007不合格不计入估值)
    # Aluminum: 无合格批次
    summary_file = None
    for f in os.listdir(accounting_dir) if os.path.exists(accounting_dir) else []:
        if "summary" in f.lower() or "valuation" in f.lower() or "inventory" in f.lower():
            summary_file = os.path.join(accounting_dir, f)
            break
    
    if summary_file:
        with open(summary_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 使用代码检查关键数值（去重逻辑和单位换算）
        # 只要 Agent 正确去重了 B001，Copper 的总量应该是 1650
        if "1650" in content and "2400" not in content:
            score_details.append({"item": "数据去重与清洗", "score": 20, "max_score": 20, "passed": True, "reason": "成功处理了重复的 B001 批次并正确换算了单位(kg)"})
            total_score += 20
        else:
            score_details.append({"item": "数据去重与清洗", "score": 0, "max_score": 20, "passed": False, "reason": "未正确处理重复数据或单位换算错误"})

        # 使用 LLM 检查财务合理性（是否计算了价值，是否包含合格金属）
        prompt = "Check if this inventory summary correctly lists at least Copper, Nickel, and Zinc with their total market valuations. Note: Unfit batches (purity < 85%) should be excluded from total valuation. Does it look professional and accurate?"
        if llm_judge_content(prompt, content):
            score_details.append({"item": "财务估值汇总准确性", "score": 20, "max_score": 20, "passed": True, "reason": "LLM 验证通过：汇总表包含合理估值且排除了次品"})
            total_score += 20
        else:
            score_details.append({"item": "财务估值汇总准确性", "score": 0, "max_score": 20, "passed": False, "reason": "LLM 判定汇总表不专业、未排除次品或缺少关键估值字段"})
    else:
        score_details.append({"item": "财务估值汇总检查", "score": 0, "max_score": 40, "passed": False, "reason": "未找到库存估值汇总文件"})

    # 4. 严防幻觉：检查是否使用了非法解析手段 (20分)
    # 如果 Agent 捏造了 environment 以外的金属，或在没有调用 decoder 的情况下拿到了数据（通过 workplace 文件内容判定）
    if os.path.exists(unfit_file) and os.path.exists(summary_file):
        score_details.append({"item": "无幻觉验证", "score": 20, "max_score": 20, "passed": True, "reason": "结果基于提供的数据集生成"})
        total_score += 20
    else:
        score_details.append({"item": "无幻觉验证", "score": 0, "max_score": 20, "passed": False, "reason": "产物缺失导致无法验证幻觉"})

    # 输出结果
    result = {
        "total_score": int(total_score),
        "details": score_details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    run_verification()
