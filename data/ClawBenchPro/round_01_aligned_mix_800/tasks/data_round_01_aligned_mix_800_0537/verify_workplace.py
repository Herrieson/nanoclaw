import os
import sys
import json
import csv
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
    # 此函数为检测非结构化文本的统一接口
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

def build_ground_truth_registry(workspace):
    registry = {}
    
    # 解析 CSV
    csv_path = os.path.join(workspace, "mapping_protocols", "registry_part_A.csv")
    if os.path.exists(csv_path):
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if "ID" in row and "Artist Name" in row:
                    registry[row["ID"].strip()] = row["Artist Name"].strip()
                    
    # 解析 TXT
    txt_path = os.path.join(workspace, "mapping_protocols", "registry_part_B.txt")
    if os.path.exists(txt_path):
        with open(txt_path, "r", encoding="utf-8") as f:
            for line in f:
                if "REF_ID:" in line and "NAME:" in line:
                    parts = line.split("|")
                    if len(parts) == 2:
                        ref_id = parts[0].split("REF_ID:")[1].strip()
                        name = parts[1].split("NAME:")[1].strip()
                        # 还原为 ID_10x 格式
                        registry[f"ID_{ref_id}"] = name
    return registry

def scan_and_evaluate_assets(workspace):
    FORBIDDEN_FONTS = {"Papyrus", "Comic Sans"}
    FORBIDDEN_COLORS = {"#000000", "#FFFFFF"}
    
    all_assets = []
    
    # 遍历整个工作区以寻找有效的 json 资产（同时记录它们的当前位置）
    for root, _, files in os.walk(workspace):
        # 排除 deliverables 目录，避免把最终结果当成原始素材
        if "deliverables" in root:
            continue
            
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # 严格通过 Schema 判断是否为真实资产
                    if isinstance(data, dict) and "id" in data and "title" in data and "metadata" in data:
                        metadata = data.get("metadata", {})
                        if "typography" in metadata and "branding" in metadata:
                            palette = metadata.get("branding", {}).get("palette", [])
                            if isinstance(palette, list) and len(palette) > 0:
                                all_assets.append({
                                    "path": file_path,
                                    "data": data,
                                    "is_bad": metadata["typography"] in FORBIDDEN_FONTS or palette[0] in FORBIDDEN_COLORS
                                })
            except Exception:
                # 忽略无法解析的 decoy 文件
                pass
                
    return all_assets

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0
    
    # ==========================================
    # 1. 验证目录结构 (10分)
    # ==========================================
    archive_dir = os.path.join(workspace, "archive")
    deliverables_dir = os.path.join(workspace, "deliverables")
    
    dir_passed = os.path.isdir(archive_dir) and os.path.isdir(deliverables_dir)
    score_details.append({
        "item": "目录结构完整性",
        "score": 10 if dir_passed else 0,
        "max_score": 10,
        "passed": dir_passed,
        "reason": "archive 和 deliverables 目录均已存在" if dir_passed else "缺少 archive 或 deliverables 目录"
    })
    total_score += 10 if dir_passed else 0

    # 获取事实数据
    registry = build_ground_truth_registry(workspace)
    assets = scan_and_evaluate_assets(workspace)
    
    # ==========================================
    # 2. 验证坏文件的归档情况 (30分)
    # ==========================================
    archive_passed = True
    archive_reasons = []
    bad_assets_count = 0
    
    for asset in assets:
        in_archive = "archive" in os.path.normpath(asset["path"]).split(os.sep)
        if asset["is_bad"]:
            bad_assets_count += 1
            if not in_archive:
                archive_passed = False
                archive_reasons.append(f"违规文件未被移入 archive: {asset['path']}")
        else:
            if in_archive:
                archive_passed = False
                archive_reasons.append(f"合规文件被错误移入 archive: {asset['path']}")

    # 检查 archive 中是否混入了 decoy（无法解析为有效 JSON 的文件）
    if os.path.exists(archive_dir):
        for file in os.listdir(archive_dir):
            file_path = os.path.join(archive_dir, file)
            if os.path.isfile(file_path):
                is_known_asset = any(os.path.samefile(file_path, a["path"]) for a in assets)
                if not is_known_asset:
                    archive_passed = False
                    archive_reasons.append(f"无关的噪音文件被移入 archive: {file}")

    archive_score = 30 if archive_passed and bad_assets_count > 0 else (0 if not archive_passed else 10) # 若无坏文件(异常情况)给10分
    score_details.append({
        "item": "隔离违规文件与噪音处理",
        "score": archive_score,
        "max_score": 30,
        "passed": archive_passed and bad_assets_count > 0,
        "reason": "违规文件均已归档且无误伤" if archive_score == 30 else "; ".join(archive_reasons[:3])
    })
    total_score += archive_score

    # ==========================================
    # 3. 验证 Deliverables 存在与格式 (20分)
    # ==========================================
    manifest_path = os.path.join(deliverables_dir, "final_manifest.json")
    manifest_data = None
    manifest_format_passed = False
    
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)
                # 判断是否为结构化的列表或字典
                if isinstance(manifest_data, (dict, list)):
                    manifest_format_passed = True
        except Exception:
            pass

    score_details.append({
        "item": "交付物 final_manifest.json 存在且为有效 JSON",
        "score": 20 if manifest_format_passed else 0,
        "max_score": 20,
        "passed": manifest_format_passed,
        "reason": "解析 JSON 成功" if manifest_format_passed else "文件不存在或 JSON 格式错误"
    })
    total_score += 20 if manifest_format_passed else 0

    # ==========================================
    # 4. 验证核心数据映射准确性 (30分)
    # ==========================================
    data_score = 0
    data_reasons = []
    
    if manifest_format_passed and manifest_data is not None:
        expected_mappings = {}
        for asset in assets:
            if not asset["is_bad"]:
                artist_name = registry.get(asset["data"]["id"])
                if artist_name:
                    concept = asset["data"]["title"]
                    hex_code = asset["data"]["metadata"]["branding"]["palette"][0]
                    expected_mappings[artist_name] = {
                        "Approved_Concept": concept,
                        "Primary_Hex": hex_code
                    }
        
        # 将 Agent 生成的数据标准化为 {Artist: {Concept, Hex}} 以便对比
        actual_mappings = {}
        if isinstance(manifest_data, dict):
            # 可能是 {"Artist Name": {"Approved_Concept": "...", "Primary_Hex": "..."}}
            for k, v in manifest_data.items():
                if isinstance(v, dict):
                    actual_mappings[k] = v
        elif isinstance(manifest_data, list):
            # 可能是 [{"Artist": "...", "Approved_Concept": "...", "Primary_Hex": "..."}]
            for item in manifest_data:
                if isinstance(item, dict):
                    # 尝试寻找代表 Artist 的键
                    artist_key = next((k for k in item.keys() if "artist" in k.lower()), None)
                    if artist_key:
                        actual_mappings[item[artist_key]] = item

        # 严格比对
        if not expected_mappings:
            data_reasons.append("未能构建出 Ground Truth，可能环境生成失败")
        else:
            correct_count = 0
            for exp_artist, exp_data in expected_mappings.items():
                if exp_artist in actual_mappings:
                    act_data = actual_mappings[exp_artist]
                    # 提取实际的 concept 和 hex (不依赖精确键名，检查值是否存在)
                    act_values = list(act_data.values())
                    if exp_data["Approved_Concept"] in act_values and exp_data["Primary_Hex"] in act_values:
                        correct_count += 1
                    else:
                        data_reasons.append(f"艺术家 {exp_artist} 的概念或颜色映射错误")
                else:
                    data_reasons.append(f"缺少合法艺术家: {exp_artist}")
            
            # 检查是否有幻觉出的多余人员
            extra_artists = set(actual_mappings.keys()) - set(expected_mappings.keys())
            if extra_artists:
                data_reasons.append(f"幻觉出多余的艺术家数据: {len(extra_artists)} 个")
                
            if correct_count == len(expected_mappings) and not extra_artists:
                data_score = 30
                data_reasons.append("精准提取并映射了所有合规艺术家的数据")
            else:
                data_score = int((correct_count / len(expected_mappings)) * 15) # 部分给分
    else:
        data_reasons.append("前置 JSON 解析失败，无法验证数据")

    score_details.append({
        "item": "数据逻辑与精准提取",
        "score": data_score,
        "max_score": 30,
        "passed": data_score == 30,
        "reason": "; ".join(data_reasons[:3])
    })
    total_score += data_score

    # ==========================================
    # 5. LLM 语义与幻觉检查 (10分)
    # ==========================================
    llm_score = 0
    llm_reason = "跳过检测"
    
    if manifest_format_passed:
        prompt_text = (
            "Analyze the provided JSON file content. "
            "The persona strictly demanded a clean JSON mapping Artist to Approved_Concept and Primary_Hex, with NO fluff. "
            "Check for the following:\n"
            "1. Does it strictly contain ONLY the requested data (or standard JSON structural wrappers)?\n"
            "2. Are there NO hallucinated apologies, extra conversational text, or irrelevant properties (like 'status': 'success') added to the root?\n"
            "If it is perfectly clean and professional data without any hallucinations or fluff, output YES. Otherwise output NO."
        )
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                content = f.read()
            passed_llm = llm_judge_content(prompt_text, content)
            if passed_llm:
                llm_score = 10
                llm_reason = "大模型判定 JSON 结构纯净，无幻觉、无废话"
            else:
                llm_reason = "大模型判定文件包含冗余废话或多余的幻觉字段"
        except Exception as e:
            llm_reason = f"LLM 检测异常: {e}"

    score_details.append({
        "item": "大模型校验：无幻觉与严格语义遵守",
        "score": llm_score,
        "max_score": 10,
        "passed": llm_score == 10,
        "reason": llm_reason
    })
    total_score += llm_score

    # ==========================================
    # 汇总并输出
    # ==========================================
    final_result = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(final_result, f, indent=2, ensure_ascii=False)
        
    print(json.dumps(final_result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    verify()
