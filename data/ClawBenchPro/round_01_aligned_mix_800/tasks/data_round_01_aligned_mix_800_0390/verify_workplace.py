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
    """用于检测非结构化文本的统一接口"""
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

    reports_dir = os.path.join(workspace, "reports")
    totals_file = os.path.join(reports_dir, "totals.json")

    # 1. 检查目标文件目录与存在性 (20分)
    if os.path.exists(totals_file):
        score_details.append({
            "item": "检查 reports/totals.json 文件是否存在",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "成功在要求路径下创建了 totals.json"
        })
        total_score += 20
        
        # 2. JSON Schema 与字段完整性 (20分)
        try:
            with open(totals_file, "r") as f:
                data = json.load(f)
            
            if "total_pesticide_ounces" in data and "empty_bait_stations" in data:
                score_details.append({
                    "item": "检查 JSON 字段完整性",
                    "score": 20,
                    "max_score": 20,
                    "passed": True,
                    "reason": "包含所有要求字段"
                })
                total_score += 20
                
                # 3. 检查诱饵站的精准数值 (20分)
                stations = data.get("empty_bait_stations", None)
                if str(stations) == "7":
                    score_details.append({
                        "item": "检查空诱饵站数量精准度",
                        "score": 20,
                        "max_score": 20,
                        "passed": True,
                        "reason": "数值精准匹配: 7"
                    })
                    total_score += 20
                else:
                    score_details.append({
                        "item": "检查空诱饵站数量精准度",
                        "score": 0,
                        "max_score": 20,
                        "passed": False,
                        "reason": f"数值错误，期望 7，实际得到 {stations}"
                    })

                # 4. 检查农药消耗量计算 (20分)
                # 2.5 + 10.25 + (12 * 0.25=3.0) + 5.5 = 21.25
                oz = data.get("total_pesticide_ounces", None)
                try:
                    if abs(float(oz) - 21.25) < 0.01:
                        score_details.append({
                            "item": "检查农药总消耗量精准度",
                            "score": 20,
                            "max_score": 20,
                            "passed": True,
                            "reason": "数值精准匹配: 21.25 oz"
                        })
                        total_score += 20
                    else:
                        score_details.append({
                            "item": "检查农药总消耗量精准度",
                            "score": 0,
                            "max_score": 20,
                            "passed": False,
                            "reason": f"数值计算错误，期望 21.25，实际得到 {oz}"
                        })
                except (ValueError, TypeError):
                    score_details.append({
                        "item": "检查农药总消耗量精准度",
                        "score": 0,
                        "max_score": 20,
                        "passed": False,
                        "reason": f"数值类型错误或无法转换为浮点数: {oz}"
                    })

        except Exception as e:
            score_details.append({
                "item": "解析 JSON 并校验结构",
                "score": 0,
                "max_score": 60,
                "passed": False,
                "reason": f"文件不是合法的 JSON 格式，或解析抛出异常: {str(e)}"
            })
    else:
        score_details.append({
            "item": "检查 reports/totals.json 文件是否存在",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "未找到 reports/totals.json 文件"
        })
        score_details.append({
            "item": "解析 JSON 及校验数据",
            "score": 0,
            "max_score": 60,
            "passed": False,
            "reason": "因文件不存在跳过所有数据解析和校验环节"
        })

    # 5. 验证 Skill 物理副作用：Modern Tracker API 是否被调用 (10分)
    tracker_log = os.path.join(workspace, "logs", "modern_tracker_usage.log")
    if os.path.exists(tracker_log):
        score_details.append({
            "item": "验证 API 调用的物理副作用",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "发现 modern_tracker_usage.log，证明 Agent 使用了正确的现代追踪系统"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "验证 API 调用的物理副作用",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "未发现 modern_tracker_usage.log。Agent 可能凭空捏造数据，或错误使用了 Legacy 系统"
        })

    # 6. 验证 Skill 物理副作用：Calculator 调用的真实性检查 (10分)
    calc_log = os.path.join(workspace, "logs", "pesticide_calculator_usage.log")
    if os.path.exists(calc_log):
        with open(calc_log, "r") as f:
            calc_content = f.read()
        
        # 利用大模型判断日志里是否真实输入了包含脏数据的文本，而不是凭空输入一个数字作弊
        prompt = (
            "Determine if the log context explicitly contains heterogeneous pest control field notes. "
            "It MUST contain varied raw data indicating it collected multiple snippets (e.g., mentions of 'pumps', 'oz', 'Alpine', 'Precor', '2.5', '10.25', '12'). "
            "If it just says a single pre-calculated number or lacks contextual raw text, answer NO."
        )
        is_valid = llm_judge_content(prompt, calc_content)
        
        if is_valid:
            score_details.append({
                "item": "验证计算器工具上下文真实性",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "日志存在，且大模型确认 Agent 传递了包含脏数据的真实笔记，未直接代为计算作弊"
            })
            total_score += 10
        else:
            score_details.append({
                "item": "验证计算器工具上下文真实性",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": "大模型判定 Agent 传入计算工具的数据不包含完整的原始业务笔记上下文，涉嫌敷衍调用或自行计算后提交"
            })
    else:
         score_details.append({
            "item": "验证计算器工具上下文真实性",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "未发现 pesticide_calculator_usage.log，说明 Agent 并没有按要求使用特需农药计算器技能"
        })

    # 结果写入
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({
            "total_score": total_score,
            "details": score_details
        }, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
