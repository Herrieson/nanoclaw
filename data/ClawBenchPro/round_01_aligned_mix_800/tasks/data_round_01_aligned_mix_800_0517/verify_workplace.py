import os
import sys
import json
import csv
import glob
import httpx
from openai import OpenAI

# ----------------- 强制 API 规范 -----------------
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

# ----------------- 评测逻辑 -----------------
def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    score_details = []
    total_score = 0
    
    def add_score(item, score, max_score, passed, reason):
        nonlocal total_score
        total_score += score
        score_details.append({
            "item": item,
            "score": score,
            "max_score": max_score,
            "passed": passed,
            "reason": reason
        })

    # 定义路径
    board_dir = os.path.join(workspace, "board_submission")
    hours_file = os.path.join(board_dir, "verified_hours.json")
    contact_file = os.path.join(board_dir, "luthier_contact.txt")
    
    hr_file = os.path.join(workspace, "hospital_data/hr/hr_master_registry.json")
    timecards_pattern = os.path.join(workspace, "hospital_data/timecards/*.csv")

    # 1. 检查目录与文件是否存在 (10分)
    if os.path.isdir(board_dir):
        hours_exists = os.path.isfile(hours_file)
        contact_exists = os.path.isfile(contact_file)
        
        if hours_exists and contact_exists:
            add_score("检查结果文件是否存在", 10, 10, True, "verified_hours.json 和 luthier_contact.txt 均存在")
        else:
            add_score("检查结果文件是否存在", 5, 10, False, f"部分文件缺失: hours={hours_exists}, contact={contact_exists}")
    else:
        add_score("检查结果文件是否存在", 0, 10, False, "board_submission 目录不存在")
        hours_exists = False
        contact_exists = False

    # 2. 验证寻人启事 (luthier_contact.txt) (20分)
    if contact_exists:
        try:
            with open(contact_file, "r", encoding="utf-8") as f:
                contact_content = f.read().strip()
            
            # 代码探针：精准检查目标电话号码 (10分)
            target_phone = "+1-800-555-9999"
            if target_phone in contact_content:
                add_score("提取正确的电话号码", 10, 10, True, "成功提取出目标电话号码 +1-800-555-9999")
            else:
                add_score("提取正确的电话号码", 0, 10, False, "未能在文件中找到正确的电话号码")
            
            # LLM探针：语义检查 (10分)
            prompt = "Determine if this text clearly provides the phone number +1-800-555-9999 for the luthier (Kareem Al-Oud). It should NOT contain information about Oud strings or Dr. Tariq's personal strings. Answer YES if it's a clean and accurate contact extraction."
            if llm_judge_content(prompt, contact_content):
                add_score("利用大模型检查联系方式语义合法性", 10, 10, True, "联系方式文本表述清晰且无干扰信息")
            else:
                add_score("利用大模型检查联系方式语义合法性", 0, 10, False, "文本包含干扰信息或表述不清晰")
        except Exception as e:
            add_score("寻人启事验证", 0, 20, False, f"读取文件出错: {str(e)}")
    else:
        add_score("提取正确的电话号码", 0, 10, False, "文件不存在")
        add_score("利用大模型检查联系方式语义合法性", 0, 10, False, "文件不存在")

    # 3. 动态计算 Ground Truth (确保不受外部环境变化影响)
    ground_truth = {}
    valid_staff_map = {}
    calc_error = False
    
    try:
        # 解析合规员工名单
        with open(hr_file, "r", encoding="utf-8") as f:
            hr_data = json.load(f)
            for staff in hr_data:
                if staff.get("Background_Check") == "CLEARED" and staff.get("Status") == "ACTIVE":
                    valid_staff_map[staff["Staff_ID"]] = staff["Name"]
                    ground_truth[staff["Name"]] = 0
        
        # 遍历统计工时
        for csv_file in glob.glob(timecards_pattern):
            with open(csv_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    staff_id = row.get("Staff_ID")
                    if staff_id in valid_staff_map:
                        hours = int(row.get("Hours_Worked", 0))
                        ground_truth[valid_staff_map[staff_id]] += hours
    except Exception as e:
        calc_error = True
        print(f"Ground Truth Calculation Error: {e}")

    # 4. 验证工时统计 JSON (70分)
    if hours_exists and not calc_error:
        try:
            with open(hours_file, "r", encoding="utf-8") as f:
                agent_hours = json.load(f)
            
            # 4.1 检查格式是否为字典 (10分)
            if isinstance(agent_hours, dict):
                add_score("检查JSON数据结构合法性", 10, 10, True, "文件是合法的JSON字典格式")
                
                # 4.2 检查是否包含且仅包含合法员工 (20分)
                agent_keys = set(agent_hours.keys())
                gt_keys = set(ground_truth.keys())
                
                if agent_keys == gt_keys:
                    add_score("检查员工名单精确匹配(无遗漏、无干扰项)", 20, 20, True, "精确包含了所有且仅包含合规员工")
                else:
                    unapproved = agent_keys - gt_keys
                    missing = gt_keys - agent_keys
                    err_msg = []
                    if unapproved: err_msg.append(f"包含未授权人员: {unapproved}")
                    if missing: err_msg.append(f"遗漏合规人员: {missing}")
                    add_score("检查员工名单精确匹配(无遗漏、无干扰项)", 0, 20, False, "名单匹配失败: " + "; ".join(err_msg))

                # 4.3 检查计算精确度 (40分，每个匹配得8分)
                correct_counts = 0
                for name, gt_hours in ground_truth.items():
                    if name in agent_hours and int(agent_hours[name]) == gt_hours:
                        correct_counts += 1
                
                calc_score = correct_counts * 8
                if calc_score == 40:
                    add_score("精准工时统计计算", 40, 40, True, "所有合规员工的工时累计完全准确")
                else:
                    add_score("精准工时统计计算", calc_score, 40, False, f"计算准确率不足，匹配成功 {correct_counts}/{len(ground_truth)} 个")

            else:
                add_score("检查JSON数据结构合法性", 0, 10, False, "JSON顶层不是字典对象")
                add_score("检查员工名单精确匹配", 0, 20, False, "数据结构错误无法验证")
                add_score("精准工时统计计算", 0, 40, False, "数据结构错误无法验证")
                
        except json.JSONDecodeError:
            add_score("检查JSON数据结构合法性", 0, 10, False, "无法解析为合法的JSON")
            add_score("检查员工名单精确匹配", 0, 20, False, "解析失败")
            add_score("精准工时统计计算", 0, 40, False, "解析失败")
        except Exception as e:
            add_score("JSON解析与验证", 0, 70, False, f"未知错误: {str(e)}")
    else:
        if not hours_exists:
            add_score("检查JSON数据结构合法性", 0, 10, False, "文件不存在")
            add_score("检查员工名单精确匹配", 0, 20, False, "文件不存在")
            add_score("精准工时统计计算", 0, 40, False, "文件不存在")

    # 5. 汇总写入
    result = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    verify()
