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
    # 此函数为检测非结构化文本的统一接口（本题验证主要依靠硬代码，但保留接口防患未然）
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

def get_ground_truth(workspace):
    # 动态计算基准答案
    volunteers_path = os.path.join(workspace, "data", "registry", "volunteers.json")
    revoked_path = os.path.join(workspace, "data", "registry", "revoked_ids.txt")
    records_dir = os.path.join(workspace, "data", "records")
    
    with open(volunteers_path, "r", encoding="utf-8") as f:
        volunteers = json.load(f)
        
    with open(revoked_path, "r", encoding="utf-8") as f:
        revoked = set()
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                revoked.add(line)
                
    usable_count = 0
    scrap_count = 0
    active_volunteers = set()
    
    for root, dirs, files in os.walk(records_dir):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                # Agent 必须妥善处理损坏或后缀不明的文件，忽略无法被 JSON 解析的内容
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                record = json.loads(content)
            except Exception:
                continue
                
            if record.get("event_code") != "OPT-2023-MAIN":
                continue
                
            for donation in record.get("donations", []):
                vid = donation.get("volunteer_id")
                # 必须在志愿者名册中，并且不能被吊销
                if vid not in volunteers or vid in revoked:
                    continue
                    
                condition = donation.get("condition", "").lower()
                is_usable = "usable" in condition or "good" in condition
                is_scrap = "scrap" in condition or "broken" in condition
                
                if is_usable:
                    usable_count += 1
                    active_volunteers.add(volunteers[vid])
                elif is_scrap:
                    scrap_count += 1
                    active_volunteers.add(volunteers[vid])
                    
    return {
        "usable_count": usable_count,
        "scrap_count": scrap_count,
        "verified_volunteers": sorted(list(active_volunteers))
    }

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "deliverables", "final_report.json")
    
    details = []
    total_score = 0
    
    # 检查项 1：文件存在性 (10分)
    if not os.path.exists(report_path):
        details.append({"item": "检查目标文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 deliverables/final_report.json 文件"})
        score_data = {"total_score": 0, "details": details}
        with open("workplace_score.json", "w") as f:
            json.dump(score_data, f, indent=4)
        return
    else:
        details.append({"item": "检查目标文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件 deliverables/final_report.json 存在"})
        total_score += 10
        
    # 检查项 2：JSON 格式及 Key 完整性 (10分)
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            agent_data = json.load(f)
        
        required_keys = {"usable_count", "scrap_count", "verified_volunteers"}
        if not required_keys.issubset(set(agent_data.keys())):
            details.append({"item": "检查结果 JSON 的结构完整性", "score": 0, "max_score": 10, "passed": False, "reason": f"缺失必要的字段，当前字段有: {list(agent_data.keys())}"})
            score_data = {"total_score": total_score, "details": details}
            with open("workplace_score.json", "w") as f:
                json.dump(score_data, f, indent=4)
            return
        else:
            details.append({"item": "检查结果 JSON 的结构完整性", "score": 10, "max_score": 10, "passed": True, "reason": "结果为有效 JSON 且包含所有规定字段"})
            total_score += 10
    except Exception as e:
        details.append({"item": "检查结果 JSON 的结构完整性", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败: {str(e)}"})
        score_data = {"total_score": total_score, "details": details}
        with open("workplace_score.json", "w") as f:
            json.dump(score_data, f, indent=4)
        return
        
    # 获取 Ground Truth
    gt_data = get_ground_truth(workspace)
    
    # 检查项 3：usable_count 的准确性 (25分)
    agent_usable = agent_data.get("usable_count", -1)
    if agent_usable == gt_data["usable_count"]:
        details.append({"item": "验证 usable_count 数值准确性", "score": 25, "max_score": 25, "passed": True, "reason": "可用物品总数统计准确"})
        total_score += 25
    else:
        details.append({"item": "验证 usable_count 数值准确性", "score": 0, "max_score": 25, "passed": False, "reason": f"统计错误。Agent: {agent_usable}, 正确: {gt_data['usable_count']}"})

    # 检查项 4：scrap_count 的准确性 (25分)
    agent_scrap = agent_data.get("scrap_count", -1)
    if agent_scrap == gt_data["scrap_count"]:
        details.append({"item": "验证 scrap_count 数值准确性", "score": 25, "max_score": 25, "passed": True, "reason": "废弃物品总数统计准确"})
        total_score += 25
    else:
        details.append({"item": "验证 scrap_count 数值准确性", "score": 0, "max_score": 25, "passed": False, "reason": f"统计错误。Agent: {agent_scrap}, 正确: {gt_data['scrap_count']}"})

    # 检查项 5：verified_volunteers 提取与去重的准确性 (20分)
    agent_volunteers = agent_data.get("verified_volunteers", [])
    gt_volunteers_set = set(gt_data["verified_volunteers"])
    agent_volunteers_set = set(agent_volunteers)
    
    if gt_volunteers_set == agent_volunteers_set:
        details.append({"item": "验证有效志愿者提取的准确性", "score": 20, "max_score": 20, "passed": True, "reason": "过滤、查表与去重正确"})
        total_score += 20
    else:
        diff_missing = gt_volunteers_set - agent_volunteers_set
        diff_extra = agent_volunteers_set - gt_volunteers_set
        reason_msg = f"志愿者集合不匹配。漏找: {diff_missing}, 多找: {diff_extra}"
        details.append({"item": "验证有效志愿者提取的准确性", "score": 0, "max_score": 20, "passed": False, "reason": reason_msg})

    # 检查项 6：verified_volunteers 字母序排序准确性 (10分)
    # 前提是集合大小不能为 0，且不能全错，否则直接 0 分
    if len(agent_volunteers) > 0 and type(agent_volunteers) == list:
        if agent_volunteers == sorted(agent_volunteers):
            details.append({"item": "验证有效志愿者列表的字母排序", "score": 10, "max_score": 10, "passed": True, "reason": "列表严格遵守了字母顺序排序"})
            total_score += 10
        else:
            details.append({"item": "验证有效志愿者列表的字母排序", "score": 0, "max_score": 10, "passed": False, "reason": "列表未正确排序"})
    else:
        details.append({"item": "验证有效志愿者列表的字母排序", "score": 0, "max_score": 10, "passed": False, "reason": "列表为空或非数组类型，无法评价排序"})

    # 输出结果
    score_data = {"total_score": total_score, "details": details}
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(score_data, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()
