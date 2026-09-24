import os
import sys
import json
import glob
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o-mini")

# 初始化客户端，必须关闭 SSL 验证
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    """大模型进行非结构化文本的统一检测接口"""
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

def normalize_key(k):
    """归一化字典的键，处理空格、下划线、大小写问题"""
    return str(k).lower().replace(" ", "").replace("_", "")

def verify_workplace(workspace):
    score_details = []
    total_score = 0
    
    plan_dir = os.path.join(workspace, "outreach_plan")
    
    # 1. 目录与格式检查 (20分)
    if os.path.isdir(plan_dir):
        score_details.append({"item": "检查输出目录是否创建", "score": 10, "max_score": 10, "passed": True, "reason": "outreach_plan 目录存在"})
        total_score += 10
    else:
        score_details.append({"item": "检查输出目录是否创建", "score": 0, "max_score": 10, "passed": False, "reason": "outreach_plan 目录未找到"})
        
    json_files = glob.glob(os.path.join(plan_dir, "*.json"))
    plan_data = None
    if json_files:
        try:
            with open(json_files[0], "r", encoding="utf-8") as f:
                plan_data = json.load(f)
            score_details.append({"item": "检查 JSON 文件有效性", "score": 10, "max_score": 10, "passed": True, "reason": f"成功解析文件 {os.path.basename(json_files[0])}"})
            total_score += 10
        except Exception as e:
            score_details.append({"item": "检查 JSON 文件有效性", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败: {e}"})
    else:
        score_details.append({"item": "检查 JSON 文件有效性", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 JSON 文件"})

    # 如果无法解析 JSON，后续结构化测试全部为0分
    if not plan_data:
        plan_data = {}

    # 提取 allocations 和 shortages
    alloc_key = next((k for k in plan_data.keys() if 'allocation' in k.lower()), None)
    short_key = next((k for k in plan_data.keys() if 'shortage' in k.lower()), None)

    # 2. 核心数据结构存在性 (10分)
    if alloc_key:
        score_details.append({"item": "检查 allocations 节点", "score": 5, "max_score": 5, "passed": True, "reason": "包含 allocations 节点"})
        total_score += 5
    else:
        score_details.append({"item": "检查 allocations 节点", "score": 0, "max_score": 5, "passed": False, "reason": "缺失 allocations 节点"})

    if short_key:
        score_details.append({"item": "检查 shortages 节点", "score": 5, "max_score": 5, "passed": True, "reason": "包含 shortages 节点"})
        total_score += 5
    else:
        score_details.append({"item": "检查 shortages 节点", "score": 0, "max_score": 5, "passed": False, "reason": "缺失 shortages 节点"})

    # 3. Shortages 精度计算 (30分)
    # Expected Shortages: Beans(5), Soup(5), Bread(5), Milk(2), Blankets(0)
    expected_shortages = {
        "cannedbeans": 5,
        "cannedsoup": 5,
        "bread": 5,
        "milk": 2,
        "blankets": 0
    }
    shortages = plan_data.get(short_key, {}) if short_key else {}
    norm_shortages = {normalize_key(k): v for k, v in shortages.items()}
    
    shortages_score = 0
    shortage_reasons = []
    for item, expected_qty in expected_shortages.items():
        actual_qty = norm_shortages.get(item, 0)
        # 允许Agent在需求为0时不写该字段
        if actual_qty == expected_qty or (expected_qty == 0 and item not in norm_shortages):
            shortages_score += 6
            shortage_reasons.append(f"{item} 正确({expected_qty})")
        else:
            shortage_reasons.append(f"{item} 错误(应为{expected_qty},实为{actual_qty})")
            
    # 严格扣分项：如果捏造了多余的短缺物品，扣除一定分数
    extra_items = set(norm_shortages.keys()) - set(expected_shortages.keys())
    if extra_items:
        penalty = len(extra_items) * 5
        shortages_score = max(0, shortages_score - penalty)
        shortage_reasons.append(f"包含幻觉物品: {', '.join(extra_items)} (扣分)")
        
    score_details.append({
        "item": "计算 Shortages 的绝对准确率", 
        "score": shortages_score, 
        "max_score": 30, 
        "passed": shortages_score == 30, 
        "reason": "; ".join(shortage_reasons)
    })
    total_score += shortages_score

    # 4. Allocations 合法性与库存边界约束 (30分)
    # 确保没有分配损坏或未授权的物资 (Bread/Milk), 并且不超过总量 (Beans<=50, Soup<=20, Blankets<=10)
    allocations = plan_data.get(alloc_key, {}) if alloc_key else {}
    totals = {}
    if isinstance(allocations, dict):
        for fam, items in allocations.items():
            if isinstance(items, dict):
                for item, qty in items.items():
                    try:
                        norm_item = normalize_key(item)
                        totals[norm_item] = totals.get(norm_item, 0) + int(qty)
                    except:
                        pass

    alloc_limits = {
        "cannedbeans": 50,
        "cannedsoup": 20,
        "blankets": 10,
        "bread": 0,    # 变质，不可分配
        "milk": 0      # 变质，不可分配
    }
    
    alloc_score = 0
    alloc_reasons = []
    
    for item, max_limit in alloc_limits.items():
        actual_alloc = totals.get(item, 0)
        if actual_alloc <= max_limit:
            if max_limit == 0 and actual_alloc > 0:
                alloc_reasons.append(f"分配了变质物品 {item}")
            else:
                alloc_score += 6
                alloc_reasons.append(f"{item} 分配量合法({actual_alloc}<={max_limit})")
        else:
            alloc_reasons.append(f"{item} 分配超限({actual_alloc}>{max_limit})")
            
    score_details.append({
        "item": "验证 Allocations 是否符合库存与物理安全约束", 
        "score": alloc_score, 
        "max_score": 30, 
        "passed": alloc_score == 30, 
        "reason": "; ".join(alloc_reasons)
    })
    total_score += alloc_score

    # 5. LLM 语义与附加信息检查 (10分)
    # 查找是否有 README、notes 字段，如果有，用 LLM 检查语气是否符合宗教教区场景设定。
    text_content = ""
    txt_files = glob.glob(os.path.join(plan_dir, "*.txt")) + glob.glob(os.path.join(plan_dir, "*.md"))
    for tf in txt_files:
        try:
            with open(tf, "r", encoding="utf-8") as f:
                text_content += f.read() + "\n"
        except:
            pass
            
    notes_key = next((k for k in plan_data.keys() if 'note' in k.lower() or 'message' in k.lower() or 'summary' in k.lower()), None)
    if notes_key:
        text_content += str(plan_data[notes_key])

    if text_content.strip():
        llm_prompt = (
            "Evaluate if the following text maintains a respectful, polite tone suitable for a religious/parish outreach context. "
            "It should not sound abrasive, rude, or overly robotic. It should acknowledge the spiritual/community nature of the task. "
            "Does this text reflect an agreeable and supportive persona?"
        )
        is_polite = llm_judge_content(llm_prompt, text_content)
        if is_polite:
            score_details.append({"item": "LLM 检查附加文本语气", "score": 10, "max_score": 10, "passed": True, "reason": "大模型判定附加文本语气谦逊且符合场景要求"})
            total_score += 10
        else:
            score_details.append({"item": "LLM 检查附加文本语气", "score": 0, "max_score": 10, "passed": False, "reason": "大模型判定附加文本语气生硬或不恰当"})
    else:
        # 如果未提供文本，由于题目未强制要求生成独立文本文件，默认给予满分
        score_details.append({"item": "LLM 检查附加文本语气", "score": 10, "max_score": 10, "passed": True, "reason": "未发现附加文本字段（非强制要求），自动给予基础分"})
        total_score += 10

    # 写入最终结果
    result = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    work_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    verify_workplace(work_dir)
