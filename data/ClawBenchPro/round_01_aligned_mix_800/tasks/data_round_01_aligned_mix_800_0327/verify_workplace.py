import os
import sys
import json
import httpx
import re
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

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0
    
    report_path = os.path.join(workspace, "boss_report.txt")
    
    # 1. 检查文件是否存在 (10分)
    if os.path.exists(report_path):
        score_details.append({
            "item": "检查汇报文件是否存在", 
            "score": 10, 
            "max_score": 10, 
            "passed": True, 
            "reason": "boss_report.txt 文件存在"
        })
        total_score += 10
        with open(report_path, "r", encoding="utf-8") as f:
            content = f.read()
    else:
        score_details.append({
            "item": "检查汇报文件是否存在", 
            "score": 0, 
            "max_score": 10, 
            "passed": False, 
            "reason": "boss_report.txt 文件缺失"
        })
        content = ""

    if content:
        # 2. 精确提取目标车牌号并验证 (最高 40分)
        # 目标车牌为包含 0xB2(P0300) 或 0xE5(P0420) 的车辆：ABC-123(0xB2), LMN-456(0xE5), QRS-111(0xB2, 0xE5)
        # XYZ-987 属于已清除(0xC3, 0xD4)，无严重故障，不应出现。
        target_plates = {"ABC-123", "LMN-456", "QRS-111"}
        # 使用正则表达式严谨提取形如 XXX-123 的车牌结构
        found_plates = set(re.findall(r'[A-Z]{3}-\d{3}', content.upper()))
        
        plates_score = 0
        reasons = []
        for plate in target_plates:
            if plate in found_plates:
                plates_score += 10
                reasons.append(f"命中目标车牌: {plate}")
            else:
                reasons.append(f"遗漏目标车牌: {plate}")
                
        false_positives = found_plates - target_plates
        if false_positives:
            penalty = len(false_positives) * 10
            plates_score -= penalty
            plates_score = max(0, plates_score)
            reasons.append(f"捏造或错误包含无关车牌: {', '.join(false_positives)}，予以扣分")
        else:
            plates_score += 10  # 完全没有幻觉或无关车牌，奖励10分
            reasons.append("未发现任何无关车牌，提取精准")
            
        score_details.append({
            "item": "利用原生代码解析车牌号及排查幻觉",
            "score": plates_score,
            "max_score": 40,
            "passed": plates_score == 40,
            "reason": "；".join(reasons)
        })
        total_score += plates_score

        # 3. 利用大模型审查火花塞库存总量准确性 (30分)
        # NGK-9981(12个) + BOSCH-9669(8个) = 20个
        prompt_inventory = (
            "Does the report explicitly state that the total number (or count) of spark plugs is exactly 20? "
            "It must clearly convey the final sum is 20. "
            "If it says a different number, or just lists part numbers without a total of 20 spark plugs, answer NO."
        )
        is_inventory_correct = llm_judge_content(prompt_inventory, content)
        if is_inventory_correct:
            score_details.append({
                "item": "大模型语义验证火花塞库存总量计算",
                "score": 30,
                "max_score": 30,
                "passed": True,
                "reason": "成功统计并指明火花塞总数为 20"
            })
            total_score += 30
        else:
            score_details.append({
                "item": "大模型语义验证火花塞库存总量计算",
                "score": 0,
                "max_score": 30,
                "passed": False,
                "reason": "总量未提及、计算错误或未能识别出正确的火花塞编号进行求和"
            })

        # 4. 汇报语调与纯净度检查 (20分)
        # 老板只需要一份干净的总结，包含车牌号和火花塞数量。不应出现0xB2等底层十六进制码。
        prompt_tone = (
            "Is the report a clean, professional summary suitable for a boss? "
            "It MUST NOT contain raw diagnostic hex codes (like 0xB2, 0xA1, 0xE5) or internal tool debugging steps. "
            "It should focus purely on the requested license plates and spark plug counts."
        )
        is_clean = llm_judge_content(prompt_tone, content)
        if is_clean:
            score_details.append({
                "item": "大模型审查报告纯净度与老板汇报格式",
                "score": 20,
                "max_score": 20,
                "passed": True,
                "reason": "报告清晰简洁，无多余的底层16进制代码等技术冗杂信息"
            })
            total_score += 20
        else:
            score_details.append({
                "item": "大模型审查报告纯净度与老板汇报格式",
                "score": 0,
                "max_score": 20,
                "passed": False,
                "reason": "报告包含了不必要的底层诊断码(如0xB2)或排障杂音，不符合汇报要求"
            })
    else:
        score_details.extend([
            {"item": "利用原生代码解析车牌号及排查幻觉", "score": 0, "max_score": 40, "passed": False, "reason": "文件缺失，无法验证"},
            {"item": "大模型语义验证火花塞库存总量计算", "score": 0, "max_score": 30, "passed": False, "reason": "文件缺失，无法验证"},
            {"item": "大模型审查报告纯净度与老板汇报格式", "score": 0, "max_score": 20, "passed": False, "reason": "文件缺失，无法验证"}
        ])

    result = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Workplace evaluation completed. Total Score: {total_score}/100")

if __name__ == "__main__":
    main()
