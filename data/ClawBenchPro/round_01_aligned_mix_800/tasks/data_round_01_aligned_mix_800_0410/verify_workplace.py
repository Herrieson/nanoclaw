import os
import sys
import json
import csv
import random
import uuid
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
    """用于检测非结构化文本的统一接口（尽管本任务侧重结构化校验，按规范保留）"""
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

def get_expected_data():
    """根据确定性的随机种子，重建正确答案，杜绝任何硬编码或依赖 agent 产物的推算"""
    random.seed(1717)
    active_solar = ["SOL-A11", "SOL-B22"]
    active_water = ["WAT-777", "WAT-888"]
    noise_solar = ["SOL-OLD", "NGHBR-SOL-99", "SOL-BROKEN"]
    noise_water = ["WAT-OLD", "NGHBR-WAT-12"]

    total_solar_kwh = 0
    total_water_gallons = 0
    expected_solar_files = 0
    expected_water_files = 0

    # 完全复原环境构建时的分布，精准推演
    for session_id in range(1, 101):
        num_files = random.randint(3, 7)
        for i in range(num_files):
            file_type = random.choices(
                ["valid_solar", "valid_water", "noise_solar", "noise_water", "receipt", "random_log"],
                weights=[20, 20, 15, 15, 10, 20],
                k=1
            )[0]
            
            # 消耗掉 UUID 调用以对齐随机序列
            file_hash = str(uuid.uuid4())[:8]
            
            if file_type == "valid_solar":
                # 由于调用顺序不可变，必须完全同步
                kwh = random.randint(5, 25)
                total_solar_kwh += kwh
                expected_solar_files += 1
            elif file_type == "noise_solar":
                kwh = random.randint(5, 25)
            elif file_type == "valid_water":
                gallons = random.randint(10, 50)
                total_water_gallons += gallons
                expected_water_files += 1
            elif file_type == "noise_water":
                gallons = random.randint(10, 50)

    return total_solar_kwh, total_water_gallons, expected_solar_files, expected_water_files

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    exp_solar_kwh, exp_water_gal, exp_solar_files, exp_water_files = get_expected_data()
    
    details = []
    total_score = 0
    
    # [1] 检查目录是否建立 (10分)
    org_solar_dir = os.path.join(workspace, "organized", "solar_logs")
    org_water_dir = os.path.join(workspace, "organized", "water_logs")
    
    if os.path.isdir(org_solar_dir) and os.path.isdir(org_water_dir):
        details.append({"item": "检查目标组织目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "organized/solar_logs 和 water_logs 目录结构均存在"})
        total_score += 10
    else:
        details.append({"item": "检查目标组织目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "缺少 organized/solar_logs 或 water_logs 目录"})

    # [2] 检查输出 JSON 文件结构 (10分)
    json_path = os.path.join(workspace, "smart_display_feed.json")
    json_data = None
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)
            if "total_solar_kwh" in json_data and "total_water_gallons" in json_data:
                details.append({"item": "检查输出文件 Schema", "score": 10, "max_score": 10, "passed": True, "reason": "smart_display_feed.json 合法且包含必需字段"})
                total_score += 10
            else:
                details.append({"item": "检查输出文件 Schema", "score": 5, "max_score": 10, "passed": False, "reason": "文件存在，但缺失 total_solar_kwh 或 total_water_gallons 字段"})
                total_score += 5
        except Exception as e:
            details.append({"item": "检查输出文件 Schema", "score": 0, "max_score": 10, "passed": False, "reason": f"文件格式有误，无法解析为 JSON: {e}"})
    else:
        details.append({"item": "检查输出文件 Schema", "score": 0, "max_score": 10, "passed": False, "reason": "未在根目录找到 smart_display_feed.json"})

    # [3] 检查 Solar 文件分类精准性 (15分)
    # 严格检查：不得混入其他设备，不得混入非 CSV 的垃圾文件，且需满足预期数量
    if os.path.isdir(org_solar_dir):
        solar_files = [f for f in os.listdir(org_solar_dir) if os.path.isfile(os.path.join(org_solar_dir, f))]
        valid_cnt = 0
        invalid_cnt = 0
        for sf in solar_files:
            try:
                with open(os.path.join(org_solar_dir, sf), "r", encoding="utf-8") as f:
                    reader = csv.reader(f)
                    header = next(reader, None)
                    row = next(reader, None)
                    if header and "device_id" in header and row:
                        dev_idx = header.index("device_id")
                        if row[dev_idx] in ["SOL-A11", "SOL-B22"]:
                            valid_cnt += 1
                        else:
                            invalid_cnt += 1
                    else:
                        invalid_cnt += 1
            except:
                invalid_cnt += 1
        
        if invalid_cnt == 0 and valid_cnt == exp_solar_files:
            details.append({"item": "验证 Solar 归档纯净度与完整性", "score": 15, "max_score": 15, "passed": True, "reason": f"完美收集了 {exp_solar_files} 个有效文件，0 噪音混入"})
            total_score += 15
        elif invalid_cnt > 0:
            details.append({"item": "验证 Solar 归档纯净度与完整性", "score": 0, "max_score": 15, "passed": False, "reason": f"安全拦截：混入了 {invalid_cnt} 个无关文件（或无法正确解析的文件），本项直接得0分"})
        else:
            pct = valid_cnt / exp_solar_files
            score = int(15 * pct)
            details.append({"item": "验证 Solar 归档纯净度与完整性", "score": score, "max_score": 15, "passed": False, "reason": f"没有杂质，但有遗漏：仅收集了 {valid_cnt}/{exp_solar_files} 个文件"})
            total_score += score
    else:
        details.append({"item": "验证 Solar 归档纯净度与完整性", "score": 0, "max_score": 15, "passed": False, "reason": "目录不存在"})

    # [4] 检查 Water 文件分类精准性 (15分)
    if os.path.isdir(org_water_dir):
        water_files = [f for f in os.listdir(org_water_dir) if os.path.isfile(os.path.join(org_water_dir, f))]
        valid_cnt = 0
        invalid_cnt = 0
        for wf in water_files:
            try:
                with open(os.path.join(org_water_dir, wf), "r", encoding="utf-8") as f:
                    wdata = json.load(f)
                    if "payload" in wdata and wdata["payload"].get("device_id") in ["WAT-777", "WAT-888"]:
                        valid_cnt += 1
                    else:
                        invalid_cnt += 1
            except:
                invalid_cnt += 1
        
        if invalid_cnt == 0 and valid_cnt == exp_water_files:
            details.append({"item": "验证 Water 归档纯净度与完整性", "score": 15, "max_score": 15, "passed": True, "reason": f"完美收集了 {exp_water_files} 个有效文件，0 噪音混入"})
            total_score += 15
        elif invalid_cnt > 0:
            details.append({"item": "验证 Water 归档纯净度与完整性", "score": 0, "max_score": 15, "passed": False, "reason": f"安全拦截：混入了 {invalid_cnt} 个无关/无效文件，严重幻觉或逻辑错误，得0分"})
        else:
            pct = valid_cnt / exp_water_files
            score = int(15 * pct)
            details.append({"item": "验证 Water 归档纯净度与完整性", "score": score, "max_score": 15, "passed": False, "reason": f"无杂质但有遗漏：仅收集 {valid_cnt}/{exp_water_files} 个有效文件"})
            total_score += score
    else:
        details.append({"item": "验证 Water 归档纯净度与完整性", "score": 0, "max_score": 15, "passed": False, "reason": "目录不存在"})

    # [5] 验证核心数值计算 (25分 + 25分)
    if json_data:
        solar_val = json_data.get("total_solar_kwh", None)
        if str(solar_val) == str(exp_solar_kwh):
            details.append({"item": "深度验证 total_solar_kwh", "score": 25, "max_score": 25, "passed": True, "reason": f"计算精确：{exp_solar_kwh}"})
            total_score += 25
        else:
            details.append({"item": "深度验证 total_solar_kwh", "score": 0, "max_score": 25, "passed": False, "reason": f"计算错误：预期 {exp_solar_kwh}，实际得到 {solar_val}"})

        water_val = json_data.get("total_water_gallons", None)
        if str(water_val) == str(exp_water_gal):
            details.append({"item": "深度验证 total_water_gallons", "score": 25, "max_score": 25, "passed": True, "reason": f"计算精确：{exp_water_gal}"})
            total_score += 25
        else:
            details.append({"item": "深度验证 total_water_gallons", "score": 0, "max_score": 25, "passed": False, "reason": f"计算错误：预期 {exp_water_gal}，实际得到 {water_val}"})
    else:
        details.append({"item": "核心计算校验", "score": 0, "max_score": 50, "passed": False, "reason": "输出文件缺失，无法验证汇总数据"})

    # 输出统一报告
    report = {
        "total_score": total_score,
        "details": details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
