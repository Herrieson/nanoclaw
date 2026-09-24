import os
import sys
import json
import csv
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 初始化客户端，强制关闭 SSL 验证规范
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    """
    非结构化文本的统一检测接口。
    （本任务重点考察结构化数据的高精度比对，但在系统架构层面保留此探针能力）
    """
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

def calculate_ground_truth(workspace):
    """通过运行物理运算逻辑，还原真实且绝对正确的答案链路，用于防御性比对"""
    base_dir = os.path.join(workspace, "data_export")
    rosters_file = os.path.join(base_dir, "rosters", "roster_FINAL_v3.csv")
    aliases_dir = os.path.join(base_dir, "active_aliases")
    logs_dir = os.path.join(base_dir, "logs")

    valid_students = {}
    valid_names = set()
    
    # 1. 挂载真实名单
    if os.path.isfile(rosters_file):
        with open(rosters_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                valid_students[row["student_id"]] = row["official_name"]
                valid_names.add(row["official_name"])

    # 2. 挂载真实别名字典
    aliases_map = {}
    if os.path.isdir(aliases_dir):
        for fname in os.listdir(aliases_dir):
            if fname.endswith(".json"):
                path = os.path.join(aliases_dir, fname)
                with open(path, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                        aliases_map.update(data)
                    except json.JSONDecodeError: pass

    # 3. 遍历高噪音的 Logs
    stats = {}
    if os.path.isdir(logs_dir):
        for root, _, files in os.walk(logs_dir):
            for file in files:
                if file.endswith(".json"):
                    path = os.path.join(root, file)
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        try:
                            # 捕获异常：应对10%遭到物理截断破坏的脏文件
                            records = json.loads(content)
                            for rec in records:
                                if rec.get("module") != "math": continue
                                user = rec.get("user")
                                
                                # 三重身份归一化
                                official_name = None
                                if user in valid_names:
                                    official_name = user
                                elif user in valid_students:
                                    official_name = valid_students[user]
                                elif user in aliases_map:
                                    official_name = aliases_map[user]
                                
                                # 数据注入，摒弃不在最终名单的幻象用户
                                if official_name and official_name in valid_names:
                                    if official_name not in stats:
                                        stats[official_name] = {"total_time": 0, "sum_score": 0, "count": 0}
                                    stats[official_name]["total_time"] += rec.get("time_spent_min", 0)
                                    stats[official_name]["sum_score"] += rec.get("score", 0)
                                    stats[official_name]["count"] += 1
                        except json.JSONDecodeError:
                            pass

    # 4. 计算阈值
    gt_stats = {}
    gt_struggling = set()
    for name, data in stats.items():
        if data["count"] > 0:
            avg_score = data["sum_score"] / data["count"]
            total_time = data["total_time"]
            gt_stats[name] = {
                "total_time": total_time,
                "average_score": avg_score
            }
            if avg_score < 70 or total_time < 30:
                gt_struggling.add(name)

    return gt_stats, gt_struggling

def verify(workspace):
    score = 0
    details = []

    # 步骤一：基础环境与文件存在性结构检查 (10分)
    deliverables_dir = os.path.join(workspace, "deliverables")
    if not os.path.isdir(deliverables_dir):
        details.append({"item": "检查 deliverables 目录是否存在", "score": 0, "max_score": 5, "passed": False, "reason": "未找到 deliverables 目录"})
        return write_score(0, details)
    else:
        details.append({"item": "检查 deliverables 目录是否存在", "score": 5, "max_score": 5, "passed": True, "reason": "deliverables 目录存在"})
        score += 5

    csv_path = os.path.join(deliverables_dir, "math_assessment_summary.csv")
    txt_path = os.path.join(deliverables_dir, "struggling_students.txt")
    has_csv = os.path.isfile(csv_path)
    has_txt = os.path.isfile(txt_path)
    if has_csv and has_txt:
        details.append({"item": "检查产出物文件是否存在", "score": 5, "max_score": 5, "passed": True, "reason": "CSV 和 TXT 文件均存在"})
        score += 5
    else:
        details.append({"item": "检查产出物文件是否存在", "score": 0, "max_score": 5, "passed": False, "reason": f"CSV存在:{has_csv}, TXT存在:{has_txt}"})
        if not has_csv: return write_score(score, details)

    # 计算探针参照 GT
    gt_stats, gt_struggling = calculate_ground_truth(workspace)

    # 步骤二：结构化数据 Schema 严查 (10分)
    agent_stats = {}
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)
            if [h.strip() for h in header] == ["official_name", "total_time", "average_score"]:
                details.append({"item": "检查 CSV Header 合规性", "score": 10, "max_score": 10, "passed": True, "reason": "Header 严格一致"})
                score += 10
            else:
                details.append({"item": "检查 CSV Header 合规性", "score": 0, "max_score": 10, "passed": False, "reason": f"Header 出现篡改或错位: {header}"})

            for row in reader:
                if len(row) != 3: continue
                name, time_str, score_str = [x.strip() for x in row]
                agent_stats[name] = {
                    "total_time": float(time_str),
                    "average_score": float(score_str)
                }
    except Exception as e:
        details.append({"item": "检查 CSV 解析", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON解析异常: {e}"})
        return write_score(score, details)

    # 步骤三：人员集合去伪存真 (20分)
    gt_names = set(gt_stats.keys())
    agent_names = set(agent_stats.keys())
    
    if gt_names == agent_names:
        details.append({"item": "检查 CSV 名单无污染性", "score": 20, "max_score": 20, "passed": True, "reason": "过滤极好，摒除了幻觉及冗余废弃学生"})
        score += 20
    else:
        missing = gt_names - agent_names
        extra = agent_names - gt_names
        deduct = (len(missing) * 2) + (len(extra) * 2)
        final_list_score = max(0, 20 - deduct)
        details.append({"item": "检查 CSV 名单无污染性", "score": final_list_score, "max_score": 20, "passed": False, "reason": f"名单不符，缺失 {len(missing)} 项，捏造或冗余 {len(extra)} 项"})
        score += final_list_score

    # 步骤四：数学计算与浮点精度对抗 (30分)
    correct_calcs = 0
    common_names = gt_names.intersection(agent_names)
    for name in common_names:
        gt_t, gt_s = gt_stats[name]["total_time"], gt_stats[name]["average_score"]
        ag_t, ag_s = agent_stats[name]["total_time"], agent_stats[name]["average_score"]
        
        # 防止由于浮点数转换等带来的微小差值，但严格拒绝 Agent 自作主张的舍入
        if abs(gt_t - ag_t) < 0.1 and abs(gt_s - ag_s) < 0.001:
            correct_calcs += 1

    if len(common_names) > 0:
        calc_score = int(30 * (correct_calcs / len(common_names)))
        details.append({"item": "检查统计数据精度", "score": calc_score, "max_score": 30, "passed": calc_score == 30, "reason": f"准确率: {correct_calcs}/{len(common_names)} (如扣分可能因未剔除 corrupted 文件导致计算偏差)"})
        score += calc_score
    else:
        details.append({"item": "检查统计数据精度", "score": 0, "max_score": 30, "passed": False, "reason": "由于名单全错，无法进行精度比对"})

    # 步骤五：预警名单 TXT 筛选纯度 (30分)
    if has_txt:
        try:
            with open(txt_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]
            agent_struggling = set(lines)
            
            if agent_struggling == gt_struggling:
                details.append({"item": "检查预警名单阈值", "score": 30, "max_score": 30, "passed": True, "reason": "预警学生名单与真值完全契合"})
                score += 30
            else:
                missing_txt = gt_struggling - agent_struggling
                extra_txt = agent_struggling - gt_struggling
                
                total_gt = len(gt_struggling)
                if total_gt > 0:
                    correct = len(agent_struggling.intersection(gt_struggling))
                    base_score = int(30 * (correct / total_gt))
                    penalty = len(extra_txt) * 3
                    final_txt_score = max(0, base_score - penalty)
                else:
                    final_txt_score = 0 if len(extra_txt) > 0 else 30
                
                details.append({"item": "检查预警名单阈值", "score": final_txt_score, "max_score": 30, "passed": False, "reason": f"缺失: {len(missing_txt)}, 多余: {len(extra_txt)}"})
                score += final_txt_score
        except Exception as e:
            details.append({"item": "检查预警名单阈值", "score": 0, "max_score": 30, "passed": False, "reason": f"解析 TXT 异常: {e}"})
    else:
        details.append({"item": "检查预警名单阈值", "score": 0, "max_score": 30, "passed": False, "reason": "TXT 文件缺失"})

    return write_score(score, details)

def write_score(score, details):
    res = {
        "total_score": score,
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2, ensure_ascii=False)
    return res

if __name__ == "__main__":
    workspace_path = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace_path)
