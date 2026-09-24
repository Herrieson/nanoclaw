import os
import sys
import json
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
    """大模型进行非结构化语境判定"""
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

def extract_all_numbers(obj):
    """
    递归扁平化提取JSON中所有的数值，不论何种schema都能捕获，
    这可防止依赖于特定key命名的脆弱正则匹配，符合防御性编程原则。
    """
    nums = []
    if isinstance(obj, dict):
        for v in obj.values():
            nums.extend(extract_all_numbers(v))
    elif isinstance(obj, list):
        for item in obj:
            nums.extend(extract_all_numbers(item))
    elif isinstance(obj, (int, float)):
        nums.append(float(obj))
    elif isinstance(obj, str):
        try:
            nums.append(float(obj))
        except ValueError:
            pass
    return nums

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    details = []
    total_score = 0
    
    plans_dir = os.path.join(workspace, "plans")
    json_path = os.path.join(plans_dir, "budget_and_materials_summary.json")
    
    # [梯度验证项 1] 检查目标目录结构 (10分)
    if os.path.isdir(plans_dir):
        details.append({"item": "检查计划目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录 plans 成功创建"})
        total_score += 10
    else:
        details.append({"item": "检查计划目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "目录 plans 不存在"})
        
    # [梯度验证项 2] 检查目标文件格式及读取能力 (10分)
    json_data = None
    json_content = ""
    if os.path.isfile(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                json_content = f.read()
                json_data = json.loads(json_content)
            details.append({"item": "检查目标文件是否为合法JSON", "score": 10, "max_score": 10, "passed": True, "reason": "成功解析 budget_and_materials_summary.json"})
            total_score += 10
        except json.JSONDecodeError:
            details.append({"item": "检查目标文件是否为合法JSON", "score": 0, "max_score": 10, "passed": False, "reason": "JSON格式错误，无法通过原生 json 库解析，可能是幻觉了 Markdown 代码块"})
    else:
        details.append({"item": "检查目标文件是否为合法JSON", "score": 0, "max_score": 10, "passed": False, "reason": "目标文件不存在"})
        
    # 如果文件合法，进行深入的内容原生探测
    if json_data is not None:
        nums = extract_all_numbers(json_data)
        
        # [梯度验证项 3] 检查账单逻辑提取计算的精准性 (30分)
        # 户外花费 = 120.50 (Boots) + 15.25 (Trail Mix) + 85.0 (Tent) + 40.0 (Spray) = 260.75
        if 260.75 in nums:
            details.append({"item": "检查户外开销汇总的精准性", "score": 30, "max_score": 30, "passed": True, "reason": "从JSON中精准找到了正确合并计算后的总户外花费 260.75"})
            total_score += 30
        elif 135.75 in nums and 125.0 in nums:
            details.append({"item": "检查户外开销汇总的精准性", "score": 15, "max_score": 30, "passed": False, "reason": "未找到大一统总和 260.75，但找到了准确按 Hiking/Camping 拆分的计算结果 135.75 和 125.0"})
            total_score += 15
        else:
            details.append({"item": "检查户外开销汇总的精准性", "score": 0, "max_score": 30, "passed": False, "reason": "未在提取出的数值集合中找到正确的花费数字，可能逻辑过滤错误"})
            
        # [梯度验证项 4] 检查可用好木材数量统计的精准性，同时检测是否混淆损坏物 (30分)
        # 应有的好木材: Oak:4, Pine:5, Cedar:2, Maple:1
        # 容易犯的错误: 把坏木材当好木材算入，坏木材数: Oak:2 (总6), Pine:6 (总11)
        wood_score = 0
        wood_target = [4.0, 5.0, 2.0, 1.0]
        found_targets = [t for t in wood_target if t in nums]
        wood_reason = ""
        
        if len(found_targets) == 4:
            wood_score += 20
            wood_reason = "成功找到了四种好木材相应的准确数量(4, 5, 2, 1)。"
        else:
            wood_score += len(found_targets) * 5
            wood_reason = f"仅找到部分好木材对应数量: {found_targets}，可能有遗漏。"
            
        # 绝对防御：如果混入了坏木材，或者做了错误的累加求和，属于逻辑严重谬误
        if 6.0 in nums or 11.0 in nums:
            wood_reason += " 警告：在提取的数字中检测到了损坏木材数或错误求和值(6 或 11)，未严格区分 Condition，扣 10 分。"
        else:
            wood_score += 10
            wood_reason += " 且数据过滤极其干净，未混入损坏木材数，处理逻辑满分。"
            
        details.append({"item": "检查木材过滤和数量统计的精准性", "score": wood_score, "max_score": 30, "passed": wood_score == 30, "reason": wood_reason})
        total_score += wood_score
        
        # [梯度验证项 5] LLM 语义与语境要求检查 (20分)
        # 业务要求: "Please, just give it to me straight." (只想要直白的数据结果，不要安抚或冗长无关废话)
        prompt_text = (
            "The user is an anxious carpenter who requested a straight-to-the-point JSON summary of his "
            "outdoor expenses and GOOD wood count. Check if the provided JSON content is STRICTLY answering this, "
            "with direct, understandable keys (e.g. 'outdoor_expenses', 'oak', 'pine'), WITHOUT generating "
            "unnecessary extra categories, long unsolicited comforting messages, or overly complicated nested objects. "
            "Answer YES if it is clean and straightforward. Answer NO if it contains hallucinated extra data or overly verbose structures."
        )
        passed_llm = llm_judge_content(prompt_text, json_content)
        if passed_llm:
            details.append({"item": "大模型检查生成结果的语境直白度及无冗余性", "score": 20, "max_score": 20, "passed": True, "reason": "大模型判定内容符合焦虑木匠对直白简洁的诉求，无强行安慰与无用层级。"})
            total_score += 20
        else:
            details.append({"item": "大模型检查生成结果的语境直白度及无冗余性", "score": 0, "max_score": 20, "passed": False, "reason": "大模型判定内容包含捏造的多余类别、不必要的废话安抚或过度复杂的结构。"})
            
    else:
        # 没有正确生成文件，后续内容项直接清零
        details.append({"item": "检查户外开销汇总的精准性", "score": 0, "max_score": 30, "passed": False, "reason": "缺少JSON文件无法验证内容"})
        details.append({"item": "检查木材过滤和数量统计的精准性", "score": 0, "max_score": 30, "passed": False, "reason": "缺少JSON文件无法验证内容"})
        details.append({"item": "大模型检查生成结果的语境直白度及无冗余性", "score": 0, "max_score": 20, "passed": False, "reason": "缺少JSON文件无法验证内容"})
        
    result = {
        "total_score": total_score,
        "details": details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
