import os
import sys
import json
import re
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
    # 此函数为检测非结构化文本的统一接口，防止因为纯文本表述(如英文单词 four)导致假阴性
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

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    deliverables_dir = os.path.join(workspace, "deliverables")
    vip_alerts_file = os.path.join(deliverables_dir, "vip_alerts.json")
    junk_count_file = os.path.join(deliverables_dir, "junk_count.txt")

    score_details = []
    total_score = 0

    # 1. 检查目录是否存在
    if os.path.isdir(deliverables_dir):
        score_details.append({"item": "检查 deliverables 目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录存在"})
        total_score += 10
    else:
        score_details.append({"item": "检查 deliverables 目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "目录不存在"})

    # 2. 检查 vip_alerts.json 结构合法性
    vip_json_valid = False
    json_data = None
    if os.path.isfile(vip_alerts_file):
        try:
            with open(vip_alerts_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            vip_json_valid = True
            score_details.append({"item": "检查 vip_alerts.json 是否合法", "score": 10, "max_score": 10, "passed": True, "reason": "文件为合法的 JSON 格式"})
            total_score += 10
        except Exception as e:
            score_details.append({"item": "检查 vip_alerts.json 是否合法", "score": 0, "max_score": 10, "passed": False, "reason": f"无法解析 JSON: {e}"})
    else:
        score_details.append({"item": "检查 vip_alerts.json 是否合法", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})

    # 3. 检查 vip_alerts.json 数据准确性
    if vip_json_valid and json_data is not None:
        def extract_strings(obj):
            if isinstance(obj, dict):
                res = []
                for k, v in obj.items():
                    res.extend(extract_strings(k))
                    res.extend(extract_strings(v))
                return res
            elif isinstance(obj, list):
                res = []
                for item in obj:
                    res.extend(extract_strings(item))
                return res
            elif isinstance(obj, str):
                return [obj]
            else:
                return [str(obj)]
        
        all_strs = extract_strings(json_data)
        full_text = " ".join(all_strs).lower()

        # Marcus Johnson
        if "marcus johnson" in full_text and "jacket" in full_text:
            score_details.append({"item": "匹配 VIP 1: Marcus Johnson 及其物品", "score": 10, "max_score": 10, "passed": True, "reason": "成功提取 Marcus Johnson 及 Jacket"})
            total_score += 10
        else:
            score_details.append({"item": "匹配 VIP 1: Marcus Johnson 及其物品", "score": 0, "max_score": 10, "passed": False, "reason": "未找到对应的 VIP 1 信息"})

        # Sarah Connor
        if "sarah connor" in full_text and ("watch" in full_text):
            score_details.append({"item": "匹配 VIP 2: Sarah Connor 及其物品", "score": 10, "max_score": 10, "passed": True, "reason": "成功提取 Sarah Connor 及 Watch"})
            total_score += 10
        else:
            score_details.append({"item": "匹配 VIP 2: Sarah Connor 及其物品", "score": 0, "max_score": 10, "passed": False, "reason": "未找到对应的 VIP 2 信息"})

        # Chloe Bennett
        if "chloe bennett" in full_text and "headset" in full_text:
            score_details.append({"item": "匹配 VIP 3: Chloe Bennett 及其物品", "score": 10, "max_score": 10, "passed": True, "reason": "成功提取 Chloe Bennett 及 Headset"})
            total_score += 10
        else:
            score_details.append({"item": "匹配 VIP 3: Chloe Bennett 及其物品", "score": 0, "max_score": 10, "passed": False, "reason": "未找到对应的 VIP 3 信息"})

        # 幻觉审查: 不能有普通人 David Smith 和无关物品
        if "david smith" in full_text or "ring" in full_text:
            score_details.append({"item": "数据幻觉检测: 排除普通人员", "score": 0, "max_score": 10, "passed": False, "reason": "严重错误：错误收录了非 VIP 成员 (David Smith)"})
        else:
            score_details.append({"item": "数据幻觉检测: 排除普通人员", "score": 10, "max_score": 10, "passed": True, "reason": "正确过滤了普通人员，未产生幻觉"})
            total_score += 10
    else:
        score_details.append({"item": "匹配 VIP 1: Marcus Johnson 及其物品", "score": 0, "max_score": 10, "passed": False, "reason": "前置条件失败"})
        score_details.append({"item": "匹配 VIP 2: Sarah Connor 及其物品", "score": 0, "max_score": 10, "passed": False, "reason": "前置条件失败"})
        score_details.append({"item": "匹配 VIP 3: Chloe Bennett 及其物品", "score": 0, "max_score": 10, "passed": False, "reason": "前置条件失败"})
        score_details.append({"item": "数据幻觉检测: 排除普通人员", "score": 0, "max_score": 10, "passed": False, "reason": "前置条件失败"})

    # 4. 检查 junk_count.txt
    if os.path.isfile(junk_count_file):
        score_details.append({"item": "检查 junk_count.txt 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "统计文件存在"})
        total_score += 10
        
        try:
            with open(junk_count_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            # 使用原生匹配结合大模型兜底
            nums = re.findall(r'\b4\b', content)
            if nums and len(re.findall(r'\d+', content)) == 1 and nums[0] == "4":
                score_details.append({"item": "计算 Junk Count", "score": 30, "max_score": 30, "passed": True, "reason": "计算正确，提取到了 4 个无主物品"})
                total_score += 30
            else:
                prompt = "Does the following text indicate that the total number of junk or unowned items is exactly 4 (or 'four')? Answer YES if it clearly states the count is 4, otherwise NO."
                if llm_judge_content(prompt, content):
                    score_details.append({"item": "计算 Junk Count", "score": 30, "max_score": 30, "passed": True, "reason": "LLM语义验证通过：结果为 4"})
                    total_score += 30
                else:
                    score_details.append({"item": "计算 Junk Count", "score": 0, "max_score": 30, "passed": False, "reason": f"计算错误，结果不为4，提取到：{content}"})
        except Exception as e:
            score_details.append({"item": "计算 Junk Count", "score": 0, "max_score": 30, "passed": False, "reason": f"文件读取失败: {e}"})
    else:
        score_details.append({"item": "检查 junk_count.txt 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "统计文件不存在"})
        score_details.append({"item": "计算 Junk Count", "score": 0, "max_score": 30, "passed": False, "reason": "前置条件失败"})

    result = {
        "total_score": total_score,
        "details": score_details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    verify()
