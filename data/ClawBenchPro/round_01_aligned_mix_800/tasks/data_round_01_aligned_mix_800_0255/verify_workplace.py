import os
import sys
import json
import httpx
from openai import OpenAI

# 🔒 强制 API 规范
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

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    report_dir = os.path.join(workspace, "green_report")
    report_file = os.path.join(report_dir, "report.json") # 假设文件名为 report.json，如果 Agent 命名不同，下方逻辑会捕获

    # 1. 目录与文件基础检查 (10分)
    if os.path.exists(report_dir) and os.path.isdir(report_dir):
        score += 5
        details.append({"item": "检查结果目录是否存在", "score": 5, "max_score": 5, "passed": True, "reason": "目录 green_report 存在"})
        
        # 寻找目录下任何 json 文件
        json_files = [f for f in os.listdir(report_dir) if f.endswith('.json')]
        if json_files:
            report_file = os.path.join(report_dir, json_files[0])
            score += 5
            details.append({"item": "检查 JSON 报告文件是否存在", "score": 5, "max_score": 5, "passed": True, "reason": f"找到报告文件: {json_files[0]}"})
        else:
            details.append({"item": "检查 JSON 报告文件是否存在", "score": 0, "max_score": 5, "passed": False, "reason": "未找到 JSON 文件"})
    else:
        details.append({"item": "检查结果目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "目录 green_report 不存在"})

    # 2. 结构化数据解析与关键数值计算 (60分)
    # 计算逻辑参考：
    # Monday: 2 (WoodSpecs), 1 (Junk), 1 (OceanPlastics), 5 (Junk) -> WoodSpecs:2, OceanPlastics:1, Junk:6
    # Wednesday: LeafFrames:4, WoodSpecs:3, EcoGaze:2, Junk(CheapoPlastics):2
    # Friday(OCR): WoodSpecs:2, Junk(Luxottica):10
    # TOTAL APPROVED: WoodSpecs: 7 (2+3+2), OceanPlastics Co.: 1, LeafFrames: 4, EcoGaze: 2
    # TOTAL UNAPPROVED (Junk): 1 (Monday) + 5 (Monday) + 2 (Wednesday) + 10 (Friday) = 18
    
    expected_approved = {
        "WoodSpecs": 7,
        "OceanPlastics Co.": 1,
        "LeafFrames": 4,
        "EcoGaze": 2
    }
    expected_unapproved_total = 18

    if os.path.exists(report_file):
        try:
            with open(report_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # A. 检查官方品牌统计是否准确 (40分)
            brand_scores = 0
            for brand, count in expected_approved.items():
                # 兼容大小写和空格
                found_val = next((v for k, v in data.items() if k.lower().replace(" ", "") == brand.lower().replace(" ", "")), None)
                if found_val == count:
                    brand_scores += 10
            
            score += brand_scores
            details.append({"item": "官方品牌(WoodSpecs/Ocean/Leaf/Eco)统计准确性", "score": brand_scores, "max_score": 40, "passed": brand_scores == 40, "reason": f"匹配分值: {brand_scores}/40"})

            # B. 检查未授权/垃圾数据统计 (20分)
            unapproved_keys = ["unapproved", "junk", "unapproved_count", "others", "others_count"]
            actual_unapproved = None
            for key in unapproved_keys:
                if key in data:
                    actual_unapproved = data[key]
                    break
            
            if actual_unapproved == expected_unapproved_total:
                score += 20
                details.append({"item": "未授权品牌(Unapproved Junk)统计准确性", "score": 20, "max_score": 20, "passed": True, "reason": "垃圾数据统计正确 (18)"})
            else:
                details.append({"item": "未授权品牌(Unapproved Junk)统计准确性", "score": 0, "max_score": 20, "passed": False, "reason": f"垃圾数据统计错误，期望 18，实际得到 {actual_unapproved}"})

        except Exception as e:
            details.append({"item": "JSON 解析合法性", "score": 0, "max_score": 60, "passed": False, "reason": f"JSON 解析失败: {str(e)}"})

    # 3. LLM 语义检查报告完整性 (30分)
    if os.path.exists(report_file):
        with open(report_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否包含关键的业务实体或进行了必要的说明 (防止只给数字没说明)
        is_professional = llm_judge_content(
            "Check if this JSON report contains a clear summary of recycling counts. Does it distinguish between official brands and unapproved items as requested by Dr. Miller?", 
            content
        )
        if is_professional:
            score += 30
            details.append({"item": "报告业务语义完整性检查", "score": 30, "max_score": 30, "passed": True, "reason": "LLM 判定报告符合业务逻辑且区分了品牌类别"})
        else:
            details.append({"item": "报告业务语义完整性检查", "score": 0, "max_score": 30, "passed": False, "reason": "LLM 判定报告内容缺失或不符合业务场景"})

    # 写入最终得分
    result = {
        "total_score": int(score),
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
