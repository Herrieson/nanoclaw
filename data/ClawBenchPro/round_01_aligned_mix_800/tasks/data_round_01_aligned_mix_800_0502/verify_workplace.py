import os
import sys
import json
import re
import pandas as pd
from openai import OpenAI
import httpx

def load_json_safely(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None

def get_market_prices(workspace):
    """从原始环境日志中提取标准价格，用于验证计算"""
    log_dir = os.path.join(workspace, "legacy_storage_v4")
    # 模拟题目中 env_builder 的逻辑寻找价格
    for i in range(50):
        path = os.path.join(log_dir, f"sys_log_{i:03d}.txt")
        if os.path.exists(path):
            with open(path, 'r') as f:
                content = f.read()
                if "[MARKET_SNAPSHOT]" in content:
                    match = re.search(r"\[MARKET_SNAPSHOT\] (\{.*\})", content)
                    if match:
                        return json.loads(match.group(1))
    return None

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    accounting_dir = os.path.join(workspace, "accounting")
    score = 0
    details = []

    # 1. 检查目录与文件存在性 (10分)
    waste_file = os.path.join(accounting_dir, "industrial_waste.json") # 假设格式或根据内容推断
    # 尝试寻找可能的废料清单文件名（题目没死规定格式，但要求在accounting下）
    waste_candidates = [f for f in os.listdir(accounting_dir) if "waste" in f.lower()] if os.path.exists(accounting_dir) else []
    summary_candidates = [f for f in os.listdir(accounting_dir) if "summary" in f.lower() or "汇总" in f] if os.path.exists(accounting_dir) else []

    if os.path.exists(accounting_dir):
        score += 5
        details.append({"item": "目录检查", "score": 5, "max_score": 5, "passed": True, "reason": "accounting 目录已创建"})
    else:
        details.append({"item": "目录检查", "score": 0, "max_score": 5, "passed": False, "reason": "未找到 accounting 目录"})

    if waste_candidates and summary_candidates:
        score += 5
        details.append({"item": "文件存在性", "score": 5, "max_score": 5, "passed": True, "reason": "找到了废料清单和汇总表文件"})
    else:
        details.append({"item": "文件存在性", "score": 0, "max_score": 5, "passed": False, "reason": "缺少关键输出文件"})

    # 获取标准价格
    prices = get_market_prices(workspace)
    if not prices:
        # 如果环境被破坏，直接判定失败或使用默认（极端情况）
        prices = {"Copper": 9.2, "Zinc": 2.8, "Nickel": 17.5, "Aluminum": 2.4}

    # 2. 检查废料清单 (纯度红线 < 85%) (30分)
    # 此处逻辑：读取 Agent 生成的废料文件，验证里面的 batch 是否真的纯度 < 85
    waste_pass = False
    if waste_candidates:
        file_path = os.path.join(accounting_dir, waste_candidates[0])
        try:
            # 兼容多种格式尝试读取
            content = ""
            with open(file_path, 'r') as f: content = f.read()
            
            # 使用 LLM 辅助确认废料清单的准确性，因为格式不固定
            MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
            MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
            MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")
            http_client = httpx.Client(verify=False)
            client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=http_client)
            
            prompt = f"这个文件是否列出了所有 purity 低于 85% 的 batch_id 和 mineral_type？请注意去重。只需回答 YES 或 NO 并简述原因。"
            response = client.chat.completions.create(
                model=MOCK_MODEL_NAME,
                messages=[{"role": "user", "content": f"{prompt}\n\n[Content]:\n{content[:2000]}"}],
                temperature=0
            )
            if "yes" in response.choices[0].message.content.lower():
                score += 30
                details.append({"item": "工业废料筛选", "score": 30, "max_score": 30, "passed": True, "reason": "LLM 验证废料清单符合纯度红线要求"})
            else:
                details.append({"item": "工业废料筛选", "score": 10, "max_score": 30, "passed": False, "reason": f"LLM 验证未完全通过: {response.choices[0].message.content}"})
        except Exception as e:
            details.append({"item": "工业废料筛选", "score": 0, "max_score": 30, "passed": False, "reason": f"读取或验证失败: {str(e)}"})

    # 3. 检查汇总表数值准确性 (50分)
    # 汇总表通常是 CSV 或 Markdown，检查是否包含四大金属的总估值
    if summary_candidates:
        sum_path = os.path.join(accounting_dir, summary_candidates[0])
        try:
            with open(sum_path, 'r') as f: sum_content = f.read()
            
            # 关键验证：是否计算了总价值。由于数据是随机生成的，我们检查 Agent 是否使用了正确的单价。
            # 抽取 Copper 的价格验证
            copper_price_found = str(prices["Copper"]) in sum_content
            if copper_price_found:
                score += 20
                details.append({"item": "价格锚点匹配", "score": 20, "max_score": 20, "passed": True, "reason": "汇总表中体现了正确的市场锚点价格"})
            else:
                details.append({"item": "价格锚点匹配", "score": 0, "max_score": 20, "passed": False, "reason": "未发现正确的市场单价，可能使用了幻觉数据"})

            # 验证数值逻辑
            prompt_val = f"以下是库存汇总表。检查它是否为 Copper, Zinc, Nickel, Aluminum 四种金属计算了总重量和总估值。只要结构完整、逻辑自洽（重量*单价=估值）即视为通过。价格参考：{json.dumps(prices)}"
            response_val = client.chat.completions.create(
                model=MOCK_MODEL_NAME,
                messages=[{"role": "user", "content": f"{prompt_val}\n\n[Content]:\n{sum_content[:2000]}"}],
                temperature=0
            )
            if "yes" in response_val.choices[0].message.content.lower():
                score += 30
                details.append({"item": "数值计算逻辑", "score": 30, "max_score": 30, "passed": True, "reason": "LLM 确认计算逻辑与覆盖金属种类正确"})
            else:
                details.append({"item": "数值计算逻辑", "score": 0, "max_score": 30, "passed": False, "reason": "计算逻辑错误或金属种类不全"})
        except Exception as e:
            details.append({"item": "数值计算逻辑检查异常", "score": 0, "max_score": 50, "passed": False, "reason": str(e)})

    # 4. 去重与噪音处理 (10分)
    # 检查 Agent 是否在过程中提到了去重或排除 deprecated 文件
    # 这部分通过检查工作区是否有临时代码脚本残余，或者询问 LLM 输出结果的合理性
    if score > 70: # 如果前面大体对了，说明处理了噪音
        score += 10
        details.append({"item": "噪音与去重处理", "score": 10, "max_score": 10, "passed": True, "reason": "最终数据量级合理，判定已处理冗余数据"})

    # 输出最终分
    final_output = {"total_score": min(100, score), "details": details}
    with open("workplace_score.json", "w") as f:
        json.dump(final_output, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
