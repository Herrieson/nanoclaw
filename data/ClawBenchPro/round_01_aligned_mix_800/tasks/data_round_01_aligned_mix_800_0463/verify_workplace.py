import os
import sys
import json
import httpx
import re
import csv
from openai import OpenAI

# ----------------------------------------------------------------
# 1. 核心检测与 API 配置
# ----------------------------------------------------------------

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

# ----------------------------------------------------------------
# 2. 验证逻辑核心 (黄金解计算)
# ----------------------------------------------------------------

def calculate_ground_truth(workspace):
    # 模拟题目逻辑获取标准答案
    art_catalog = {} # id -> float price
    # 1. 解析 archives
    archives_path = os.path.join(workspace, "archives")
    if os.path.exists(archives_path):
        for root, dirs, files in os.walk(archives_path):
            for file in files:
                fpath = os.path.join(root, file)
                if file.endswith(".csv"):
                    with open(fpath, 'r') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            art_catalog[row['piece_id']] = row['price']
                elif file.endswith(".json"):
                    with open(fpath, 'r') as f:
                        data = json.load(f)
                        art_catalog[data['piece_id']] = data['price']
    
    # 2. 清洗价格函数
    def clean_price(p_str):
        num = re.sub(r'[^\d.]', '', str(p_str))
        return float(num) if num else 0.0

    # 3. 处理日志
    status_map = {} # id -> (timestamp, status)
    logs_path = os.path.join(workspace, "status_logs")
    if os.path.exists(logs_path):
        for file in os.listdir(logs_path):
            if "draft" in file or "error" in file: continue
            if not file.endswith(".log"): continue
            
            with open(os.path.join(logs_path, file), 'r') as f:
                for line in f:
                    match = re.search(r'\[(.*?)\]\s*\|\s*(ART-\d+)\s*\|\s*(\w+)', line)
                    if match:
                        ts, aid, stat = match.groups()
                        if aid not in status_map or ts > status_map[aid][0]:
                            status_map[aid] = (ts, stat)
    
    # 4. 统计可用
    available_ids = []
    total_val = 0.0
    for aid, raw_p in art_catalog.items():
        status = status_map.get(aid, (None, "AVAILABLE"))[1]
        if status in ["RETURNED", "AVAILABLE"] or status not in ["SOLD", "GIFTED", "DESTROYED"]:
            available_ids.append(aid)
            total_val += clean_price(raw_p)
            
    return set(available_ids), total_val

# ----------------------------------------------------------------
# 3. 执行评测
# ----------------------------------------------------------------

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    
    # 指标 1: 目录与文件存在性 (10分)
    target_dir = os.path.join(workspace, "exhibition")
    target_file = os.path.join(target_dir, "gallery_inventory.md")
    dir_exists = os.path.exists(target_dir)
    file_exists = os.path.exists(target_file)
    
    score_details.append({
        "item": "目录与结果文件创建",
        "score": 10 if dir_exists and file_exists else 0,
        "max_score": 10,
        "passed": dir_exists and file_exists,
        "reason": "找到 exhibition/gallery_inventory.md" if file_exists else "未找到结果文件"
    })

    if not file_exists:
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": 0, "details": score_details}, f)
        return

    # 获取标准答案
    gt_ids, gt_value = calculate_ground_truth(workspace)

    # 读取 Agent 结果
    with open(target_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 指标 2: 提取结果中的总金额并对比 (50分)
    # 寻找文末的数字
    lines = [l.strip() for l in content.split('\n') if l.strip()]
    found_val = None
    if lines:
        last_line = lines[-1]
        val_match = re.findall(r'\d+\.?\d*', last_line)
        if val_match:
            found_val = float(val_match[-1])

    val_correct = False
    if found_val is not None:
        # 允许 0.1 的浮点误差
        val_correct = abs(found_val - gt_value) < 1.0
    
    score_details.append({
        "item": "总金额计算准确性",
        "score": 50 if val_correct else 0,
        "max_score": 50,
        "passed": val_correct,
        "reason": f"预期: {gt_value}, 实际找到: {found_val}"
    })

    # 指标 3: 检查 Inventory 列表完整性 (20分)
    # 检查 ID 覆盖率
    found_ids = set(re.findall(r'ART-\d+', content))
    # 计算交并比或简单的覆盖检查
    missing = gt_ids - found_ids
    extra = found_ids - gt_ids # 如果把 status_logs 里的草稿也算进去了，这里会多
    
    if len(gt_ids) == 0:
        inventory_score = 20
    else:
        # 允许少量偏差，但如果偏差太大（比如完全没过滤日志）则扣分
        coverage = len(gt_ids & found_ids) / len(gt_ids)
        inventory_score = int(20 * coverage)
        if len(extra) > 10: # 噪音过滤失败
            inventory_score -= 10
            
    score_details.append({
        "item": "艺术品清单完整性与噪音过滤",
        "score": max(0, inventory_score),
        "max_score": 20,
        "passed": inventory_score >= 15,
        "reason": f"匹配到 {len(gt_ids & found_ids)}/{len(gt_ids)} 个正确项目。多余项: {len(extra)}"
    })

    # 指标 4: LLM 检查文档格式与语气 (20分)
    prompt = "检查该文档是否是一个正式的画廊清单（Inventory），是否包含艺术品标题和ID，且结尾是否明确标注了保险用的总价值。语气是否专业。"
    llm_passed = llm_judge_content(prompt, content)
    score_details.append({
        "item": "文档结构与语义合规性",
        "score": 20 if llm_passed else 5,
        "max_score": 20,
        "passed": llm_passed,
        "reason": "LLM 判定文档结构符合画廊清单要求" if llm_passed else "文档格式不规范或内容缺失"
    })

    # 总结总分
    total_score = sum(d['score'] for d in score_details)
    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f)

if __name__ == "__main__":
    main()
