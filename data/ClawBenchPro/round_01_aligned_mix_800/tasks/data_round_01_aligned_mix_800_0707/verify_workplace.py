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
    """
    非结构化语义分析的统一接口：
    用于对 Agent 生成的非标准格式文件进行降级评分。
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

def extract_all_strings(obj):
    """
    深度优先遍历 JSON 所有的数值与字符串叶子节点，返回扁平化字符串列表。
    用于在结构未知的情况下，严格进行确定性检索。
    """
    res = []
    if isinstance(obj, dict):
        for v in obj.values():
            res.extend(extract_all_strings(v))
    elif isinstance(obj, list):
        for item in obj:
            res.extend(extract_all_strings(item))
    elif isinstance(obj, str):
        res.append(obj)
    elif isinstance(obj, (int, float)):
        res.append(str(obj))
    return res

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."

    total_score = 0
    details = []

    def add_detail(item, score, max_score, passed, reason):
        nonlocal total_score
        total_score += score
        details.append({
            "item": item,
            "score": score,
            "max_score": max_score,
            "passed": passed,
            "reason": reason
        })

    deliverables_path = os.path.join(workspace, "deliverables")
    missing_waivers_path = os.path.join(deliverables_path, "missing_waivers.json")
    fixed_route_path = os.path.join(deliverables_path, "fixed_route.json")

    # 1. 结构与格式探针 (15分)
    if os.path.isdir(deliverables_path):
        add_detail("目录结构检查: deliverables", 5, 5, True, "成功创建了 deliverables 目录")
    else:
        add_detail("目录结构检查: deliverables", 0, 5, False, "未能找到 deliverables 目录")

    missing_data = None
    if os.path.isfile(missing_waivers_path):
        try:
            with open(missing_waivers_path, "r", encoding="utf-8") as f:
                missing_data = json.load(f)
            add_detail("文件格式检查: missing_waivers", 5, 5, True, "文件存在且为完全合法的 JSON")
        except Exception as e:
            add_detail("文件格式检查: missing_waivers", 0, 5, False, f"JSON 解析失败或存在额外文本: {e}")
    else:
        add_detail("文件格式检查: missing_waivers", 0, 5, False, "未找到 missing_waivers.json 文件")

    fixed_data = None
    if os.path.isfile(fixed_route_path):
        try:
            with open(fixed_route_path, "r", encoding="utf-8") as f:
                fixed_data = json.load(f)
            add_detail("文件格式检查: fixed_route", 5, 5, True, "文件存在且为完全合法的 JSON")
        except Exception as e:
            add_detail("文件格式检查: fixed_route", 0, 5, False, f"JSON 解析失败或存在额外文本: {e}")
    else:
        add_detail("文件格式检查: fixed_route", 0, 5, False, "未找到 fixed_route.json 文件")

    # 2. missing_waivers 内容确定性解析与严格排他校验 (40分)
    if missing_data is not None:
        all_strs = extract_all_strings(missing_data)
        all_text = " ".join(all_strs)
        
        # 验证缺失对象1
        if "T-8803" in all_text or "Michael Brown" in all_text:
            add_detail("数据分析: 识别 T-8803", 15, 15, True, "成功识别出缺失的 T-8803 游客")
        else:
            add_detail("数据分析: 识别 T-8803", 0, 15, False, "未能识别出缺失的 T-8803 游客")
            
        # 验证缺失对象2
        if "T-8806" in all_text or "Sarah Miller" in all_text:
            add_detail("数据分析: 识别 T-8806", 15, 15, True, "成功识别出缺失的 T-8806 游客")
        else:
            add_detail("数据分析: 识别 T-8806", 0, 15, False, "未能识别出缺失的 T-8806 游客")
            
        # 防幻觉/防作弊验证
        has_others = False
        forbidden_list = ["T-8801", "T-8802", "T-8804", "T-8805", "John Smith", "Alice Johnson", "Emily Davis", "David Wilson"]
        for other in forbidden_list:
            if other in all_text:
                has_others = True
                break
        if not has_others:
            add_detail("数据分析: 严厉剔除防伪", 10, 10, True, "完美剔除了已签名人员，无冗余/幻觉数据")
        else:
            add_detail("数据分析: 严厉剔除防伪", 0, 10, False, "一票否决：名单内混入了已经签名的游客或存在错误幻觉数据")
    else:
        # LLM 语义降级判定：如果写成了非规范的文本文件
        if os.path.isfile(missing_waivers_path):
            with open(missing_waivers_path, "r", encoding="utf-8") as f:
                content = f.read()
            prompt = "Does the text explicitly mention that T-8803 (Michael Brown) and T-8806 (Sarah Miller) are missing waivers, and strictly NO ONE ELSE?"
            if llm_judge_content(prompt, content):
                add_detail("数据分析(LLM降级): 缺失名单", 20, 40, False, "JSON解析失败，但大模型判定文本内提取了正确的人员名单（降级得分）")
            else:
                add_detail("数据分析(LLM降级): 缺失名单", 0, 40, False, "非JSON格式且大模型判定内容存在逻辑错误或人员遗漏")
        else:
            add_detail("数据分析: 缺失名单探针组", 0, 40, False, "文件不存在，全盘扣除")

    # 3. fixed_route 经纬度对调精确验证与幻觉检查 (45分)
    if fixed_data is not None:
        if isinstance(fixed_data, list):
            # 数量验证
            if len(fixed_data) == 4:
                add_detail("空间校对: 节点完整度", 10, 10, True, "未丢弃或捏造地标，精确保持4个坐标节点")
            else:
                add_detail("空间校对: 节点完整度", 0, 10, False, f"发生了严重幻觉或遗漏，包含 {len(fixed_data)} 个地标，必须且只能是 4 个")
                
            # 精度验证
            correct_coords = 0
            for item in fixed_data:
                if isinstance(item, dict):
                    lat = item.get("lat", item.get("latitude"))
                    lon = item.get("lon", item.get("longitude"))
                    # The original was lat: ~(-82), lon: ~(39)
                    # Correct should be lat: ~(39), lon: ~(-82)
                    if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
                        if 39.0 <= float(lat) <= 40.0 and -83.0 <= float(lon) <= -82.0:
                            correct_coords += 1
            
            if correct_coords == 4:
                add_detail("空间校对: 经纬数据严查", 35, 35, True, "所有地标的纬度(lat)和经度(lon)均正确地调换成了北美坐标")
            else:
                score_per_item = int(35 / 4)
                add_detail("空间校对: 经纬数据严查", correct_coords * score_per_item, 35, False, f"部分数据修正失败。正确纠正了 {correct_coords}/4 个地标，或 JSON 字典键值命名丢失")
        else:
            add_detail("空间校对: 结构严查", 0, 45, False, "JSON 根节点非列表，结构彻底崩溃")
    else:
        # LLM 语义降级判定
        if os.path.isfile(fixed_route_path):
            with open(fixed_route_path, "r", encoding="utf-8") as f:
                content = f.read()
            prompt = "Read the landmarks. Does EVERY landmark now have a positive latitude (around 39) and negative longitude (around -82)?"
            if llm_judge_content(prompt, content):
                add_detail("空间校对(LLM降级): 经纬互换", 15, 45, False, "JSON解析失败，大模型判定文本内含有近似正确的互换逻辑描述（降级得分）")
            else:
                add_detail("空间校对(LLM降级): 经纬互换", 0, 45, False, "非JSON且大模型未能检测出经纬度的正确修正")
        else:
            add_detail("空间校对: 探针组", 0, 45, False, "文件不存在，全盘扣除")

    # 4. 生成报告
    result = {
        "total_score": int(total_score),
        "details": details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
