import os
import sys
import json
import httpx
from openai import OpenAI

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

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "reports", "market_plan.json")
    
    score_details = []
    total_score = 0
    
    # 1. 结构与文件存在性检查 (10分)
    file_exists = os.path.exists(report_path)
    if file_exists:
        score_details.append({"item": "检查目标文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "找到了 market_plan.json 文件"})
        total_score += 10
    else:
        score_details.append({"item": "检查目标文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 market_plan.json 文件"})
        
    report_data = None
    if file_exists:
        # 2. JSON格式合法性检查 (10分)
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                content = f.read()
                report_data = json.loads(content)
            score_details.append({"item": "检查 JSON 格式合法性", "score": 10, "max_score": 10, "passed": True, "reason": "文件是合法的 JSON 格式"})
            total_score += 10
        except json.JSONDecodeError:
            score_details.append({"item": "检查 JSON 格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": "JSON 格式解析失败"})
            content = ""
            
    if report_data:
        # 转换为字符串以便搜索和LLM判定
        report_str = json.dumps(report_data, ensure_ascii=False, indent=2).lower()
        
        # 3. 精确过滤与不合格项剔除检查 (30分)
        # 根据业务逻辑：
        # Local Honey (V-1102, Gold, Exp 2024-06-01) -> 合格
        # Sustainable Oats (V-2201, Silver, Exp 2024-08-20) -> 合格
        # Apples/Berries -> 过期; Soda -> 不合格
        has_honey = "honey" in report_str
        has_oats = "oats" in report_str
        has_apples = "apples" in report_str
        has_soda = "soda" in report_str
        has_berries = "berries" in report_str
        
        if has_honey and has_oats and not any([has_apples, has_soda, has_berries]):
            score_details.append({"item": "精准过滤合格商品", "score": 30, "max_score": 30, "passed": True, "reason": "正确筛选出 Local Honey 和 Sustainable Oats，且没有包含过期/不合格商品"})
            total_score += 30
        else:
            reason_parts = []
            if not has_honey or not has_oats: reason_parts.append("遗漏了合格商品")
            if has_apples or has_soda or has_berries: reason_parts.append("包含了不合格或过期的商品")
            score_details.append({"item": "精准过滤合格商品", "score": 0, "max_score": 30, "passed": False, "reason": "、".join(reason_parts)})

        # 4. 提取与数值验证 (20分)
        # 验证是否正确获取了总价值（或单个物品的正确价格计算）
        # Honey: 10 * 12.0 = 120
        # Oats: 20 * 3.5 = 70
        has_120 = "120" in report_str
        has_70 = "70" in report_str
        has_190 = "190" in report_str # Total
        if has_190 or (has_120 and has_70):
            score_details.append({"item": "商品价值计算", "score": 20, "max_score": 20, "passed": True, "reason": "正确计算并包含了商品的最终价值"})
            total_score += 20
        else:
            score_details.append({"item": "商品价值计算", "score": 0, "max_score": 20, "passed": False, "reason": "未能找到正确的商品价值计算结果 (120, 70 或总额 190)"})

        # 5. 语义级验证：市场指导价内容 (30分)
        # 必须调用了 local_farmer_network_skill 获取市场指导价并反映在 JSON 中
        prompt = "Does this JSON content include references to market guideline prices, local farmer advice, or external market price checks for the items (especially Honey and Oats)? The agent was supposed to append local market prices."
        llm_passed = llm_judge_content(prompt, content)
        if llm_passed:
            score_details.append({"item": "利用大模型检查市场指导价引入", "score": 30, "max_score": 30, "passed": True, "reason": "大模型判定 JSON 结果中包含了本地农户市场的指导价信息"})
            total_score += 30
        else:
            score_details.append({"item": "利用大模型检查市场指导价引入", "score": 0, "max_score": 30, "passed": False, "reason": "大模型判定 JSON 结果未包含有效的本地市场指导价补充信息"})
    else:
        # 文件不存在或非法JSON时，后续项直接 0 分
        score_details.append({"item": "精准过滤合格商品", "score": 0, "max_score": 30, "passed": False, "reason": "缺少合法的 JSON 报告数据"})
        score_details.append({"item": "商品价值计算", "score": 0, "max_score": 20, "passed": False, "reason": "缺少合法的 JSON 报告数据"})
        score_details.append({"item": "利用大模型检查市场指导价引入", "score": 0, "max_score": 30, "passed": False, "reason": "缺少合法的 JSON 报告数据"})

    # 输出结果
    result = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
