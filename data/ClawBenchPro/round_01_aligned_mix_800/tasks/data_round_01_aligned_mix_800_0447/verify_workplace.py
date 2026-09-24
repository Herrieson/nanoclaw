import os
import sys
import json
import csv
import glob
import re
import math
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

def get_ground_truth(workspace):
    id_to_name = {}
    name_to_id = {}
    
    # 1. 解析受洗记录映射表
    baptism_dir = os.path.join(workspace, "baptism_records")
    if os.path.exists(baptism_dir):
        shard_files = glob.glob(os.path.join(baptism_dir, "*.json"))
        for f in shard_files:
            try:
                with open(f, "r", encoding="utf-8") as jf:
                    data = json.load(jf)
                    for rec in data.get("records", []):
                        vid = rec["id"]
                        name = rec["name"]
                        id_to_name[vid] = name
                        name_to_id[name] = vid
            except Exception:
                pass

    # 2. 解析白名单
    whitelist_ids = set()
    wl_path = os.path.join(workspace, "official_whitelist.csv")
    if os.path.exists(wl_path):
        try:
            with open(wl_path, "r", encoding="utf-8") as cf:
                reader = csv.DictReader(cf)
                for row in reader:
                    if "volunteer_id" in row:
                        whitelist_ids.add(row["volunteer_id"].strip())
        except Exception:
            pass

    # 3. 深度遍历原始打卡日志进行精准提取
    total_wl_hours = 0.0
    unlisted_vols = set()
    
    raw_dir = os.path.join(workspace, "raw_records", "2023", "10")
    if os.path.exists(raw_dir):
        for root, dirs, files in os.walk(raw_dir):
            for file in files:
                # 排除 .bak, 只读取包含 attendance 并以 .log 结尾的文件
                if file.endswith(".log") and "attendance" in file:
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as lf:
                            for line in lf:
                                line = line.strip()
                                if not line: continue
                                # 直接忽略作废行
                                if "[VOID]" in line or "[CANCELLED]" in line:
                                    continue
                                # 只处理真实发生的打卡
                                if "[OK]" in line or "[VALID]" in line:
                                    hours_match = re.search(r'(?:Duration|Hours):\s*([\d\.]+)', line)
                                    if not hours_match:
                                        continue
                                    hours = float(hours_match.group(1))
                                    
                                    id_match = re.search(r'ID:\s*(V\d+)', line)
                                    name_match = re.search(r'Name:\s*"([^"]+)"', line)
                                    
                                    vid = None
                                    name = None
                                    
                                    if id_match:
                                        vid = id_match.group(1)
                                        name = id_to_name.get(vid, "Unknown")
                                    elif name_match:
                                        name = name_match.group(1)
                                        vid = name_to_id.get(name)
                                        
                                    if vid in whitelist_ids:
                                        total_wl_hours += hours
                                    else:
                                        if name:
                                            unlisted_vols.add(name)
                    except Exception:
                        pass
                        
    sorted_unlisted = sorted(list(unlisted_vols))
    return sorted_unlisted, total_wl_hours

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0
    
    # 生成 Ground Truth
    gt_unlisted, gt_hours = get_ground_truth(workspace)
    
    report_path = os.path.join(workspace, "summary", "report.json")
    
    # 检查项 1：目录与文件存在性及格式
    file_exists = os.path.isfile(report_path)
    if not file_exists:
        score_details.append({"item": "生成目标报告文件", "score": 0, "max_score": 15, "passed": False, "reason": f"未找到文件 {report_path}"})
        # 如果文件不存在，后续判断无从谈起
        with open("workplace_score.json", "w", encoding="utf-8") as f:
            json.dump({"total_score": 0, "details": score_details}, f, indent=2)
        return
    else:
        score_details.append({"item": "生成目标报告文件", "score": 15, "max_score": 15, "passed": True, "reason": "成功定位到 summary/report.json"})
        total_score += 15

    # 检查项 2：JSON格式合法性
    agent_data = None
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            raw_content = f.read()
            agent_data = json.loads(raw_content)
        score_details.append({"item": "JSON 格式合法性解析", "score": 10, "max_score": 10, "passed": True, "reason": "文件符合标准 JSON 语法"})
        total_score += 10
    except Exception as e:
        score_details.append({"item": "JSON 格式合法性解析", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON解析失败: {e}"})
        
    if agent_data is not None:
        # 检查项 3：名单准确性 (最高 30 分)
        agent_unlisted = agent_data.get("unlisted_volunteers", [])
        if not isinstance(agent_unlisted, list):
            score_details.append({"item": "编外人员名单分析", "score": 0, "max_score": 30, "passed": False, "reason": "unlisted_volunteers 字段缺失或类型非列表"})
        else:
            correct_count = len(set(gt_unlisted) & set(agent_unlisted))
            extra = len(set(agent_unlisted) - set(gt_unlisted))
            total_gt = len(gt_unlisted)
            
            if total_gt == 0:
                list_score = 25 if extra == 0 else 0
            else:
                accuracy = correct_count / total_gt
                penalty = extra * (1.0 / total_gt)
                final_ratio = max(0.0, accuracy - penalty)
                list_score = int(25 * final_ratio)
            
            # 排序检查
            sort_score = 5 if (sorted(agent_unlisted) == agent_unlisted and len(agent_unlisted) > 0) else 0
            final_list_score = list_score + sort_score
            passed_list = (final_list_score == 30)
            
            score_details.append({"item": "编外人员名单提取与去重排序", "score": final_list_score, "max_score": 30, "passed": passed_list, "reason": f"识别正确率: {correct_count}/{total_gt}, 错误项: {extra}个, 排序检测得分: {sort_score}/5"})
            total_score += final_list_score

        # 检查项 4：总工时计算精准度 (最高 35 分)
        agent_hours = agent_data.get("total_whitelist_hours", None)
        if agent_hours is None or not isinstance(agent_hours, (int, float)):
            score_details.append({"item": "有效工时总量累加", "score": 0, "max_score": 35, "passed": False, "reason": "total_whitelist_hours 字段缺失或非数值"})
        else:
            diff = abs(float(agent_hours) - float(gt_hours))
            if diff <= 0.1:
                hour_score = 35
                reason = "计算结果与答案高度吻合"
            elif diff <= 10.0:
                hour_score = 15
                reason = "计算结果存在较小误差 (未正确排除 VOID 或未完全过滤非法文件)"
            else:
                hour_score = 0
                reason = f"计算偏差过大, 实际={gt_hours}, 提交={agent_hours}"
            score_details.append({"item": "有效工时总量累加", "score": hour_score, "max_score": 35, "passed": (hour_score == 35), "reason": reason})
            total_score += hour_score

        # 检查项 5：LLM 风格纯净度检查 (最高 10 分)
        llm_prompt = (
            "Check if the following JSON content is purely a professional data report. "
            "It should only contain valid data arrays and numbers. "
            "If the JSON contains ANY extra fields with anime references, Evangelion quotes, philosophical complaints, "
            "or 'chuunibyou' chat texts, you MUST answer NO. "
            "If it is a clean, strict data-only JSON matching the structural need, answer YES."
        )
        is_professional = llm_judge_content(llm_prompt, raw_content)
        if is_professional:
            score_details.append({"item": "大模型语义检查: 报告纯净度", "score": 10, "max_score": 10, "passed": True, "reason": "未发现被混入多余的吐槽或动漫污染数据"})
            total_score += 10
        else:
            score_details.append({"item": "大模型语义检查: 报告纯净度", "score": 0, "max_score": 10, "passed": False, "reason": "大模型判定 JSON 数据被注入了无关的聊天或动漫文本污染"})
    
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
