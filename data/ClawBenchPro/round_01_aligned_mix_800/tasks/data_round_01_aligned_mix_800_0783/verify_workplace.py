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

def find_number(node):
    """递归遍历 JSON 所有节点，提取其中的数值进行比对，防止嵌套导致无法识别。"""
    numbers = []
    if isinstance(node, dict):
        for k, v in node.items():
            numbers.extend(find_number(v))
    elif isinstance(node, list):
        for i in node:
            numbers.extend(find_number(i))
    elif isinstance(node, (int, float)):
        numbers.append(node)
    elif isinstance(node, str):
        try:
            numbers.append(float(node))
        except ValueError:
            pass
    return numbers

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    file_path = os.path.join(workspace, "deliverables", "ready_volunteers.json")
    
    # 1. 物理探针检查：目标交付物是否存在 (20分)
    if os.path.isfile(file_path):
        score += 20
        details.append({"item": "检查结果文件是否存在", "score": 20, "max_score": 20, "passed": True, "reason": f"文件 {file_path} 存在。"})
    else:
        details.append({"item": "检查结果文件是否存在", "score": 0, "max_score": 20, "passed": False, "reason": f"未找到文件 {file_path}，目录或文件未被正确创建。"})
        with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
            json.dump({"total_score": score, "details": details}, f, indent=2, ensure_ascii=False)
        return

    # 2. 结构验证：检查是否为合法 JSON 且结构正常 (10分)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            data = json.loads(content)
        score += 10
        details.append({"item": "检查文件格式是否为合法JSON", "score": 10, "max_score": 10, "passed": True, "reason": "文件通过 JSON 解析器。"})
    except Exception as e:
        details.append({"item": "检查文件格式是否为合法JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"无法作为合法 JSON 解析: {e}"})
        with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
            json.dump({"total_score": score, "details": details}, f, indent=2, ensure_ascii=False)
        return

    # 3. 核心业务验证：排查人员名单是否正确筛选 (30分)
    # 基于题目中 csv 的人员名单，合格者为：
    # "Alice Trenton" (19, YES), "Diana Prince" (18, YES), "Evan Wright" (17, YES), "Greg House" (50, YES)
    target_people = {"Alice Trenton", "Diana Prince", "Evan Wright", "Greg House"}
    wrong_people = {"Bobby J", "Charlie Davis", "Fiona Gallagher", "Hannah Abbott"}
    
    json_str = json.dumps(data)
    found_targets = [p for p in target_people if p in json_str]
    found_wrongs = [p for p in wrong_people if p in json_str]
    
    people_score = 0
    if len(found_targets) == 4 and len(found_wrongs) == 0:
        people_score = 30
        details.append({"item": "验证批准志愿者名单过滤正确性", "score": 30, "max_score": 30, "passed": True, "reason": "精确包含4名符合条件的人员，没有任何未成年人或未携带环保水瓶的错漏项。"})
    else:
        # 梯度算分：找到对的加 7.5 分，找到错的每个扣 10 分
        people_score += (len(found_targets) * 7.5)
        people_score -= (len(found_wrongs) * 10)
        people_score = max(0, int(people_score)) # 保底 0 分，取整
        details.append({"item": "验证批准志愿者名单过滤正确性", "score": people_score, "max_score": 30, "passed": False, "reason": f"名单不完全准确。应当通过 4 人（实际找到 {len(found_targets)} 人），应当剔除的人中错误包含了 {len(found_wrongs)} 人。"})
    
    score += people_score

    # 4. 精准数值验证：检查总工时 (13小时) (30分)
    # 合格人员的 total combined hours = 4 + 3 + 2 + 4 = 13
    numbers_in_json = find_number(data)
    if 13 in numbers_in_json or 13.0 in numbers_in_json:
        score += 30
        details.append({"item": "检查志愿者的总工时汇总计算结果", "score": 30, "max_score": 30, "passed": True, "reason": "在 JSON 数据中成功提取到计算正确的总工时 13。"})
    else:
        details.append({"item": "检查志愿者的总工时汇总计算结果", "score": 0, "max_score": 30, "passed": False, "reason": f"未在生成结果中找到应有的汇总计算结果 13。提取到的所有数值: {numbers_in_json}"})

    # 5. 混合探针验证：利用大模型判断最终文件数据字段命名语义是否健康 (10分)
    prompt = "Look at this JSON. Structurally, does it clearly contain at least one key indicating 'volunteer names' (like 'names', 'volunteers', 'approved_volunteers') AND one key indicating 'total hours' (like 'total_hours', 'combined_hours', 'hours')? Ensure it reflects both aspects of the requirement."
    llm_ok = llm_judge_content(prompt, content)
    if llm_ok:
        score += 10
        details.append({"item": "利用大模型检查 JSON 结构的业务语义合理性", "score": 10, "max_score": 10, "passed": True, "reason": "大模型判定 JSON 字段命名符合业务需求。"})
    else:
        details.append({"item": "利用大模型检查 JSON 结构的业务语义合理性", "score": 0, "max_score": 10, "passed": False, "reason": "大模型判定 JSON 未能在 key 命名上清晰表达姓名列表与总工时。"})

    # 输出统一评测结果
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({"total_score": score, "details": details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
